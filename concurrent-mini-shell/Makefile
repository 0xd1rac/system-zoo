CC = gcc
CFLAGS = -Wall -Wextra -pthread
SRCS = main.c job_control.c input_handler.c
OBJS = $(SRCS:.c=.o)
TARGET = shell

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET) $(CFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET) 