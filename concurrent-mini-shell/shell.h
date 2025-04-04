#ifndef SHELL_H
#define SHELL_H

#include <pthread.h>
#include <stdbool.h>
#include <fcntl.h>

#define MAX_COMMAND_LENGTH 1024
#define MAX_ARGS 64
#define MAX_JOBS 100
#define MAX_PIPES 10

// Job status
typedef enum {
    JOB_RUNNING,
    JOB_STOPPED,
    JOB_DONE
} job_status_t;

// Redirection types
typedef enum {
    REDIRECT_NONE,
    REDIRECT_IN,
    REDIRECT_OUT,
    REDIRECT_APPEND
} redirect_type_t;

// Command structure for parsing
typedef struct {
    char* args[MAX_ARGS];
    int arg_count;
    char* input_file;
    char* output_file;
    redirect_type_t in_redirect;
    redirect_type_t out_redirect;
    bool background;
} command_t;

// Pipeline structure
typedef struct {
    command_t commands[MAX_PIPES];
    int command_count;
    bool background;
} pipeline_t;

// Job structure
typedef struct job {
    pid_t pid;
    int job_id;
    char command[MAX_COMMAND_LENGTH];
    job_status_t status;
    struct job* next;
} job_t;

// Job list structure
typedef struct {
    job_t* head;
    int count;
} job_list_t;

// Shell state structure
typedef struct {
    job_list_t* jobs;
    int job_count;
    pthread_mutex_t job_mutex;
    bool running;
} shell_state_t;

// Function declarations
void update_job_status(shell_state_t* state, pid_t pid, int status);
job_list_t* create_job_list(void);
void cleanup_job_list(job_list_t* list);
void add_job(job_list_t* list, pid_t pid, const char* command);
void remove_job(job_list_t* list, pid_t pid);
job_t* find_job_by_pid(job_list_t* list, pid_t pid);
job_t* find_job_by_id(job_list_t* list, int job_id);

// Pipeline and redirection functions
pipeline_t* parse_pipeline(char* line);
void free_pipeline(pipeline_t* pipeline);
int execute_pipeline(shell_state_t* state, pipeline_t* pipeline);
void setup_redirection(command_t* cmd);
void close_pipe_fds(int pipe_fds[][2], int count);

#endif // SHELL_H 