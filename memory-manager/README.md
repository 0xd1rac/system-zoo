# Custom Memory Allocator

This project implements a custom memory allocator with both heap and stack allocation strategies. It provides a hands-on understanding of memory management concepts and implementation details.

## Features

### Heap Allocator
- Custom implementation of malloc, free, and realloc
- Block splitting and coalescing
- Free list management
- Memory alignment
- Fragmentation handling
- Thread safety with mutex locks
- Memory protection (read, write, execute)
- Memory usage statistics and monitoring

### Stack Allocator
- Simple linear allocation strategy
- Push/pop behavior
- Fixed-size memory pool
- Fast allocation and deallocation
- Thread safety with mutex locks
- Memory usage statistics and monitoring

## Building the Project

```bash
mkdir build
cd build
cmake ..
make
```

## Running the Tests

```bash
./memory_manager_test
```

## Implementation Details

### Heap Allocator
The heap allocator uses a linked list of memory blocks, where each block contains:
- Size information
- Allocation status
- Memory protection flags
- Corruption detection magic number
- Pointer to next block
- User data

Key features:
1. First-fit allocation strategy
2. Block splitting for efficient memory usage
3. Coalescing of adjacent free blocks
4. 8-byte memory alignment
5. Thread safety with mutex locks
6. Memory protection with mprotect
7. Memory corruption detection
8. Comprehensive memory usage statistics

### Stack Allocator
The stack allocator provides:
1. Linear allocation with a moving pointer
2. Simple push/pop behavior
3. Fast allocation (O(1))
4. Limited to freeing only the most recently allocated block
5. Thread safety with mutex locks
6. Memory usage statistics

## Memory Layout

Each allocated block in the heap allocator has the following layout:
```
+----------------+----------------+----------------+
| Block Header   | User Data      | Next Block    |
| (size, flags,  | (variable)     | (if any)      |
|  protection,   |                |               |
|  magic)        |                |               |
+----------------+----------------+----------------+
```

## Memory Protection

The memory manager supports setting different protection levels for allocated memory:
- Read-only memory
- Write-only memory
- Execute-only memory
- Read-write memory (default)
- Read-execute memory
- Write-execute memory
- Read-write-execute memory

Example:
```c
// Protect memory as read-only
memory_manager_protect(manager, ptr, size, MEMORY_PROTECT_READ);

// Check if memory is read-only
if (memory_manager_is_protected(manager, ptr, MEMORY_PROTECT_READ)) {
    // Memory is read-only
}
```

## Memory Statistics

The memory manager tracks various statistics about memory usage:
- Total memory allocated
- Total memory freed
- Current memory usage
- Peak memory usage
- Number of allocations
- Number of frees
- Number of failed allocations
- Fragmentation percentage

Example:
```c
// Get memory statistics
MemoryStats stats = memory_manager_get_stats(manager);

// Print memory statistics
memory_manager_print_stats(manager);

// Reset memory statistics
memory_manager_reset_stats(manager);
```

## Thread Safety

Both allocators are thread-safe, using mutex locks to protect critical sections:
- All allocation operations
- All deallocation operations
- Memory protection changes
- Statistics updates

This allows multiple threads to safely allocate and free memory without data races.

## Usage Example

```c
// Initialize memory manager
MemoryManager* manager = memory_manager_init(1024 * 1024);  // 1MB pool

// Allocate memory
void* ptr = memory_manager_malloc(manager, 100);

// Use memory
strcpy(ptr, "Hello, World!");

// Protect memory as read-only
memory_manager_protect(manager, ptr, 100, MEMORY_PROTECT_READ);

// Print memory statistics
memory_manager_print_stats(manager);

// Free memory
memory_manager_free(manager, ptr);

// Cleanup
memory_manager_destroy(manager);
```

## Limitations

1. Fixed pool size (no dynamic growth)
2. Memory protection requires page alignment on some systems
3. Simple first-fit strategy (could be improved with best-fit)

## Future Improvements

1. Support for dynamic pool growth
2. Implement best-fit allocation
3. Add memory leak detection
4. Add more advanced corruption detection
5. Add memory pooling for small allocations
6. Add support for different alignment requirements 