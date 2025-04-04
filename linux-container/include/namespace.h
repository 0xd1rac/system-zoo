#ifndef NAMESPACE_H
#define NAMESPACE_H

#include <sched.h>
#include <stdbool.h>
#include "container.h"

// Namespace flags
#define NS_PID  CLONE_NEWPID
#define NS_NET  CLONE_NEWNET
#define NS_IPC  CLONE_NEWIPC
#define NS_UTS  CLONE_NEWUTS
#define NS_MNT  CLONE_NEWNS
#define NS_USER CLONE_NEWUSER

// Function to setup namespaces for a container
int setup_namespaces(container_config_t *config);

// Function to cleanup namespaces
int cleanup_namespaces(pid_t pid);

// Function to check if a namespace is supported
bool is_namespace_supported(int ns_type);

// Function to get namespace flags based on config
int get_namespace_flags(container_config_t *config);

#endif // NAMESPACE_H 