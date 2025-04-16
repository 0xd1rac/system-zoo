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
