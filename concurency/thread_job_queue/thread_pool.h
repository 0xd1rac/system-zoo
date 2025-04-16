#ifndef THREAD_POOL_H
#define THREAD_POOL_H

#include "task_queue.h"

// Defines a thread pool structure
typedef struct thread_pool thread_pool_t;

// Defines a function pointer to a task
typedef void (*task_fn)(void* args);

// Create thread pool with `num_threads` workers 
thread_pool_t *thread_pool_create(int num_threads);

// Submit a task to the thread pool
int thread_pool_submit(thread_pool_t *pool, task_fn function, void *args);

// Destroy the thread pool and free all resources
void thread_pool_destroy(thread_pool_t *pool);

#endif 
