#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <fcntl.h>
#include "shell.h"

// Built-in commands
static int handle_exit(char** args) {
    return 0;
}

static int handle_jobs(shell_state_t* state) {
    pthread_mutex_lock(&state->job_mutex);
    
    job_t* current = state->jobs->head;
    while (current) {
        printf("[%d] %s %s\n", 
            current->job_id,
            current->status == JOB_RUNNING ? "Running" : 
            current->status == JOB_STOPPED ? "Stopped" : "Done",
            current->command);
        current = current->next;
    }
    
    pthread_mutex_unlock(&state->job_mutex);
    return 1;
}

static int handle_fg(shell_state_t* state, char** args) {
    if (!args[1]) {
        fprintf(stderr, "fg: job ID required\n");
        return 1;
    }
    
    int job_id = atoi(args[1]);
    pthread_mutex_lock(&state->job_mutex);
    
    job_t* job = find_job_by_id(state->jobs, job_id);
    if (!job) {
        fprintf(stderr, "fg: job %d not found\n", job_id);
        pthread_mutex_unlock(&state->job_mutex);
        return 1;
    }
    
    if (job->status == JOB_STOPPED) {
        kill(job->pid, SIGCONT);
    }
    
    pthread_mutex_unlock(&state->job_mutex);
    
    int status;
    waitpid(job->pid, &status, 0);
    return 1;
}

static int handle_bg(shell_state_t* state, char** args) {
    if (!args[1]) {
        fprintf(stderr, "bg: job ID required\n");
        return 1;
    }
    
    int job_id = atoi(args[1]);
    pthread_mutex_lock(&state->job_mutex);
    
    job_t* job = find_job_by_id(state->jobs, job_id);
    if (!job) {
        fprintf(stderr, "bg: job %d not found\n", job_id);
        pthread_mutex_unlock(&state->job_mutex);
        return 1;
    }
    
    if (job->status == JOB_STOPPED) {
        kill(job->pid, SIGCONT);
        job->status = JOB_RUNNING;
    }
    
    pthread_mutex_unlock(&state->job_mutex);
    return 1;
}

// Command execution
static int execute_command(shell_state_t* state, char** args, bool background) {
    if (!args[0]) return 1;
    
    // Handle built-in commands
    if (strcmp(args[0], "exit") == 0) {
        state->running = 0;
        return handle_exit(args);
    }
    if (strcmp(args[0], "jobs") == 0) {
        return handle_jobs(state);
    }
    if (strcmp(args[0], "fg") == 0) {
        return handle_fg(state, args);
    }
    if (strcmp(args[0], "bg") == 0) {
        return handle_bg(state, args);
    }
    
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }
    
    if (pid == 0) {
        // Child process
        if (execvp(args[0], args) == -1) {
            perror("execvp");
            exit(1);
        }
    } else {
        // Parent process
        if (!background) {
            int status;
            waitpid(pid, &status, 0);
        } else {
            pthread_mutex_lock(&state->job_mutex);
            add_job(state->jobs, pid, args[0]);
            printf("[%d] %d %s\n", state->jobs->count, pid, args[0]);
            pthread_mutex_unlock(&state->job_mutex);
        }
    }
    
    return 1;
}

// Parse a single command with redirection
static command_t parse_command_with_redirection(char* cmd_str) {
    command_t cmd = {0};
    cmd.in_redirect = REDIRECT_NONE;
    cmd.out_redirect = REDIRECT_NONE;
    cmd.background = false;
    cmd.arg_count = 0;
    
    char* token = strtok(cmd_str, " \t\n");
    while (token && cmd.arg_count < MAX_ARGS - 1) {
        if (strcmp(token, "<") == 0) {
            token = strtok(NULL, " \t\n");
            if (token) {
                cmd.input_file = token;
                cmd.in_redirect = REDIRECT_IN;
            }
        } else if (strcmp(token, ">") == 0) {
            token = strtok(NULL, " \t\n");
            if (token) {
                cmd.output_file = token;
                cmd.out_redirect = REDIRECT_OUT;
            }
        } else if (strcmp(token, ">>") == 0) {
            token = strtok(NULL, " \t\n");
            if (token) {
                cmd.output_file = token;
                cmd.out_redirect = REDIRECT_APPEND;
            }
        } else if (strcmp(token, "&") == 0) {
            cmd.background = true;
        } else {
            cmd.args[cmd.arg_count++] = token;
        }
        token = strtok(NULL, " \t\n");
    }
    
    cmd.args[cmd.arg_count] = NULL;
    return cmd;
}

// Parse a pipeline from a command line
pipeline_t* parse_pipeline(char* line) {
    pipeline_t* pipeline = malloc(sizeof(pipeline_t));
    if (!pipeline) return NULL;
    
    pipeline->command_count = 0;
    pipeline->background = false;
    
    // Check for background execution
    char* line_copy = strdup(line);
    if (!line_copy) {
        free(pipeline);
        return NULL;
    }
    
    char* last_token = strrchr(line_copy, '&');
    if (last_token && *(last_token + 1) == '\0') {
        pipeline->background = true;
        *last_token = '\0';
    }
    
    // Split by pipe
    char* cmd_str = strtok(line_copy, "|");
    while (cmd_str && pipeline->command_count < MAX_PIPES) {
        // Trim whitespace
        while (*cmd_str == ' ' || *cmd_str == '\t') cmd_str++;
        
        char* end = cmd_str + strlen(cmd_str) - 1;
        while (end > cmd_str && (*end == ' ' || *end == '\t' || *end == '\n')) {
            *end = '\0';
            end--;
        }
        
        pipeline->commands[pipeline->command_count++] = parse_command_with_redirection(cmd_str);
        cmd_str = strtok(NULL, "|");
    }
    
    free(line_copy);
    return pipeline;
}

// Free a pipeline structure
void free_pipeline(pipeline_t* pipeline) {
    if (!pipeline) return;
    free(pipeline);
}

// Set up redirection for a command
void setup_redirection(command_t* cmd) {
    if (cmd->in_redirect == REDIRECT_IN && cmd->input_file) {
        int fd = open(cmd->input_file, O_RDONLY);
        if (fd < 0) {
            perror("open input file");
            exit(1);
        }
        dup2(fd, STDIN_FILENO);
        close(fd);
    }
    
    if (cmd->out_redirect == REDIRECT_OUT && cmd->output_file) {
        int fd = open(cmd->output_file, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            perror("open output file");
            exit(1);
        }
        dup2(fd, STDOUT_FILENO);
        close(fd);
    }
    
    if (cmd->out_redirect == REDIRECT_APPEND && cmd->output_file) {
        int fd = open(cmd->output_file, O_WRONLY | O_CREAT | O_APPEND, 0644);
        if (fd < 0) {
            perror("open output file (append)");
            exit(1);
        }
        dup2(fd, STDOUT_FILENO);
        close(fd);
    }
}

// Close pipe file descriptors
void close_pipe_fds(int pipe_fds[][2], int count) {
    for (int i = 0; i < count; i++) {
        close(pipe_fds[i][0]);
        close(pipe_fds[i][1]);
    }
}

// Execute a pipeline of commands
int execute_pipeline(shell_state_t* state, pipeline_t* pipeline) {
    if (!pipeline || pipeline->command_count == 0) return 1;
    
    // Handle built-in commands for single commands
    if (pipeline->command_count == 1) {
        command_t* cmd = &pipeline->commands[0];
        if (cmd->arg_count == 0) return 1;
        
        if (strcmp(cmd->args[0], "exit") == 0) {
            state->running = 0;
            return handle_exit(cmd->args);
        }
        if (strcmp(cmd->args[0], "jobs") == 0) {
            return handle_jobs(state);
        }
        if (strcmp(cmd->args[0], "fg") == 0) {
            return handle_fg(state, cmd->args);
        }
        if (strcmp(cmd->args[0], "bg") == 0) {
            return handle_bg(state, cmd->args);
        }
    }
    
    // Create pipes for the pipeline
    int pipe_fds[MAX_PIPES][2];
    for (int i = 0; i < pipeline->command_count - 1; i++) {
        if (pipe(pipe_fds[i]) < 0) {
            perror("pipe");
            return 1;
        }
    }
    
    // Execute each command in the pipeline
    pid_t pids[MAX_PIPES];
    for (int i = 0; i < pipeline->command_count; i++) {
        command_t* cmd = &pipeline->commands[i];
        
        pids[i] = fork();
        if (pids[i] < 0) {
            perror("fork");
            close_pipe_fds(pipe_fds, pipeline->command_count - 1);
            return 1;
        }
        
        if (pids[i] == 0) {
            // Child process
            
            // Set up pipes
            if (i > 0) {
                // Not the first command, read from previous pipe
                dup2(pipe_fds[i-1][0], STDIN_FILENO);
                close(pipe_fds[i-1][1]);
            }
            
            if (i < pipeline->command_count - 1) {
                // Not the last command, write to next pipe
                dup2(pipe_fds[i][1], STDOUT_FILENO);
                close(pipe_fds[i][0]);
            }
            
            // Close all other pipe fds
            for (int j = 0; j < pipeline->command_count - 1; j++) {
                if (j != i && j != i-1) {
                    close(pipe_fds[j][0]);
                    close(pipe_fds[j][1]);
                }
            }
            
            // Set up redirection
            setup_redirection(cmd);
            
            // Execute the command
            if (execvp(cmd->args[0], cmd->args) == -1) {
                perror("execvp");
                exit(1);
            }
        }
    }
    
    // Parent process
    // Close all pipe fds
    close_pipe_fds(pipe_fds, pipeline->command_count - 1);
    
    // Wait for all children to finish if not in background
    if (!pipeline->background) {
        for (int i = 0; i < pipeline->command_count; i++) {
            int status;
            waitpid(pids[i], &status, 0);
        }
    } else {
        // Add the last process to the job list
        pthread_mutex_lock(&state->job_mutex);
        add_job(state->jobs, pids[pipeline->command_count - 1], 
                pipeline->commands[pipeline->command_count - 1].args[0]);
        printf("[%d] %d %s\n", state->jobs->count, 
               pids[pipeline->command_count - 1], 
               pipeline->commands[pipeline->command_count - 1].args[0]);
        pthread_mutex_unlock(&state->job_mutex);
    }
    
    return 1;
}

// Command parsing
static char** parse_command(char* line, bool* background) {
    char** args = malloc(MAX_ARGS * sizeof(char*));
    if (!args) return NULL;
    
    int i = 0;
    char* token = strtok(line, " \t\n");
    
    while (token && i < MAX_ARGS - 1) {
        args[i++] = token;
        token = strtok(NULL, " \t\n");
    }
    
    if (i > 0 && strcmp(args[i-1], "&") == 0) {
        *background = true;
        args[--i] = NULL;
    } else {
        *background = false;
        args[i] = NULL;
    }
    
    return args;
}

void* input_handler(void* arg) {
    shell_state_t* state = (shell_state_t*)arg;
    char line[MAX_COMMAND_LENGTH];
    
    while (state->running) {
        printf("shell> ");
        fflush(stdout);
        
        if (!fgets(line, MAX_COMMAND_LENGTH, stdin)) {
            break;
        }
        
        // Check for pipeline or redirection
        if (strchr(line, '|') || strchr(line, '<') || strchr(line, '>')) {
            pipeline_t* pipeline = parse_pipeline(line);
            if (pipeline) {
                execute_pipeline(state, pipeline);
                free_pipeline(pipeline);
            }
        } else {
            bool background;
            char** args = parse_command(line, &background);
            if (!args) continue;
            
            if (args[0]) {
                execute_command(state, args, background);
            }
            
            free(args);
        }
    }
    
    return NULL;
} 