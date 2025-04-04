/**
 * Kernel Server
 * 
 * This program sends a kernel image to the UDP bootloader.
 * It listens for bootloader discovery packets and responds with the kernel.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>

// Network configuration
#define BOOTLOADER_PORT 1234
#define KERNEL_PORT 1235
#define MAX_PACKET_SIZE 1024

// Kernel image header
typedef struct {
    uint32_t magic;          // Magic number to identify kernel
    uint32_t size;           // Size of kernel in bytes
    uint32_t entry_point;    // Entry point address
    uint32_t checksum;       // Simple checksum
} kernel_header_t;

// Function prototypes
uint32_t calculate_checksum(uint8_t *data, uint32_t size);
void send_kernel(int sock, struct sockaddr_in *client_addr, const char *kernel_file);

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <kernel_file>\n", argv[0]);
        return 1;
    }
    
    // Create UDP socket
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }
    
    // Set socket options
    int broadcast = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
        perror("setsockopt");
        close(sock);
        return 1;
    }
    
    // Bind to kernel port
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(KERNEL_PORT);
    
    if (bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind");
        close(sock);
        return 1;
    }
    
    printf("Kernel server listening on port %d\n", KERNEL_PORT);
    printf("Waiting for bootloader discovery...\n");
    
    // Wait for bootloader discovery
    char buffer[MAX_PACKET_SIZE];
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    
    while (1) {
        int recv_len = recvfrom(sock, buffer, MAX_PACKET_SIZE, 0, 
                                (struct sockaddr *)&client_addr, &client_len);
        
        if (recv_len < 0) {
            perror("recvfrom");
            continue;
        }
        
        // Check if this is a bootloader discovery packet
        if (strncmp(buffer, "BOOTLOADER_DISCOVER", 18) == 0) {
            printf("Bootloader discovered at %s:%d\n", 
                   inet_ntoa(client_addr.sin_addr), 
                   ntohs(client_addr.sin_port));
            
            // Send kernel
            send_kernel(sock, &client_addr, argv[1]);
        } else if (strncmp(buffer, "ACK", 3) == 0) {
            // Acknowledgment received, continue sending
            printf("Acknowledgment received\n");
        }
    }
    
    close(sock);
    return 0;
}

// Calculate simple checksum
uint32_t calculate_checksum(uint8_t *data, uint32_t size) {
    uint32_t sum = 0;
    for (uint32_t i = 0; i < size; i++) {
        sum += data[i];
    }
    return sum;
}

// Send kernel to bootloader
void send_kernel(int sock, struct sockaddr_in *client_addr, const char *kernel_file) {
    // Open kernel file
    FILE *fp = fopen(kernel_file, "rb");
    if (!fp) {
        perror("fopen");
        return;
    }
    
    // Get kernel size
    fseek(fp, 0, SEEK_END);
    uint32_t kernel_size = fseek(fp, 0, SEEK_CUR);
    fseek(fp, 0, SEEK_SET);
    
    // Allocate buffer for kernel
    uint8_t *kernel_buffer = malloc(kernel_size);
    if (!kernel_buffer) {
        perror("malloc");
        fclose(fp);
        return;
    }
    
    // Read kernel
    if (fread(kernel_buffer, 1, kernel_size, fp) != kernel_size) {
        perror("fread");
        free(kernel_buffer);
        fclose(fp);
        return;
    }
    
    fclose(fp);
    
    // Calculate checksum
    uint32_t checksum = calculate_checksum(kernel_buffer, kernel_size);
    
    // Prepare kernel header
    kernel_header_t header;
    header.magic = 0xDEADBEEF;
    header.size = kernel_size;
    header.entry_point = 0x100000 + sizeof(kernel_header_t);  // After header
    header.checksum = checksum;
    
    // Send kernel header
    if (sendto(sock, &header, sizeof(header), 0, 
               (struct sockaddr *)client_addr, sizeof(*client_addr)) < 0) {
        perror("sendto");
        free(kernel_buffer);
        return;
    }
    
    // Wait for acknowledgment
    char ack_buffer[MAX_PACKET_SIZE];
    struct sockaddr_in ack_addr;
    socklen_t ack_len = sizeof(ack_addr);
    
    if (recvfrom(sock, ack_buffer, MAX_PACKET_SIZE, 0, 
                 (struct sockaddr *)&ack_addr, &ack_len) < 0) {
        perror("recvfrom");
        free(kernel_buffer);
        return;
    }
    
    // Send kernel in chunks
    uint32_t offset = 0;
    while (offset < kernel_size) {
        uint32_t chunk_size = (kernel_size - offset) > MAX_PACKET_SIZE ? 
                              MAX_PACKET_SIZE : (kernel_size - offset);
        
        if (sendto(sock, kernel_buffer + offset, chunk_size, 0, 
                  (struct sockaddr *)client_addr, sizeof(*client_addr)) < 0) {
            perror("sendto");
            free(kernel_buffer);
            return;
        }
        
        // Wait for acknowledgment
        if (recvfrom(sock, ack_buffer, MAX_PACKET_SIZE, 0, 
                     (struct sockaddr *)&ack_addr, &ack_len) < 0) {
            perror("recvfrom");
            free(kernel_buffer);
            return;
        }
        
        offset += chunk_size;
        printf("Sent %u/%u bytes\n", offset, kernel_size);
    }
    
    printf("Kernel sent successfully\n");
    free(kernel_buffer);
} 