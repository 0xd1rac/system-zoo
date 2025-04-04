#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include "memory_manager.h"

#define NUM_THREADS 4
#define ALLOCATIONS_PER_THREAD 100

// Thread function for heap allocator
void* heap_allocator_thread(void* arg) {
    MemoryManager* manager = (MemoryManager*)arg;
    void* ptrs[ALLOCATIONS_PER_THREAD];
    
    // Allocate memory
    for (int i = 0; i < ALLOCATIONS_PER_THREAD; i++) {
        size_t size = (rand() % 1000) + 100;  // Random size between 100 and 1100 bytes
        ptrs[i] = memory_manager_malloc(manager, size);
        
        if (ptrs[i]) {
            // Use the memory
            memset(ptrs[i], i % 256, size);
        }
        
        // Sleep a bit to simulate work
        usleep(1000);
    }
    
    // Free some memory
    for (int i = 0; i < ALLOCATIONS_PER_THREAD; i += 2) {
        if (ptrs[i]) {
            memory_manager_free(manager, ptrs[i]);
            ptrs[i] = NULL;
        }
    }
    
    // Allocate more memory
    for (int i = 0; i < ALLOCATIONS_PER_THREAD / 2; i++) {
        size_t size = (rand() % 500) + 50;  // Random size between 50 and 550 bytes
        void* ptr = memory_manager_malloc(manager, size);
        
        if (ptr) {
            // Use the memory
            memset(ptr, (i + 100) % 256, size);
        }
        
        // Sleep a bit to simulate work
        usleep(1000);
    }
    
    // Free remaining memory
    for (int i = 0; i < ALLOCATIONS_PER_THREAD; i++) {
        if (ptrs[i]) {
            memory_manager_free(manager, ptrs[i]);
        }
    }
    
    return NULL;
}

// Thread function for stack allocator
void* stack_allocator_thread(void* arg) {
    StackAllocator* allocator = (StackAllocator*)arg;
    void* ptrs[ALLOCATIONS_PER_THREAD];
    
    // Allocate memory
    for (int i = 0; i < ALLOCATIONS_PER_THREAD; i++) {
        size_t size = (rand() % 100) + 10;  // Random size between 10 and 110 bytes
        ptrs[i] = stack_allocator_allocate(allocator, size);
        
        if (ptrs[i]) {
            // Use the memory
            memset(ptrs[i], i % 256, size);
        }
        
        // Sleep a bit to simulate work
        usleep(1000);
    }
    
    // Free some memory (only the most recently allocated)
    for (int i = ALLOCATIONS_PER_THREAD - 1; i >= 0; i -= 2) {
        if (ptrs[i]) {
            stack_allocator_free(allocator, ptrs[i]);
            ptrs[i] = NULL;
        }
    }
    
    return NULL;
}

void test_heap_allocator() {
    printf("Testing Heap Allocator:\n");
    
    // Initialize memory manager with 1MB pool
    MemoryManager* manager = memory_manager_init(1024 * 1024);
    if (!manager) {
        printf("Failed to initialize memory manager\n");
        return;
    }
    
    // Test basic allocation
    void* ptr1 = memory_manager_malloc(manager, 100);
    void* ptr2 = memory_manager_malloc(manager, 200);
    void* ptr3 = memory_manager_malloc(manager, 300);
    
    if (ptr1 && ptr2 && ptr3) {
        printf("Basic allocation successful\n");
        
        // Test memory usage
        strcpy(ptr1, "Hello");
        strcpy(ptr2, "World");
        strcpy(ptr3, "Memory");
        
        printf("ptr1: %s\n", (char*)ptr1);
        printf("ptr2: %s\n", (char*)ptr2);
        printf("ptr3: %s\n", (char*)ptr3);
    }
    
    // Test memory protection
    printf("\nTesting Memory Protection:\n");
    
    // Protect ptr1 as read-only
    if (memory_manager_protect(manager, ptr1, 100, MEMORY_PROTECT_READ)) {
        printf("Memory protection set successfully\n");
        
        // Try to write to read-only memory (should fail)
        printf("Attempting to write to read-only memory...\n");
        strcpy(ptr1, "Modified");  // This should cause a segmentation fault
        
        printf("ptr1: %s\n", (char*)ptr1);
    } else {
        printf("Failed to set memory protection\n");
    }
    
    // Test free and realloc
    memory_manager_free(manager, ptr2);
    void* ptr4 = memory_manager_malloc(manager, 150);
    if (ptr4) {
        printf("Reallocation after free successful\n");
        strcpy(ptr4, "Reallocated");
        printf("ptr4: %s\n", (char*)ptr4);
    }
    
    // Test realloc
    void* ptr5 = memory_manager_realloc(manager, ptr1, 200);
    if (ptr5) {
        printf("Realloc successful\n");
        strcpy(ptr5, "Reallocated string");
        printf("ptr5: %s\n", (char*)ptr5);
    }
    
    // Print memory statistics
    printf("\nMemory Statistics:\n");
    memory_manager_print_stats(manager);
    
    // Test thread safety
    printf("\nTesting Thread Safety:\n");
    
    pthread_t threads[NUM_THREADS];
    
    // Create threads
    for (int i = 0; i < NUM_THREADS; i++) {
        if (pthread_create(&threads[i], NULL, heap_allocator_thread, manager) != 0) {
            printf("Failed to create thread %d\n", i);
        }
    }
    
    // Wait for threads to finish
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // Print memory statistics after multi-threaded operations
    printf("\nMemory Statistics After Multi-threaded Operations:\n");
    memory_manager_print_stats(manager);
    
    memory_manager_destroy(manager);
    printf("Heap allocator tests completed\n\n");
}

void test_stack_allocator() {
    printf("Testing Stack Allocator:\n");
    
    // Initialize stack allocator with 1MB pool
    StackAllocator* allocator = stack_allocator_init(1024 * 1024);
    if (!allocator) {
        printf("Failed to initialize stack allocator\n");
        return;
    }
    
    // Test sequential allocation
    void* ptr1 = stack_allocator_allocate(allocator, 100);
    void* ptr2 = stack_allocator_allocate(allocator, 200);
    void* ptr3 = stack_allocator_allocate(allocator, 300);
    
    if (ptr1 && ptr2 && ptr3) {
        printf("Sequential allocation successful\n");
        
        // Test memory usage
        strcpy(ptr1, "Stack");
        strcpy(ptr2, "Allocator");
        strcpy(ptr3, "Test");
        
        printf("ptr1: %s\n", (char*)ptr1);
        printf("ptr2: %s\n", (char*)ptr2);
        printf("ptr3: %s\n", (char*)ptr3);
    }
    
    // Test free (should only work for the most recently allocated block)
    stack_allocator_free(allocator, ptr3);
    void* ptr4 = stack_allocator_allocate(allocator, 150);
    if (ptr4) {
        printf("Reallocation after free successful\n");
        strcpy(ptr4, "NewBlock");
        printf("ptr4: %s\n", (char*)ptr4);
    }
    
    // Print memory statistics
    printf("\nMemory Statistics:\n");
    stack_allocator_print_stats(allocator);
    
    // Test thread safety
    printf("\nTesting Thread Safety:\n");
    
    pthread_t threads[NUM_THREADS];
    
    // Create threads
    for (int i = 0; i < NUM_THREADS; i++) {
        if (pthread_create(&threads[i], NULL, stack_allocator_thread, allocator) != 0) {
            printf("Failed to create thread %d\n", i);
        }
    }
    
    // Wait for threads to finish
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // Print memory statistics after multi-threaded operations
    printf("\nMemory Statistics After Multi-threaded Operations:\n");
    stack_allocator_print_stats(allocator);
    
    stack_allocator_destroy(allocator);
    printf("Stack allocator tests completed\n\n");
}

int main() {
    test_heap_allocator();
    test_stack_allocator();
    return 0;
} 