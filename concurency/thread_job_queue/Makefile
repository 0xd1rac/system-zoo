CC = gcc
CFLAGS = -Wall -Wextra -pthread
OBJS = main.o thread_pool.o task_queue.o

all: thread_pool_demo

thread_pool_demo: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) thread_pool_demo

.PHONY: all clean
