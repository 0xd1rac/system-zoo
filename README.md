# system-zoo

 ## Project 1: Threaded Job Queue (Thread Pool with Work Stealing)
**Goal:** Implement a thread pool where:
- Main thread dispatches jobs (e.g., tasks like printf, computations).
- Worker threads wait for jobs using condition variables.
- Queue is shared → needs mutex locks.
- You’ll need to handle shutdown, race conditions, and thread-safe data access.
- Add work stealing between worker queues.
- Add a timer thread to simulate scheduled jobs.

## Project 2: Bounded Buffer (Producer-Consumer)
  **Goal:** Simulate multiple producers and consumers using a bounded circular buffer.
You’ll need:
- A mutex to protect buffer access.
- Two semaphores:
  - One for available slots.
  - One for filled slots.
- Properly coordinate sem_wait, sem_post, and mutex locking.
- Make producers and consumers run at random speeds.
- Detect and log starvation.

## Project 3: Multiplayer Chat Server (Event-Based Concurrency)
Goal: Create a simple TCP chat server:
- One thread handles incoming connections.
- Each client gets a thread.
- Shared message queue that broadcasts to all connected clients.
- Use mutex or condition variables to protect shared queues.
- Use select() instead of threads for handling sockets.
- Add username support, disconnection handling, and message history.

## Project 4: Custom Lock Library
Goal:
Reimplement pthread_mutex_t from scratch using atomic operations (like __sync_lock_test_and_set) and create a minimal spinlock and ticket lock.

What You'll Learn:
- Basic lock implementation
- Lock fairness (ticket locks)
- Busy-wait vs blocking behavior

Bonus:
Benchmark your lock performance vs pthread_mutex.

## Project 5: Readers-Writers Problem (Using Condition Variables)
**Focus**: Condition Variables + Locks

**Goal:** Implement the classic Readers-Writers problem:
- Multiple readers can read at once.
- Writers need exclusive access.
- Use a shared counter, mutex, and two condition variables: readPhase, writePhase.

**What You'll Learn:**
- When to signal/broadcast
- How to avoid starvation
- Fine-grained thread coordination

**Bonus:**
Implement both:
- First readers preference
- First writers preference
  
## Project 6: Traffic Light Simulation (Using Semaphores)
**Focus:** Semaphores

**Goal:** Simulate a 4-way intersection:
- Each lane is a thread.
- A central semaphore controls how many cars (threads) can be in the intersection at once.
- Only 1 car per direction allowed at a time (binary semaphore per lane).

**What You'll Learn:**
- Using sem_wait/sem_post
- Managing concurrent access
- Modeling real-world constraints with semaphores

**Bonus:**
- Add pedestrian crossing as another semaphore.
- Add traffic light cycles using timed threads.

## Deadlock Detection Tool

**Goal:**  
Implement a deadlock detection system that tracks locks held and requested by threads.

**What to Implement:**
- A resource graph (thread ↔ lock relationships)
- Periodic check for cycles in the graph
- Detection alert if a cycle is found (i.e., deadlock)

**What You’ll Learn:**
- How to track lock ownership across threads
- Graph-based cycle detection
- How real systems (like Java's `jstack`) detect deadlocks

## Rate Limiter or Watchdog Timer with Signals

**Goal:**  
Create a timer-based system that monitors or limits thread behavior using signals.

**What to Implement:**
- Use `sigaction()` to catch `SIGALRM`
- Set interval timers using `setitimer()`
- Use it to limit how often a function runs, or detect if a thread stalls

**What You’ll Learn:**
- Asynchronous signal handling
- Signal-safe functions and reentrancy
- Timers and watchdog patterns used in system daemons

Inter-Process Shared Memory + Semaphores

**Goal:**  
Implement a shared memory message-passing system between forked processes.

**What to Implement:**
- Create shared memory with `shm_open` and `mmap`
- Synchronize access using `sem_open`
- Fork multiple processes that produce/consume messages

 Multicore Lock Benchmarking

**Goal:**  
Benchmark and compare different locking mechanisms across multiple cores.

**What to Implement:**
- Custom test harness using 2, 4, and 8 threads
- Measure throughput and latency of:
  - `pthread_mutex`
  - Spinlock (custom and `pthread_spinlock`)
  - Ticket lock (custom)

**What You’ll Learn:**
- Effects of CPU contention and cache coherence
- Performance tradeoffs between lock types
- NUMA implications

**What You’ll Learn:**
- Shared memory between processes (not threads)
- Named semaphores and lifetime management
- Basics of IPC (Inter-process communication)

# 💻 OS Memory Management Project Series (C)

## 🧭 1. Virtual Address Visualizer

**Topics:** Address Spaces, Address Translation  
**Goal:** Build a CLI tool that takes a virtual address and visualizes how it maps to segments (code, heap, stack) and physical memory (if possible).

**Features:**
- Parse `/proc/self/maps` on Linux
- Translate given pointer addresses to segment labels
- Display binary layout and page number breakdown

---

## 📦 2. Custom `malloc()` and `free()` (Memory Allocator)

**Topics:** Memory API, Free Space Management  
**Goal:** Implement your own memory allocator using `sbrk()` or `mmap()`.

**Features:**
- Implement first-fit and best-fit strategies
- Support `malloc()`, `free()`, `calloc()`, and `realloc()`
- Track memory fragmentation

---

## 🧮 3. Manual Page Table Translator

**Topics:** Address Translation, Paging  
**Goal:** Simulate a page table in user space and translate virtual → physical addresses manually.

**Features:**
- Implement single-level and multi-level page tables
- Perform bit-level address breakdown
- Support page faults and invalid entries

---

## 📊 4. Paging Visual Simulator

**Topics:** Paging, TLBs, Page Tables  
**Goal:** Build a simulator for paging and TLB behavior over a series of memory accesses.

**Features:**
- Simulate TLB hits/misses
- Track page table lookups
- Support FIFO and LRU page replacement

---

## 🗺️ 5. Segmentation Fault Injector

**Topics:** Segmentation  
**Goal:** Write code that intentionally causes segmentation faults and catch them using `sigaction()` to explore boundary protections.

**Features:**
- Stack overflow
- Out-of-bounds heap access
- Null pointer dereference + logging

---

## 🔁 6. Buddy Memory Allocator

**Topics:** Free Space Management  
**Goal:** Implement the buddy system memory allocator with recursive splitting and merging.

**Features:**
- Use power-of-two block sizes
- Track internal/external fragmentation
- Visualize allocator state

---

## ⚡ 7. TLB Hit Rate Benchmark

**Topics:** Translation Lookaside Buffers (TLB)  
**Goal:** Benchmark access patterns that produce TLB hits vs misses.

**Features:**
- Vary strides (cache line vs page size)
- Report timing and TLB miss rates
- Use `perf stat` on Linux for measurements

---

## 🔃 8. Page Replacement Simulator

**Topics:** Swapping Policies, Advanced Page Tables  
**Goal:** Simulate different page replacement algorithms.

**Features:**
- Implement FIFO, LRU, Clock, and Optimal
- Feed in memory access traces
- Visualize page faults and frame state

---

## 🧠 9. LRU Cache with Backing Store

**Topics:** Swapping Mechanisms  
**Goal:** Build an LRU-based memory cache backed by disk (a file).

**Features:**
- Evict least-recently-used pages
- Simulate disk reads/writes with `fread()` and `fwrite()`
- Track swap-in and swap-out counts

---

## 🧰 10. Virtual Memory System End-to-End

**Topics:** Complete VM Systems  
**Goal:** Build a minimal OS-like VM system simulator combining page table, TLB, allocator, and swap policies.

**Features:**
- Virtual to physical mapping
- Page faults + swapping
- Backing store simulation
- Logging + stats

---

