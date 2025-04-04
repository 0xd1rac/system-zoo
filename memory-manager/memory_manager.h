#ifndef MEMORY_MANAGER_H
#define MEMORY_MANAGER_H

#include <stddef.h>
#include <stdint.h>
#include <pthread.h>

// Memory protection flags
#define MEMORY_PROTECT_NONE  0x00
#define MEMORY_PROTECT_READ  0x01
#define MEMORY_PROTECT_WRITE 0x02
#define MEMORY_PROTECT_EXEC  0x04
#define MEMORY_PROTECT_ALL   0x07

// Memory usage statistics
typedef struct {
    size_t total_allocated;      // Total memory allocated
    size_t total_freed;          // Total memory freed
    size_t current_usage;        // Current memory in use
    size_t peak_usage;           // Peak memory usage
    size_t allocation_count;     // Number of allocations
    size_t free_count;           // Number of frees
    size_t failed_allocations;   // Number of failed allocations
    size_t fragmentation;        // Estimated fragmentation percentage
} MemoryStats;

// Block header structure to store metadata about each memory block
typedef struct BlockHeader {
    size_t size;          // Size of the block (including header)
    uint8_t is_free;      // Flag indicating if block is free (1) or allocated (0)
    uint8_t protection;   // Memory protection flags
    uint32_t magic;       // Magic number for corruption detection
    struct BlockHeader* next;  // Pointer to next block in the list
} BlockHeader;

// Memory manager structure
typedef struct {
    void* memory_pool;    // Pointer to the allocated memory pool
    size_t pool_size;     // Total size of the memory pool
    BlockHeader* free_list;  // Pointer to the first free block
    pthread_mutex_t mutex;   // Mutex for thread safety
    MemoryStats stats;       // Memory usage statistics
    uint32_t magic;          // Magic number for corruption detection
} MemoryManager;

// Core memory management functions
MemoryManager* memory_manager_init(size_t pool_size);
void* memory_manager_malloc(MemoryManager* manager, size_t size);
void memory_manager_free(MemoryManager* manager, void* ptr);
void* memory_manager_realloc(MemoryManager* manager, void* ptr, size_t new_size);
void memory_manager_destroy(MemoryManager* manager);

// Memory protection functions
int memory_manager_protect(MemoryManager* manager, void* ptr, size_t size, uint8_t protection);
int memory_manager_is_protected(MemoryManager* manager, void* ptr, uint8_t protection);

// Memory statistics functions
MemoryStats memory_manager_get_stats(MemoryManager* manager);
void memory_manager_reset_stats(MemoryManager* manager);
void memory_manager_print_stats(MemoryManager* manager);

// Optional stack allocator functions
typedef struct {
    void* memory_pool;
    size_t pool_size;
    size_t current_offset;
    pthread_mutex_t mutex;   // Mutex for thread safety
    MemoryStats stats;       // Memory usage statistics
    uint32_t magic;          // Magic number for corruption detection
} StackAllocator;

StackAllocator* stack_allocator_init(size_t pool_size);
void* stack_allocator_allocate(StackAllocator* allocator, size_t size);
void stack_allocator_free(StackAllocator* allocator, void* ptr);
void stack_allocator_destroy(StackAllocator* allocator);

// Stack allocator statistics
MemoryStats stack_allocator_get_stats(StackAllocator* allocator);
void stack_allocator_reset_stats(StackAllocator* allocator);
void stack_allocator_print_stats(StackAllocator* allocator);

#endif // MEMORY_MANAGER_H 