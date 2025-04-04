# UDP Bootloader

This is a simple UDP bootloader that can receive a kernel image over the network and load it into memory. It's designed to be embedded in an FPGA image to avoid having to redownload the kernel over serial each time.

## Features

- Receives kernel image over UDP
- Simple protocol with acknowledgments
- Checksum verification
- Can be embedded in FPGA image

## Components

- `bootloader.c`: The main bootloader code
- `startup.S`: Assembly startup code
- `linker.ld`: Linker script
- `kernel_server.c`: Host-side program to send kernel images

## Building

### Bootloader (for FPGA)

```bash
make bootloader.bin
```

This will create a binary file that can be embedded in your FPGA image.

### Kernel Server (for host)

```bash
make kernel_server
```

## Usage

1. Embed the bootloader binary in your FPGA image
2. Build your kernel
3. Run the kernel server:

```bash
./kernel_server kernel.bin
```

4. Power on your FPGA
5. The bootloader will discover the kernel server and download the kernel
6. The bootloader will jump to the kernel entry point

## Protocol

The bootloader uses a simple protocol:

1. Bootloader sends a "BOOTLOADER_DISCOVER" packet to broadcast address
2. Kernel server responds with the kernel header
3. Bootloader acknowledges the header
4. Kernel server sends kernel data in chunks
5. Bootloader acknowledges each chunk
6. After receiving all data, bootloader verifies checksum and jumps to kernel

## Customization

You can customize the bootloader by modifying the following:

- Network configuration (MAC address, IP address, ports)
- Kernel load address
- Packet size
- Checksum algorithm

## Hardware Requirements

The bootloader requires:

- Ethernet controller
- At least 64KB of flash and 64KB of RAM
- ARM processor

## License

This code is released under the MIT License. 