#ifndef TASK_H
#define TASK_H

// Defines a function pointer type for tasks
typedef void (*task_fn)(void* args);

// Defines a task structure
typedef struct task {
    task_fn function;  // Function to execute
    void *args;        // Arguments to pass to the function
    struct task *next; // Pointer to the next task in the queue
} task_t;

#endif // TASK_H 