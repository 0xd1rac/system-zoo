#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <errno.h>
#include "container.h"
#include "namespace.h"
#include "cgroup.h"
#include "filesystem.h"

// Stack size for clone
#define STACK_SIZE (1024 * 1024)

// Container process entry point
static int container_process(void *arg) {
    container_config_t *config = (container_config_t *)arg;
    
    // Setup root filesystem
    if (setup_rootfs(NULL) != FS_SUCCESS) {
        fprintf(stderr, "Failed to setup root filesystem\n");
        return CONTAINER_ERROR_FILESYSTEM;
    }
    
    // Execute the command
    if (execvp(config->command, config->args) == -1) {
        fprintf(stderr, "Failed to execute command: %s\n", strerror(errno));
        return CONTAINER_ERROR_PROCESS;
    }
    
    return CONTAINER_SUCCESS;
}

container_t* container_create(container_config_t *config) {
    container_t *container = malloc(sizeof(container_t));
    if (!container) {
        return NULL;
    }
    
    // Copy configuration
    memcpy(&container->config, config, sizeof(container_config_t));
    container->pid = 0;
    container->status = 0;
    container->cgroup_path = NULL;
    
    return container;
}

int container_start(container_t *container) {
    // Allocate stack for clone
    void *stack = malloc(STACK_SIZE);
    if (!stack) {
        return CONTAINER_ERROR_PROCESS;
    }
    
    // Get namespace flags
    int flags = get_namespace_flags(&container->config);
    
    // Clone the process
    container->pid = clone(container_process, stack + STACK_SIZE,
                         flags | SIGCHLD, &container->config);
    
    if (container->pid == -1) {
        free(stack);
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    // Setup cgroups
    if (setup_cgroup(container) != CGROUP_SUCCESS) {
        kill(container->pid, SIGKILL);
        free(stack);
        return CONTAINER_ERROR_CGROUP;
    }
    
    free(stack);
    return CONTAINER_SUCCESS;
}

int container_stop(container_t *container) {
    if (container->pid > 0) {
        kill(container->pid, SIGTERM);
        waitpid(container->pid, &container->status, 0);
    }
    return CONTAINER_SUCCESS;
}

int container_destroy(container_t *container) {
    // Stop the container if it's running
    container_stop(container);
    
    // Cleanup resources
    cleanup_cgroup(container);
    cleanup_namespaces(container->pid);
    cleanup_rootfs(container);
    
    // Free container resources
    free(container->cgroup_path);
    free(container);
    
    return CONTAINER_SUCCESS;
}

int container_status(container_t *container) {
    if (container->pid <= 0) {
        return -1;
    }
    
    int status;
    pid_t result = waitpid(container->pid, &status, WNOHANG);
    
    if (result == 0) {
        return 1; // Container is running
    } else if (result == container->pid) {
        return 0; // Container has exited
    }
    
    return -1; // Error checking status
} 