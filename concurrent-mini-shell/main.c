#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>
#include <sys/wait.h>
#include "shell.h"
#include "job_control.h"
#include "input_handler.h"

// Global shell state
shell_state_t shell_state = {
    .jobs = NULL,
    .job_count = 0,
    .job_mutex = PTHREAD_MUTEX_INITIALIZER,
    .running = 1
};

// Signal handler for SIGCHLD
void sigchld_handler(int signo) {
    pid_t pid;
    int status;
    
    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        update_job_status(&shell_state, pid, status);
    }
}

// Signal handler for SIGINT
void sigint_handler(int signo) {
    printf("\n");
    fflush(stdout);
}

int main() {
    pthread_t input_thread;
    pthread_t monitor_thread;
    
    // Initialize job list
    shell_state.jobs = create_job_list();
    if (!shell_state.jobs) {
        fprintf(stderr, "Failed to initialize job list\n");
        return 1;
    }
    
    // Set up signal handlers
    struct sigaction sa_chld = {0};
    sa_chld.sa_handler = sigchld_handler;
    sigaction(SIGCHLD, &sa_chld, NULL);
    
    struct sigaction sa_int = {0};
    sa_int.sa_handler = sigint_handler;
    sigaction(SIGINT, &sa_int, NULL);
    
    // Create input handler thread
    if (pthread_create(&input_thread, NULL, input_handler, &shell_state) != 0) {
        fprintf(stderr, "Failed to create input handler thread\n");
        cleanup_job_list(shell_state.jobs);
        return 1;
    }
    
    // Create job monitor thread
    if (pthread_create(&monitor_thread, NULL, job_monitor, &shell_state) != 0) {
        fprintf(stderr, "Failed to create job monitor thread\n");
        shell_state.running = 0;
        pthread_join(input_thread, NULL);
        cleanup_job_list(shell_state.jobs);
        return 1;
    }
    
    // Wait for threads to finish
    pthread_join(input_thread, NULL);
    pthread_join(monitor_thread, NULL);
    
    // Cleanup
    cleanup_job_list(shell_state.jobs);
    pthread_mutex_destroy(&shell_state.job_mutex);
    
    return 0;
} 