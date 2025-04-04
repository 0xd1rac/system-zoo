#include "memory_manager.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
#include <errno.h>

// Magic number for corruption detection
#define MAGIC_NUMBER 0xDEADBEEF

// Helper function to align memory addresses
static size_t align_size(size_t size) {
    const size_t alignment = 8;  // 8-byte alignment
    return (size + alignment - 1) & ~(alignment - 1);
}

// Helper function to get the header from a memory block
static BlockHeader* get_block_header(void* ptr) {
    return (BlockHeader*)((char*)ptr - sizeof(BlockHeader));
}

// Helper function to get the data pointer from a header
static void* get_block_data(BlockHeader* header) {
    return (void*)((char*)header + sizeof(BlockHeader));
}

// Helper function to check if a block is corrupted
static int is_block_corrupted(BlockHeader* header) {
    return header->magic != MAGIC_NUMBER;
}

// Helper function to update memory statistics
static void update_stats(MemoryStats* stats, size_t allocated, size_t freed, int success) {
    if (success) {
        stats->total_allocated += allocated;
        stats->current_usage += allocated - freed;
        stats->allocation_count++;
        
        if (stats->current_usage > stats->peak_usage) {
            stats->peak_usage = stats->current_usage;
        }
    } else {
        stats->failed_allocations++;
    }
    
    if (freed > 0) {
        stats->total_freed += freed;
        stats->free_count++;
    }
    
    // Calculate fragmentation (simplified)
    if (stats->total_allocated > 0) {
        stats->fragmentation = (stats->total_allocated - stats->current_usage) * 100 / stats->total_allocated;
    }
}

// Helper function to set memory protection
static int set_memory_protection(void* ptr, size_t size, uint8_t protection) {
    int prot = 0;
    if (protection & MEMORY_PROTECT_READ) prot |= PROT_READ;
    if (protection & MEMORY_PROTECT_WRITE) prot |= PROT_WRITE;
    if (protection & MEMORY_PROTECT_EXEC) prot |= PROT_EXEC;
    
    if (mprotect(ptr, size, prot) == -1) {
        return 0;  // Failed to set protection
    }
    return 1;  // Success
}

MemoryManager* memory_manager_init(size_t pool_size) {
    // Align pool size
    pool_size = align_size(pool_size);
    
    // Allocate memory for the manager structure
    MemoryManager* manager = (MemoryManager*)malloc(sizeof(MemoryManager));
    if (!manager) return NULL;
    
    // Initialize mutex
    if (pthread_mutex_init(&manager->mutex, NULL) != 0) {
        free(manager);
        return NULL;
    }
    
    // Allocate the memory pool with read/write protection initially
    manager->memory_pool = mmap(NULL, pool_size, PROT_READ | PROT_WRITE, 
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (manager->memory_pool == MAP_FAILED) {
        pthread_mutex_destroy(&manager->mutex);
        free(manager);
        return NULL;
    }
    
    // Initialize the first block header
    BlockHeader* first_block = (BlockHeader*)manager->memory_pool;
    first_block->size = pool_size;
    first_block->is_free = 1;
    first_block->next = NULL;
    first_block->protection = MEMORY_PROTECT_READ | MEMORY_PROTECT_WRITE;
    first_block->magic = MAGIC_NUMBER;
    
    manager->pool_size = pool_size;
    manager->free_list = first_block;
    manager->magic = MAGIC_NUMBER;
    
    // Initialize statistics
    memset(&manager->stats, 0, sizeof(MemoryStats));
    
    return manager;
}

void* memory_manager_malloc(MemoryManager* manager, size_t size) {
    if (!manager || size == 0) return NULL;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    // Align the requested size
    size = align_size(size);
    
    // Search for a suitable block using first-fit strategy
    BlockHeader* current = manager->free_list;
    BlockHeader* prev = NULL;
    
    while (current) {
        if (current->is_free && current->size >= size + sizeof(BlockHeader)) {
            // Found a suitable block
            if (current->size > size + sizeof(BlockHeader) + 8) {  // Minimum block size check
                // Split the block
                BlockHeader* new_block = (BlockHeader*)((char*)current + sizeof(BlockHeader) + size);
                new_block->size = current->size - size - sizeof(BlockHeader);
                new_block->is_free = 1;
                new_block->next = current->next;
                new_block->protection = MEMORY_PROTECT_READ | MEMORY_PROTECT_WRITE;
                new_block->magic = MAGIC_NUMBER;
                
                current->size = size + sizeof(BlockHeader);
                current->next = new_block;
            }
            
            // Mark the block as allocated
            current->is_free = 0;
            
            // Update free list
            if (prev) {
                prev->next = current->next;
            } else {
                manager->free_list = current->next;
            }
            
            // Update statistics
            update_stats(&manager->stats, size, 0, 1);
            
            // Unlock the mutex
            pthread_mutex_unlock(&manager->mutex);
            
            return get_block_data(current);
        }
        
        prev = current;
        current = current->next;
    }
    
    // Update statistics for failed allocation
    update_stats(&manager->stats, 0, 0, 0);
    
    // Unlock the mutex
    pthread_mutex_unlock(&manager->mutex);
    
    return NULL;  // No suitable block found
}

void memory_manager_free(MemoryManager* manager, void* ptr) {
    if (!manager || !ptr) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    BlockHeader* header = get_block_header(ptr);
    
    // Check for corruption
    if (is_block_corrupted(header)) {
        fprintf(stderr, "Memory corruption detected in block at %p\n", ptr);
        pthread_mutex_unlock(&manager->mutex);
        return;
    }
    
    if (header->is_free) {
        pthread_mutex_unlock(&manager->mutex);
        return;  // Already free
    }
    
    // Update statistics
    update_stats(&manager->stats, 0, header->size - sizeof(BlockHeader), 1);
    
    // Mark as free
    header->is_free = 1;
    
    // Add to free list
    header->next = manager->free_list;
    manager->free_list = header;
    
    // Try to coalesce with next block
    BlockHeader* next_block = (BlockHeader*)((char*)header + header->size);
    if ((char*)next_block < (char*)manager->memory_pool + manager->pool_size &&
        next_block->is_free) {
        header->size += next_block->size;
        header->next = next_block->next;
    }
    
    // Try to coalesce with previous block
    BlockHeader* current = manager->free_list;
    while (current && current->next != header) {
        current = current->next;
    }
    
    if (current && (char*)current + current->size == (char*)header) {
        current->size += header->size;
        current->next = header->next;
    }
    
    // Unlock the mutex
    pthread_mutex_unlock(&manager->mutex);
}

void* memory_manager_realloc(MemoryManager* manager, void* ptr, size_t new_size) {
    if (!manager || !ptr) return memory_manager_malloc(manager, new_size);
    if (new_size == 0) {
        memory_manager_free(manager, ptr);
        return NULL;
    }
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    BlockHeader* header = get_block_header(ptr);
    
    // Check for corruption
    if (is_block_corrupted(header)) {
        fprintf(stderr, "Memory corruption detected in block at %p\n", ptr);
        pthread_mutex_unlock(&manager->mutex);
        return NULL;
    }
    
    if (header->size >= new_size + sizeof(BlockHeader)) {
        // Current block is large enough
        pthread_mutex_unlock(&manager->mutex);
        return ptr;
    }
    
    // Unlock the mutex before allocating new block
    pthread_mutex_unlock(&manager->mutex);
    
    // Allocate new block and copy data
    void* new_ptr = memory_manager_malloc(manager, new_size);
    if (!new_ptr) return NULL;
    
    // Lock the mutex again for copying data
    pthread_mutex_lock(&manager->mutex);
    
    memcpy(new_ptr, ptr, header->size - sizeof(BlockHeader));
    
    // Unlock the mutex before freeing old block
    pthread_mutex_unlock(&manager->mutex);
    
    memory_manager_free(manager, ptr);
    
    return new_ptr;
}

int memory_manager_protect(MemoryManager* manager, void* ptr, size_t size, uint8_t protection) {
    if (!manager || !ptr) return 0;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    BlockHeader* header = get_block_header(ptr);
    
    // Check for corruption
    if (is_block_corrupted(header)) {
        fprintf(stderr, "Memory corruption detected in block at %p\n", ptr);
        pthread_mutex_unlock(&manager->mutex);
        return 0;
    }
    
    // Set the protection flags in the header
    header->protection = protection;
    
    // Set the actual memory protection
    int result = set_memory_protection(ptr, size, protection);
    
    // Unlock the mutex
    pthread_mutex_unlock(&manager->mutex);
    
    return result;
}

int memory_manager_is_protected(MemoryManager* manager, void* ptr, uint8_t protection) {
    if (!manager || !ptr) return 0;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    BlockHeader* header = get_block_header(ptr);
    
    // Check for corruption
    if (is_block_corrupted(header)) {
        fprintf(stderr, "Memory corruption detected in block at %p\n", ptr);
        pthread_mutex_unlock(&manager->mutex);
        return 0;
    }
    
    // Check if the requested protection is set
    int result = (header->protection & protection) == protection;
    
    // Unlock the mutex
    pthread_mutex_unlock(&manager->mutex);
    
    return result;
}

MemoryStats memory_manager_get_stats(MemoryManager* manager) {
    MemoryStats stats = {0};
    
    if (!manager) return stats;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    // Copy the stats
    stats = manager->stats;
    
    // Unlock the mutex
    pthread_mutex_unlock(&manager->mutex);
    
    return stats;
}

void memory_manager_reset_stats(MemoryManager* manager) {
    if (!manager) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    // Reset the stats
    memset(&manager->stats, 0, sizeof(MemoryStats));
    
    // Unlock the mutex
    pthread_mutex_unlock(&manager->mutex);
}

void memory_manager_print_stats(MemoryManager* manager) {
    if (!manager) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    // Get the stats
    MemoryStats stats = manager->stats;
    
    // Unlock the mutex
    pthread_mutex_unlock(&manager->mutex);
    
    // Print the stats
    printf("Memory Manager Statistics:\n");
    printf("  Total Allocated: %zu bytes\n", stats.total_allocated);
    printf("  Total Freed: %zu bytes\n", stats.total_freed);
    printf("  Current Usage: %zu bytes\n", stats.current_usage);
    printf("  Peak Usage: %zu bytes\n", stats.peak_usage);
    printf("  Allocation Count: %zu\n", stats.allocation_count);
    printf("  Free Count: %zu\n", stats.free_count);
    printf("  Failed Allocations: %zu\n", stats.failed_allocations);
    printf("  Fragmentation: %zu%%\n", stats.fragmentation);
}

void memory_manager_destroy(MemoryManager* manager) {
    if (!manager) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&manager->mutex);
    
    // Unmap the memory pool
    munmap(manager->memory_pool, manager->pool_size);
    
    // Destroy the mutex
    pthread_mutex_unlock(&manager->mutex);
    pthread_mutex_destroy(&manager->mutex);
    
    // Free the manager structure
    free(manager);
}

// Stack Allocator Implementation
StackAllocator* stack_allocator_init(size_t pool_size) {
    pool_size = align_size(pool_size);
    
    StackAllocator* allocator = (StackAllocator*)malloc(sizeof(StackAllocator));
    if (!allocator) return NULL;
    
    // Initialize mutex
    if (pthread_mutex_init(&allocator->mutex, NULL) != 0) {
        free(allocator);
        return NULL;
    }
    
    // Allocate the memory pool with read/write protection initially
    allocator->memory_pool = mmap(NULL, pool_size, PROT_READ | PROT_WRITE, 
                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (allocator->memory_pool == MAP_FAILED) {
        pthread_mutex_destroy(&allocator->mutex);
        free(allocator);
        return NULL;
    }
    
    allocator->pool_size = pool_size;
    allocator->current_offset = 0;
    allocator->magic = MAGIC_NUMBER;
    
    // Initialize statistics
    memset(&allocator->stats, 0, sizeof(MemoryStats));
    
    return allocator;
}

void* stack_allocator_allocate(StackAllocator* allocator, size_t size) {
    if (!allocator || size == 0) return NULL;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&allocator->mutex);
    
    size = align_size(size);
    
    if (allocator->current_offset + size > allocator->pool_size) {
        // Update statistics for failed allocation
        update_stats(&allocator->stats, 0, 0, 0);
        
        // Unlock the mutex
        pthread_mutex_unlock(&allocator->mutex);
        
        return NULL;  // Out of memory
    }
    
    void* ptr = (char*)allocator->memory_pool + allocator->current_offset;
    allocator->current_offset += size;
    
    // Update statistics
    update_stats(&allocator->stats, size, 0, 1);
    
    // Unlock the mutex
    pthread_mutex_unlock(&allocator->mutex);
    
    return ptr;
}

void stack_allocator_free(StackAllocator* allocator, void* ptr) {
    // In a stack allocator, we can only free the most recently allocated block
    if (!allocator || !ptr) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&allocator->mutex);
    
    if (ptr == (char*)allocator->memory_pool + allocator->current_offset - 8) {
        // Update statistics
        update_stats(&allocator->stats, 0, 8, 1);
        
        allocator->current_offset -= 8;  // Assuming minimum block size of 8 bytes
    }
    
    // Unlock the mutex
    pthread_mutex_unlock(&allocator->mutex);
}

MemoryStats stack_allocator_get_stats(StackAllocator* allocator) {
    MemoryStats stats = {0};
    
    if (!allocator) return stats;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&allocator->mutex);
    
    // Copy the stats
    stats = allocator->stats;
    
    // Unlock the mutex
    pthread_mutex_unlock(&allocator->mutex);
    
    return stats;
}

void stack_allocator_reset_stats(StackAllocator* allocator) {
    if (!allocator) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&allocator->mutex);
    
    // Reset the stats
    memset(&allocator->stats, 0, sizeof(MemoryStats));
    
    // Unlock the mutex
    pthread_mutex_unlock(&allocator->mutex);
}

void stack_allocator_print_stats(StackAllocator* allocator) {
    if (!allocator) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&allocator->mutex);
    
    // Get the stats
    MemoryStats stats = allocator->stats;
    
    // Unlock the mutex
    pthread_mutex_unlock(&allocator->mutex);
    
    // Print the stats
    printf("Stack Allocator Statistics:\n");
    printf("  Total Allocated: %zu bytes\n", stats.total_allocated);
    printf("  Total Freed: %zu bytes\n", stats.total_freed);
    printf("  Current Usage: %zu bytes\n", stats.current_usage);
    printf("  Peak Usage: %zu bytes\n", stats.peak_usage);
    printf("  Allocation Count: %zu\n", stats.allocation_count);
    printf("  Free Count: %zu\n", stats.free_count);
    printf("  Failed Allocations: %zu\n", stats.failed_allocations);
    printf("  Fragmentation: %zu%%\n", stats.fragmentation);
}

void stack_allocator_destroy(StackAllocator* allocator) {
    if (!allocator) return;
    
    // Lock the mutex for thread safety
    pthread_mutex_lock(&allocator->mutex);
    
    // Unmap the memory pool
    munmap(allocator->memory_pool, allocator->pool_size);
    
    // Destroy the mutex
    pthread_mutex_unlock(&allocator->mutex);
    pthread_mutex_destroy(&allocator->mutex);
    
    // Free the allocator structure
    free(allocator);
} 