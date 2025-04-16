#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "thread_pool.h"

// Example task function
void print_task(void* arg) {
    int task_id = *(int*)arg;
    printf("Task %d executed by thread %lu\n", task_id, (unsigned long)pthread_self());
    free(arg); // Free the argument
    usleep(100000); // Sleep for 100ms to simulate work
}

int main() {
    // Create a thread pool with 4 worker threads
    thread_pool_t* pool = thread_pool_create(4);
    if (!pool) {
        fprintf(stderr, "Failed to create thread pool\n");
        return 1;
    }
    
    printf("Thread pool created with 4 worker threads\n");
    
    // Submit 10 tasks to the thread pool
    for (int i = 0; i < 10; i++) {
        int* task_id = malloc(sizeof(int));
        if (!task_id) {
            fprintf(stderr, "Failed to allocate memory for task ID\n");
            continue;
        }
        *task_id = i;
        
        if (thread_pool_submit(pool, print_task, task_id) != 0) {
            fprintf(stderr, "Failed to submit task %d\n", i);
            free(task_id);
        } else {
            printf("Task %d submitted to thread pool\n", i);
        }
        
        usleep(50000); // Sleep for 50ms between submissions
    }
    
    printf("All tasks submitted, waiting for completion...\n");
    sleep(2); // Give some time for tasks to complete
    
    // Destroy the thread pool
    thread_pool_destroy(pool);
    printf("Thread pool destroyed\n");
    
    return 0;
}
