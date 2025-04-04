#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include "filesystem.h"

int mount_proc(void) {
    if (mount("proc", "/proc", "proc", 0, NULL) == -1) {
        if (errno != EBUSY) {
            fprintf(stderr, "Failed to mount /proc: %s\n", strerror(errno));
            return FS_ERROR_MOUNT;
        }
    }
    return FS_SUCCESS;
}

int mount_dev(void) {
    if (mount("devtmpfs", "/dev", "devtmpfs", 0, NULL) == -1) {
        if (errno != EBUSY) {
            fprintf(stderr, "Failed to mount /dev: %s\n", strerror(errno));
            return FS_ERROR_MOUNT;
        }
    }
    return FS_SUCCESS;
}

int mount_sys(void) {
    if (mount("sysfs", "/sys", "sysfs", 0, NULL) == -1) {
        if (errno != EBUSY) {
            fprintf(stderr, "Failed to mount /sys: %s\n", strerror(errno));
            return FS_ERROR_MOUNT;
        }
    }
    return FS_SUCCESS;
}

int setup_rootfs(container_t *container) {
    // Mount essential filesystems
    if (mount_proc() != FS_SUCCESS) {
        return FS_ERROR_MOUNT;
    }
    
    if (mount_dev() != FS_SUCCESS) {
        return FS_ERROR_MOUNT;
    }
    
    if (mount_sys() != FS_SUCCESS) {
        return FS_ERROR_MOUNT;
    }
    
    return FS_SUCCESS;
}

int cleanup_rootfs(container_t *container) {
    // Unmount in reverse order
    umount("/sys");
    umount("/dev");
    umount("/proc");
    
    return FS_SUCCESS;
}

int change_root(const char *new_root) {
    if (chroot(new_root) == -1) {
        fprintf(stderr, "Failed to chroot: %s\n", strerror(errno));
        return FS_ERROR_CHROOT;
    }
    
    if (chdir("/") == -1) {
        fprintf(stderr, "Failed to chdir: %s\n", strerror(errno));
        return FS_ERROR_CHROOT;
    }
    
    return FS_SUCCESS;
}

int pivot_root(const char *new_root, const char *put_old) {
    if (syscall(SYS_pivot_root, new_root, put_old) == -1) {
        fprintf(stderr, "Failed to pivot_root: %s\n", strerror(errno));
        return FS_ERROR_PIVOT;
    }
    
    if (chdir("/") == -1) {
        fprintf(stderr, "Failed to chdir: %s\n", strerror(errno));
        return FS_ERROR_PIVOT;
    }
    
    return FS_SUCCESS;
} 