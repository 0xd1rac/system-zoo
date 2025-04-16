#include "thread_pool.h"
#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

// This is a classic producer-consumer pattern where threads are producers and consumers of tasks
// 1. Producer threads add tasks to the queue (at the tail)
// 2. Consumer threads remove tasks from the queue (from the head)
// 3. Mutex is used to synchronize access to the queue
// 4. The condition variable (cond) allows threads to wait efficiently when there are no tasks
// 5. The stop flag is used to tell threads when to shut down
struct thread_pool {
    pthread_t *threads; // Array of thread handles (pthread_t) that represent the worker threads in the pool
    int num_threads; // Number of worker threads in the pool
    task_queue_t task_queue; // The task queue for this thread pool
    bool stop; // A boolean flag to tell threads when to shut down
};

// Worker thread function that consumes tasks from the queue
static void *worker(void *args) {
    thread_pool_t *pool = (thread_pool_t *)args; //pointer to the thread pool
    
    while (true) {
        // Get a task from the queue (this will block if the queue is empty)
        task_t *task = task_queue_pop(&pool->task_queue);
        
        // If we got a NULL task and the queue is shut down, we're done
        if (!task && pool->stop) {
            break;
        }
        
        // Execute the task if we got one
        if (task) {
            task->function(task->args);
            free(task);
        }
    }
    
    return NULL;
}

thread_pool_t *thread_pool_create(int num_threads) {
    thread_pool_t *pool = (thread_pool_t *)malloc(sizeof(thread_pool_t));
    if (!pool) {
        fprintf(stderr, "Failed to allocate memory for thread pool\n");
        return NULL;
    }
    
    pool->num_threads = num_threads;
    pool->threads = malloc(sizeof(pthread_t) * num_threads);
    if (!pool->threads) {
        fprintf(stderr, "Failed to allocate memory for threads\n");
        free(pool);
        return NULL;
    }
    
    pool->stop = false;
    
    // Initialize the task queue
    task_queue_init(&pool->task_queue);
    
    // Create worker threads
    for (int i = 0; i < num_threads; i++) {
        if (pthread_create(&pool->threads[i], NULL, worker, (void *)pool) != 0) {
            fprintf(stderr, "Failed to create thread %d\n", i);
            thread_pool_destroy(pool);
            return NULL;
        }
    }
    
    return pool;
}

int thread_pool_submit(thread_pool_t *pool, task_fn function, void *args) {
    if (!pool || !function) {
        return -1;
    }
    
    // Add the task to the queue
    task_queue_push(&pool->task_queue, (void (*)(void *))function, args);
    
    return 0;
}

void thread_pool_destroy(thread_pool_t *pool) {
    if (!pool) {
        return;
    }
    
    // Signal all threads to stop
    pool->stop = true;
    task_queue_shutdown(&pool->task_queue);
    
    // Wait for all threads to finish
    for (int i = 0; i < pool->num_threads; i++) {
        pthread_join(pool->threads[i], NULL);
    }
    
    // Clean up resources
    task_queue_destroy(&pool->task_queue);
    free(pool->threads);
    free(pool);
}


