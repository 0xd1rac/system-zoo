#ifndef CONTAINER_H
#define CONTAINER_H

#include <stdbool.h>
#include <sys/types.h>

// Container configuration structure
typedef struct {
    char *name;           // Container name
    char *rootfs;         // Root filesystem path
    char *command;        // Command to run inside container
    char **args;          // Command arguments
    size_t num_args;      // Number of arguments
    
    // Resource limits
    unsigned long memory_limit;  // Memory limit in bytes
    unsigned long cpu_limit;     // CPU limit in percentage
    
    // Namespace flags
    bool pid_ns;          // PID namespace
    bool net_ns;          // Network namespace
    bool ipc_ns;          // IPC namespace
    bool uts_ns;          // UTS namespace
    bool mnt_ns;          // Mount namespace
    bool user_ns;         // User namespace
} container_config_t;

// Container structure
typedef struct {
    container_config_t config;
    pid_t pid;            // Container process ID
    int status;           // Container status
    char *cgroup_path;    // Cgroup path
} container_t;

// Container management functions
container_t* container_create(container_config_t *config);
int container_start(container_t *container);
int container_stop(container_t *container);
int container_destroy(container_t *container);
int container_status(container_t *container);

// Error codes
#define CONTAINER_SUCCESS 0
#define CONTAINER_ERROR_NAMESPACE 1
#define CONTAINER_ERROR_CGROUP 2
#define CONTAINER_ERROR_FILESYSTEM 3
#define CONTAINER_ERROR_PROCESS 4

#endif // CONTAINER_H 