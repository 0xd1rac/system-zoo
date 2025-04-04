CC = gcc
CFLAGS = -Wall -Wextra -O2

# Bootloader (for FPGA)
BOOTLOADER_SRCS = bootloader.c
BOOTLOADER_OBJS = $(BOOTLOADER_SRCS:.c=.o)
BOOTLOADER = bootloader.bin

# Kernel server (for host)
KERNEL_SERVER_SRCS = kernel_server.c
KERNEL_SERVER_OBJS = $(KERNEL_SERVER_SRCS:.c=.o)
KERNEL_SERVER = kernel_server

# Default target
all: $(KERNEL_SERVER)

# Build kernel server
$(KERNEL_SERVER): $(KERNEL_SERVER_OBJS)
	$(CC) $(CFLAGS) -o $@ $^

# Build bootloader (for FPGA)
$(BOOTLOADER): $(BOOTLOADER_OBJS)
	$(CC) $(CFLAGS) -nostdlib -T linker.ld -o bootloader.elf $(BOOTLOADER_OBJS)
	objcopy -O binary bootloader.elf $@

# Compile C files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean
clean:
	rm -f $(BOOTLOADER_OBJS) $(KERNEL_SERVER_OBJS) $(BOOTLOADER) $(KERNEL_SERVER) bootloader.elf

# Run kernel server
run: $(KERNEL_SERVER)
	./$(KERNEL_SERVER) kernel.bin

.PHONY: all clean run 