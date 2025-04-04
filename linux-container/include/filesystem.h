#ifndef FILESYSTEM_H
#define FILESYSTEM_H

#include <stdbool.h>
#include "container.h"

// Filesystem management functions
int setup_rootfs(container_t *container);
int cleanup_rootfs(container_t *container);

// Mount operations
int mount_proc(void);
int mount_dev(void);
int mount_sys(void);

// Filesystem isolation functions
int pivot_root(const char *new_root, const char *put_old);
int change_root(const char *new_root);

// Error codes
#define FS_SUCCESS 0
#define FS_ERROR_MOUNT 1
#define FS_ERROR_PIVOT 2
#define FS_ERROR_CHROOT 3

#endif // FILESYSTEM_H 