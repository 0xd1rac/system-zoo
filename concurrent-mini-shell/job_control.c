#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include "shell.h"

job_list_t* create_job_list(void) {
    job_list_t* list = malloc(sizeof(job_list_t));
    if (!list) return NULL;
    
    list->head = NULL;
    list->count = 0;
    return list;
}

void cleanup_job_list(job_list_t* list) {
    if (!list) return;
    
    job_t* current = list->head;
    while (current) {
        job_t* next = current->next;
        free(current);
        current = next;
    }
    free(list);
}

void add_job(job_list_t* list, pid_t pid, const char* command) {
    if (!list || !command) return;
    
    job_t* new_job = malloc(sizeof(job_t));
    if (!new_job) return;
    
    new_job->pid = pid;
    new_job->job_id = list->count + 1;
    strncpy(new_job->command, command, MAX_COMMAND_LENGTH - 1);
    new_job->command[MAX_COMMAND_LENGTH - 1] = '\0';
    new_job->status = JOB_RUNNING;
    new_job->next = list->head;
    
    list->head = new_job;
    list->count++;
}

void remove_job(job_list_t* list, pid_t pid) {
    if (!list) return;
    
    job_t* current = list->head;
    job_t* prev = NULL;
    
    while (current) {
        if (current->pid == pid) {
            if (prev) {
                prev->next = current->next;
            } else {
                list->head = current->next;
            }
            free(current);
            list->count--;
            return;
        }
        prev = current;
        current = current->next;
    }
}

job_t* find_job_by_pid(job_list_t* list, pid_t pid) {
    if (!list) return NULL;
    
    job_t* current = list->head;
    while (current) {
        if (current->pid == pid) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

job_t* find_job_by_id(job_list_t* list, int job_id) {
    if (!list) return NULL;
    
    job_t* current = list->head;
    while (current) {
        if (current->job_id == job_id) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

void update_job_status(shell_state_t* state, pid_t pid, int status) {
    if (!state || !state->jobs) return;
    
    pthread_mutex_lock(&state->job_mutex);
    
    job_t* job = find_job_by_pid(state->jobs, pid);
    if (job) {
        if (WIFSTOPPED(status)) {
            job->status = JOB_STOPPED;
        } else if (WIFEXITED(status) || WIFSIGNALED(status)) {
            job->status = JOB_DONE;
            printf("[%d] Done: %s\n", job->job_id, job->command);
            remove_job(state->jobs, pid);
        }
    }
    
    pthread_mutex_unlock(&state->job_mutex);
}

void* job_monitor(void* arg) {
    shell_state_t* state = (shell_state_t*)arg;
    
    while (state->running) {
        pthread_mutex_lock(&state->job_mutex);
        
        job_t* current = state->jobs->head;
        while (current) {
            pid_t pid = current->pid;
            int status;
            
            if (waitpid(pid, &status, WNOHANG) > 0) {
                update_job_status(state, pid, status);
            }
            current = current->next;
        }
        
        pthread_mutex_unlock(&state->job_mutex);
        usleep(100000); // Sleep for 100ms
    }
    
    return NULL;
} 