
# Threaded Job Queue (Thread Pool with Work Stealing)

## 🚀 Overview

This project implements a **thread pool** in C, where:
- The **main thread** submits jobs.
- A fixed set of **worker threads** execute those jobs.
- **Condition variables** are used to sleep/wake workers.
- **Mutex locks** ensure safe access to shared queues.
- Includes **work stealing** for improved load balancing.
- A **timer thread** can be used to schedule periodic or delayed jobs.

---

## 🛠️ Features

- ✅ Fixed-size thread pool
- ✅ Job queue with `enqueue` / `dequeue` operations
- ✅ Condition variables to avoid busy waiting
- ✅ Graceful shutdown of workers
- ✅ Optional work-stealing support between thread-local queues
- ✅ Timer thread to simulate scheduled jobs (e.g., run after delay)

---
## 🧪 Strech Goals
- Support dynamic resizing of the thread pool
- Add job prioritization (e.g., high vs low priority jobs)
- Expose job results using futures/promises
- Implement delayed or periodic jobs using the timer thread
- Add benchmarking support for job latency / throughput

---

## 📁 File Structure

```bash
.
├── main.c              # Entry point and test setup
├── thread_pool.c       # Thread pool implementation
├── thread_pool.h       # Header for thread pool API
├── job_queue.c         # Job queue (circular or linked list)
├── job_queue.h         # Job queue header
├── timer.c             # (Optional) Scheduled job management
├── Makefile            # Build system
└── README.md           # You're here!
```
---

## 📦 Compilation
```bash
make
```

To run:
```bash
./thread_pool_demo
```

## 🔨 Usage Example
```c
void print_hello(void* arg) {
    printf("Hello from thread %ld\n", (long)arg);
}

int main() {
    thread_pool_t* pool = thread_pool_create(4); // 4 worker threads

    for (long i = 0; i < 10; i++) {
        thread_pool_submit(pool, print_hello, (void*)i);
    }

    thread_pool_destroy(pool);
    return 0;
}

```


## ✅ Requirements
- GCC or Clang
- POSIX-compatible system (Linux/macOS)
- Pthreads library (-lpthread)

