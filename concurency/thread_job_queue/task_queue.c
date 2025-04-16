#include "task_queue.h"
#include <stdlib.h>
#include <stdio.h>

void task_queue_init(task_queue_t *q) {
    q->head = q->tail = NULL;
    q->is_shutdown = false;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
}

void task_queue_push(task_queue_t *q, task_fn function, void *args) {
    task_t *task = malloc(sizeof(task_t));
    if (!task) {
        fprintf(stderr, "Failed to allocate memory for task\n");
        return;
    }
    
    task->function = function;
    task->args = args;
    task->next = NULL;
    
    pthread_mutex_lock(&q->lock);
    
    if (q->tail) {
        q->tail->next = task;
    } else {
        q->head = task;
    }
    q->tail = task;
    
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
}

task_t *task_queue_pop(task_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    
    while (!q->head && !q->is_shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    
    if (q->is_shutdown && !q->head) {
        pthread_mutex_unlock(&q->lock);
        return NULL;
    }
    
    task_t *task = q->head;
    if (task) {
        q->head = task->next;
        if (!q->head) {
            q->tail = NULL;
        }
    }
    
    pthread_mutex_unlock(&q->lock);
    return task;
}

void task_queue_shutdown(task_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    q->is_shutdown = true;
    pthread_cond_broadcast(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
}

void task_queue_destroy(task_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    
    // Free all remaining tasks
    task_t *current = q->head;
    while (current) {
        task_t *next = current->next;
        free(current);
        current = next;
    }
    
    q->head = q->tail = NULL;
    
    pthread_mutex_unlock(&q->lock);
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
}


