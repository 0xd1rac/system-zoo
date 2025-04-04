#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <pcap.h>
#include "packet_sniffer.h"

// Global variables
static pcap_t *handle = NULL;
static int running = 1;

// Signal handler for graceful shutdown
void signal_handler(int signum) {
    printf("\nStopping packet capture...\n");
    running = 0;
}

int main(int argc, char *argv[]) {
    char *device = NULL;
    char errbuf[PCAP_ERRBUF_SIZE];
    
    // Set up signal handler
    signal(SIGINT, signal_handler);
    
    // Get the default device if none specified
    if (argc > 1) {
        device = argv[1];
    } else {
        device = pcap_lookupdev(errbuf);
        if (device == NULL) {
            fprintf(stderr, "Couldn't find default device: %s\n", errbuf);
            return 1;
        }
    }
    
    printf("Starting packet capture on device: %s\n", device);
    
    // Initialize pcap
    if (initialize_pcap(device, &handle) != 0) {
        return 1;
    }
    
    // Start capturing packets
    printf("Capturing packets... Press Ctrl+C to stop\n");
    printf("----------------------------------------\n");
    
    while (running) {
        if (pcap_dispatch(handle, 1, packet_handler, NULL) < 0) {
            break;
        }
    }
    
    // Cleanup
    cleanup_pcap(handle);
    
    // Print final statistics
    print_statistics(&stats);
    
    return 0;
} 