#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include "namespace.h"

int get_namespace_flags(container_config_t *config) {
    int flags = 0;
    
    if (config->pid_ns) flags |= NS_PID;
    if (config->net_ns) flags |= NS_NET;
    if (config->ipc_ns) flags |= NS_IPC;
    if (config->uts_ns) flags |= NS_UTS;
    if (config->mnt_ns) flags |= NS_MNT;
    if (config->user_ns) flags |= NS_USER;
    
    return flags;
}

bool is_namespace_supported(int ns_type) {
    char path[256];
    snprintf(path, sizeof(path), "/proc/self/ns/%d", ns_type);
    return access(path, F_OK) != -1;
}

int setup_namespaces(container_config_t *config) {
    // Check if namespaces are supported
    if (config->pid_ns && !is_namespace_supported(NS_PID)) {
        fprintf(stderr, "PID namespace not supported\n");
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    if (config->net_ns && !is_namespace_supported(NS_NET)) {
        fprintf(stderr, "Network namespace not supported\n");
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    if (config->ipc_ns && !is_namespace_supported(NS_IPC)) {
        fprintf(stderr, "IPC namespace not supported\n");
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    if (config->uts_ns && !is_namespace_supported(NS_UTS)) {
        fprintf(stderr, "UTS namespace not supported\n");
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    if (config->mnt_ns && !is_namespace_supported(NS_MNT)) {
        fprintf(stderr, "Mount namespace not supported\n");
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    if (config->user_ns && !is_namespace_supported(NS_USER)) {
        fprintf(stderr, "User namespace not supported\n");
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    return CONTAINER_SUCCESS;
}

int cleanup_namespaces(pid_t pid) {
    if (pid <= 0) {
        return CONTAINER_ERROR_NAMESPACE;
    }
    
    // Namespaces are automatically cleaned up when the process exits
    return CONTAINER_SUCCESS;
} 