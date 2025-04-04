#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include "cgroup.h"

static char* create_cgroup_path(container_t *container, const char *subsystem) {
    char *path = malloc(strlen(CGROUP_ROOT) + strlen(subsystem) + strlen(container->config.name) + 3);
    if (!path) {
        return NULL;
    }
    
    sprintf(path, "%s/%s/%s", CGROUP_ROOT, subsystem, container->config.name);
    return path;
}

int setup_cgroup(container_t *container) {
    // Create memory cgroup
    char *mem_path = create_cgroup_path(container, "memory");
    if (!mem_path) {
        return CGROUP_ERROR_CREATE;
    }
    
    if (mkdir(mem_path, 0755) == -1 && errno != EEXIST) {
        free(mem_path);
        return CGROUP_ERROR_CREATE;
    }
    
    // Create CPU cgroup
    char *cpu_path = create_cgroup_path(container, "cpu");
    if (!cpu_path) {
        free(mem_path);
        return CGROUP_ERROR_CREATE;
    }
    
    if (mkdir(cpu_path, 0755) == -1 && errno != EEXIST) {
        free(mem_path);
        free(cpu_path);
        return CGROUP_ERROR_CREATE;
    }
    
    // Set memory limit
    if (set_memory_limit(container, container->config.memory_limit) != CGROUP_SUCCESS) {
        free(mem_path);
        free(cpu_path);
        return CGROUP_ERROR_LIMIT;
    }
    
    // Set CPU limit
    if (set_cpu_limit(container, container->config.cpu_limit) != CGROUP_SUCCESS) {
        free(mem_path);
        free(cpu_path);
        return CGROUP_ERROR_LIMIT;
    }
    
    // Add process to cgroups
    char task_path[256];
    snprintf(task_path, sizeof(task_path), "%s/tasks", mem_path);
    FILE *fp = fopen(task_path, "w");
    if (fp) {
        fprintf(fp, "%d", container->pid);
        fclose(fp);
    }
    
    snprintf(task_path, sizeof(task_path), "%s/tasks", cpu_path);
    fp = fopen(task_path, "w");
    if (fp) {
        fprintf(fp, "%d", container->pid);
        fclose(fp);
    }
    
    free(mem_path);
    free(cpu_path);
    return CGROUP_SUCCESS;
}

int set_memory_limit(container_t *container, unsigned long limit) {
    char *path = create_cgroup_path(container, "memory");
    if (!path) {
        return CGROUP_ERROR_LIMIT;
    }
    
    char limit_path[256];
    snprintf(limit_path, sizeof(limit_path), "%s/memory.limit_in_bytes", path);
    
    FILE *fp = fopen(limit_path, "w");
    if (!fp) {
        free(path);
        return CGROUP_ERROR_LIMIT;
    }
    
    fprintf(fp, "%lu", limit);
    fclose(fp);
    free(path);
    
    return CGROUP_SUCCESS;
}

int set_cpu_limit(container_t *container, unsigned long limit) {
    char *path = create_cgroup_path(container, "cpu");
    if (!path) {
        return CGROUP_ERROR_LIMIT;
    }
    
    char limit_path[256];
    snprintf(limit_path, sizeof(limit_path), "%s/cpu.shares", path);
    
    FILE *fp = fopen(limit_path, "w");
    if (!fp) {
        free(path);
        return CGROUP_ERROR_LIMIT;
    }
    
    fprintf(fp, "%lu", limit);
    fclose(fp);
    free(path);
    
    return CGROUP_SUCCESS;
}

int cleanup_cgroup(container_t *container) {
    char *mem_path = create_cgroup_path(container, "memory");
    char *cpu_path = create_cgroup_path(container, "cpu");
    
    if (mem_path) {
        rmdir(mem_path);
        free(mem_path);
    }
    
    if (cpu_path) {
        rmdir(cpu_path);
        free(cpu_path);
    }
    
    return CGROUP_SUCCESS;
}

int get_memory_usage(container_t *container, unsigned long *usage) {
    char *path = create_cgroup_path(container, "memory");
    if (!path) {
        return CGROUP_ERROR_MONITOR;
    }
    
    char usage_path[256];
    snprintf(usage_path, sizeof(usage_path), "%s/memory.usage_in_bytes", path);
    
    FILE *fp = fopen(usage_path, "r");
    if (!fp) {
        free(path);
        return CGROUP_ERROR_MONITOR;
    }
    
    fscanf(fp, "%lu", usage);
    fclose(fp);
    free(path);
    
    return CGROUP_SUCCESS;
}

int get_cpu_usage(container_t *container, unsigned long *usage) {
    char *path = create_cgroup_path(container, "cpu");
    if (!path) {
        return CGROUP_ERROR_MONITOR;
    }
    
    char usage_path[256];
    snprintf(usage_path, sizeof(usage_path), "%s/cpu.usage", path);
    
    FILE *fp = fopen(usage_path, "r");
    if (!fp) {
        free(path);
        return CGROUP_ERROR_MONITOR;
    }
    
    fscanf(fp, "%lu", usage);
    fclose(fp);
    free(path);
    
    return CGROUP_SUCCESS;
} 