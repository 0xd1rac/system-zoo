#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include "container.h"

void print_usage(const char *program_name) {
    printf("Usage: %s [options] command [args...]\n\n", program_name);
    printf("Options:\n");
    printf("  -h, --help                 Show this help message\n");
    printf("  -n, --name NAME            Container name\n");
    printf("  -r, --rootfs PATH          Root filesystem path\n");
    printf("  -m, --memory LIMIT         Memory limit in bytes\n");
    printf("  -c, --cpu LIMIT            CPU limit in percentage\n");
    printf("  --pid-ns                   Enable PID namespace\n");
    printf("  --net-ns                   Enable network namespace\n");
    printf("  --ipc-ns                   Enable IPC namespace\n");
    printf("  --uts-ns                   Enable UTS namespace\n");
    printf("  --mnt-ns                   Enable mount namespace\n");
    printf("  --user-ns                  Enable user namespace\n");
}

int main(int argc, char *argv[]) {
    container_config_t config = {0};
    config.name = "default";
    config.rootfs = "/";
    config.memory_limit = 1024 * 1024 * 1024;  // 1GB
    config.cpu_limit = 100;                    // 100%
    
    // Default namespace settings
    config.pid_ns = true;
    config.net_ns = true;
    config.ipc_ns = true;
    config.uts_ns = true;
    config.mnt_ns = true;
    config.user_ns = false;
    
    static struct option long_options[] = {
        {"help",     no_argument,       0, 'h'},
        {"name",     required_argument, 0, 'n'},
        {"rootfs",   required_argument, 0, 'r'},
        {"memory",   required_argument, 0, 'm'},
        {"cpu",      required_argument, 0, 'c'},
        {"pid-ns",   no_argument,       0, 0},
        {"net-ns",   no_argument,       0, 0},
        {"ipc-ns",   no_argument,       0, 0},
        {"uts-ns",   no_argument,       0, 0},
        {"mnt-ns",   no_argument,       0, 0},
        {"user-ns",  no_argument,       0, 0},
        {0, 0, 0, 0}
    };
    
    int opt;
    int option_index = 0;
    
    while ((opt = getopt_long(argc, argv, "hn:r:m:c:", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'h':
                print_usage(argv[0]);
                return 0;
            case 'n':
                config.name = optarg;
                break;
            case 'r':
                config.rootfs = optarg;
                break;
            case 'm':
                config.memory_limit = strtoul(optarg, NULL, 10);
                break;
            case 'c':
                config.cpu_limit = strtoul(optarg, NULL, 10);
                break;
            case 0:
                if (strcmp(long_options[option_index].name, "pid-ns") == 0)
                    config.pid_ns = true;
                else if (strcmp(long_options[option_index].name, "net-ns") == 0)
                    config.net_ns = true;
                else if (strcmp(long_options[option_index].name, "ipc-ns") == 0)
                    config.ipc_ns = true;
                else if (strcmp(long_options[option_index].name, "uts-ns") == 0)
                    config.uts_ns = true;
                else if (strcmp(long_options[option_index].name, "mnt-ns") == 0)
                    config.mnt_ns = true;
                else if (strcmp(long_options[option_index].name, "user-ns") == 0)
                    config.user_ns = true;
                break;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    if (optind >= argc) {
        fprintf(stderr, "Error: No command specified\n");
        print_usage(argv[0]);
        return 1;
    }
    
    // Set up command and arguments
    config.command = argv[optind];
    config.args = &argv[optind];
    config.num_args = argc - optind;
    
    // Create and start container
    container_t *container = container_create(&config);
    if (!container) {
        fprintf(stderr, "Failed to create container\n");
        return 1;
    }
    
    if (container_start(container) != CONTAINER_SUCCESS) {
        fprintf(stderr, "Failed to start container\n");
        container_destroy(container);
        return 1;
    }
    
    // Wait for container to finish
    int status;
    waitpid(container->pid, &status, 0);
    
    // Cleanup
    container_destroy(container);
    
    return WEXITSTATUS(status);
} 