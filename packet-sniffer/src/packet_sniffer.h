#ifndef PACKET_SNIFFER_H
#define PACKET_SNIFFER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pcap.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <time.h>

// Maximum size of packet buffer
#define MAX_PACKET_SIZE 65535

// Structure to hold packet statistics
typedef struct {
    unsigned long total_packets;
    unsigned long tcp_packets;
    unsigned long udp_packets;
    unsigned long icmp_packets;
    unsigned long other_packets;
} PacketStats;

// Structure to hold packet information
typedef struct {
    time_t timestamp;
    char source_ip[INET_ADDRSTRLEN];
    char dest_ip[INET_ADDRSTRLEN];
    unsigned short source_port;
    unsigned short dest_port;
    unsigned char protocol;
    unsigned int length;
} PacketInfo;

// Function declarations
void packet_handler(u_char *user, const struct pcap_pkthdr *pkthdr, const u_char *packet);
void print_packet_info(const PacketInfo *info);
void print_statistics(const PacketStats *stats);
int initialize_pcap(const char *device, pcap_t **handle);
void cleanup_pcap(pcap_t *handle);
void process_packet(const u_char *packet, int len, PacketInfo *info);
void update_statistics(PacketStats *stats, unsigned char protocol);

#endif // PACKET_SNIFFER_H 