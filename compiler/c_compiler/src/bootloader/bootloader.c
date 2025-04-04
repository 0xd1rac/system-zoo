/**
 * UDP Bootloader
 * 
 * This bootloader receives a kernel image over UDP and loads it into memory.
 * It can be embedded in an FPGA image to avoid having to redownload the kernel
 * over serial each time.
 */

#include <stdint.h>
#include <string.h>

// Network configuration
#define BOOTLOADER_PORT 1234
#define KERNEL_PORT 1235
#define MAX_PACKET_SIZE 1024
#define KERNEL_LOAD_ADDRESS 0x100000

// Ethernet MAC address (replace with your FPGA's MAC)
#define MAC_ADDRESS {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}

// IP configuration (replace with your network settings)
#define IP_ADDRESS {192, 168, 1, 100}
#define SUBNET_MASK {255, 255, 255, 0}
#define GATEWAY {192, 168, 1, 1}

// Kernel image header
typedef struct {
    uint32_t magic;          // Magic number to identify kernel
    uint32_t size;           // Size of kernel in bytes
    uint32_t entry_point;    // Entry point address
    uint32_t checksum;       // Simple checksum
} kernel_header_t;

// Function prototypes
void init_network(void);
void receive_kernel(void);
uint32_t calculate_checksum(uint8_t *data, uint32_t size);
void jump_to_kernel(uint32_t entry_point);

// Hardware-specific functions (implement these for your FPGA)
void init_ethernet(void);
void send_udp_packet(uint8_t *data, uint16_t length, uint16_t src_port, uint16_t dst_port, uint8_t *dst_ip);
void receive_udp_packet(uint8_t *buffer, uint16_t *length, uint16_t *src_port, uint8_t *src_ip);
void delay_ms(uint32_t ms);

// Main bootloader function
void bootloader_main(void) {
    // Initialize network
    init_network();
    
    // Wait for kernel
    receive_kernel();
    
    // We should never return from receive_kernel if successful
    // If we do, something went wrong
    while (1) {
        // Blink LED or indicate error
        delay_ms(1000);
    }
}

// Initialize network
void init_network(void) {
    // Initialize Ethernet hardware
    init_ethernet();
    
    // Wait for link to be established
    delay_ms(1000);
}

// Receive kernel over UDP
void receive_kernel(void) {
    uint8_t packet_buffer[MAX_PACKET_SIZE];
    uint16_t packet_length;
    uint16_t src_port;
    uint8_t src_ip[4];
    
    uint8_t *kernel_buffer = (uint8_t *)KERNEL_LOAD_ADDRESS;
    uint32_t kernel_size = 0;
    uint32_t bytes_received = 0;
    kernel_header_t *header = NULL;
    
    // Send broadcast packet to discover kernel server
    uint8_t discover_packet[] = "BOOTLOADER_DISCOVER";
    uint8_t broadcast_ip[] = {255, 255, 255, 255};
    send_udp_packet(discover_packet, sizeof(discover_packet), BOOTLOADER_PORT, KERNEL_PORT, broadcast_ip);
    
    // Wait for response
    while (1) {
        receive_udp_packet(packet_buffer, &packet_length, &src_port, src_ip);
        
        // Check if this is a kernel packet
        if (src_port == KERNEL_PORT) {
            // First packet should contain the kernel header
            if (bytes_received == 0) {
                header = (kernel_header_t *)packet_buffer;
                
                // Verify magic number
                if (header->magic != 0xDEADBEEF) {
                    continue;  // Not a valid kernel
                }
                
                kernel_size = header->size;
                
                // Copy header to kernel buffer
                memcpy(kernel_buffer, packet_buffer, sizeof(kernel_header_t));
                bytes_received = sizeof(kernel_header_t);
                
                // Send acknowledgment
                uint8_t ack_packet[] = "ACK";
                send_udp_packet(ack_packet, sizeof(ack_packet), BOOTLOADER_PORT, KERNEL_PORT, src_ip);
            } else {
                // Copy kernel data
                memcpy(kernel_buffer + bytes_received, packet_buffer, packet_length);
                bytes_received += packet_length;
                
                // Send acknowledgment
                uint8_t ack_packet[] = "ACK";
                send_udp_packet(ack_packet, sizeof(ack_packet), BOOTLOADER_PORT, KERNEL_PORT, src_ip);
                
                // Check if we've received the entire kernel
                if (bytes_received >= kernel_size + sizeof(kernel_header_t)) {
                    // Verify checksum
                    uint32_t calculated_checksum = calculate_checksum(
                        kernel_buffer + sizeof(kernel_header_t), 
                        kernel_size
                    );
                    
                    if (calculated_checksum == header->checksum) {
                        // Kernel received successfully, jump to it
                        jump_to_kernel(header->entry_point);
                    } else {
                        // Checksum error, start over
                        bytes_received = 0;
                        header = NULL;
                    }
                }
            }
        }
    }
}

// Calculate simple checksum
uint32_t calculate_checksum(uint8_t *data, uint32_t size) {
    uint32_t sum = 0;
    for (uint32_t i = 0; i < size; i++) {
        sum += data[i];
    }
    return sum;
}

// Jump to kernel
void jump_to_kernel(uint32_t entry_point) {
    // Disable interrupts
    // (implement based on your hardware)
    
    // Jump to kernel
    typedef void (*kernel_entry_t)(void);
    kernel_entry_t kernel_entry = (kernel_entry_t)entry_point;
    kernel_entry();
    
    // We should never return
}

// Hardware-specific functions (implement these for your FPGA)

// Initialize Ethernet hardware
void init_ethernet(void) {
    // Configure MAC address
    uint8_t mac[] = MAC_ADDRESS;
    // Set MAC address in hardware registers
    
    // Configure IP address
    uint8_t ip[] = IP_ADDRESS;
    uint8_t subnet[] = SUBNET_MASK;
    uint8_t gateway[] = GATEWAY;
    // Set IP configuration in hardware registers
    
    // Initialize UDP
    // Configure UDP sockets
}

// Send UDP packet
void send_udp_packet(uint8_t *data, uint16_t length, uint16_t src_port, uint16_t dst_port, uint8_t *dst_ip) {
    // Implement UDP send for your hardware
}

// Receive UDP packet
void receive_udp_packet(uint8_t *buffer, uint16_t *length, uint16_t *src_port, uint8_t *src_ip) {
    // Implement UDP receive for your hardware
}

// Delay in milliseconds
void delay_ms(uint32_t ms) {
    // Implement delay for your hardware
} 