#ifndef CGROUP_H
#define CGROUP_H

#include <stdbool.h>
#include "container.h"

// Cgroup paths
#define CGROUP_ROOT "/sys/fs/cgroup"
#define CGROUP_MEMORY CGROUP_ROOT "/memory"
#define CGROUP_CPU CGROUP_ROOT "/cpu"

// Cgroup management functions
int setup_cgroup(container_t *container);
int cleanup_cgroup(container_t *container);

// Resource limit functions
int set_memory_limit(container_t *container, unsigned long limit);
int set_cpu_limit(container_t *container, unsigned long limit);

// Monitoring functions
int get_memory_usage(container_t *container, unsigned long *usage);
int get_cpu_usage(container_t *container, unsigned long *usage);

// Error codes
#define CGROUP_SUCCESS 0
#define CGROUP_ERROR_CREATE 1
#define CGROUP_ERROR_LIMIT 2
#define CGROUP_ERROR_MONITOR 3

#endif // CGROUP_H 