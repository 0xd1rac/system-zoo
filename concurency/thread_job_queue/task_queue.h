#ifndef TASK_QUEUE_H
#define TASK_QUEUE_H

#include <pthread.h>
#include <stdbool.h>
#include "task.h"

typedef struct task_queue{
    task_t *head;
    task_t *tail;
    pthread_mutex_t lock;
    pthread_cond_t cond not_empty;
    bool is_shutdown;
} task_queue_t;


void task_queue_init(task_queue_t *q);
void task_queue_push(task_queue_t *q, task_fn function, void *args);
task_t *task_queue_pop(task_queue_t *q); //blocks if queue is empty
void task_queue_shutdown(task_queue_t *q); // wakes up all waiting threads
void task_queue_destroy(task_queue_t *q);


#endif
