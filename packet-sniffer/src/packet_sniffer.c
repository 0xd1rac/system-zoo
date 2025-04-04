#include "packet_sniffer.h"

// Global statistics
static PacketStats stats = {0};

void packet_handler(u_char *user, const struct pcap_pkthdr *pkthdr, const u_char *packet) {
    PacketInfo info = {0};
    
    // Process the packet
    process_packet(packet, pkthdr->len, &info);
    
    // Update statistics
    update_statistics(&stats, info.protocol);
    
    // Print packet information
    print_packet_info(&info);
}

void process_packet(const u_char *packet, int len, PacketInfo *info) {
    struct ether_header *eth_header;
    struct ip *ip_header;
    struct tcphdr *tcp_header;
    struct udphdr *udp_header;
    
    // Get timestamp
    info->timestamp = time(NULL);
    info->length = len;
    
    // Parse Ethernet header
    eth_header = (struct ether_header *)packet;
    
    // Check if it's an IP packet
    if (ntohs(eth_header->ether_type) == ETHERTYPE_IP) {
        // Parse IP header
        ip_header = (struct ip *)(packet + sizeof(struct ether_header));
        
        // Store IP addresses
        inet_ntop(AF_INET, &(ip_header->ip_src), info->source_ip, INET_ADDRSTRLEN);
        inet_ntop(AF_INET, &(ip_header->ip_dst), info->dest_ip, INET_ADDRSTRLEN);
        
        // Get protocol
        info->protocol = ip_header->ip_p;
        
        // Parse transport layer header based on protocol
        if (info->protocol == IPPROTO_TCP) {
            tcp_header = (struct tcphdr *)((u_char *)ip_header + sizeof(struct ip));
            info->source_port = ntohs(tcp_header->source);
            info->dest_port = ntohs(tcp_header->dest);
        } else if (info->protocol == IPPROTO_UDP) {
            udp_header = (struct udphdr *)((u_char *)ip_header + sizeof(struct ip));
            info->source_port = ntohs(udp_header->source);
            info->dest_port = ntohs(udp_header->dest);
        }
    }
}

void print_packet_info(const PacketInfo *info) {
    char time_str[26];
    ctime_r(&info->timestamp, time_str);
    time_str[24] = '\0';  // Remove newline
    
    printf("\nPacket captured at %s\n", time_str);
    printf("Source IP: %s\n", info->source_ip);
    printf("Destination IP: %s\n", info->dest_ip);
    
    if (info->protocol == IPPROTO_TCP) {
        printf("Protocol: TCP\n");
        printf("Source Port: %d\n", info->source_port);
        printf("Destination Port: %d\n", info->dest_port);
    } else if (info->protocol == IPPROTO_UDP) {
        printf("Protocol: UDP\n");
        printf("Source Port: %d\n", info->source_port);
        printf("Destination Port: %d\n", info->dest_port);
    } else if (info->protocol == IPPROTO_ICMP) {
        printf("Protocol: ICMP\n");
    } else {
        printf("Protocol: Other\n");
    }
    
    printf("Packet Length: %d bytes\n", info->length);
    printf("----------------------------------------\n");
}

void print_statistics(const PacketStats *stats) {
    printf("\nPacket Statistics:\n");
    printf("Total Packets: %lu\n", stats->total_packets);
    printf("TCP Packets: %lu\n", stats->tcp_packets);
    printf("UDP Packets: %lu\n", stats->udp_packets);
    printf("ICMP Packets: %lu\n", stats->icmp_packets);
    printf("Other Packets: %lu\n", stats->other_packets);
    printf("----------------------------------------\n");
}

void update_statistics(PacketStats *stats, unsigned char protocol) {
    stats->total_packets++;
    
    switch (protocol) {
        case IPPROTO_TCP:
            stats->tcp_packets++;
            break;
        case IPPROTO_UDP:
            stats->udp_packets++;
            break;
        case IPPROTO_ICMP:
            stats->icmp_packets++;
            break;
        default:
            stats->other_packets++;
            break;
    }
}

int initialize_pcap(const char *device, pcap_t **handle) {
    char errbuf[PCAP_ERRBUF_SIZE];
    
    // Open the device for capturing
    *handle = pcap_open_live(device, MAX_PACKET_SIZE, 1, 1000, errbuf);
    
    if (*handle == NULL) {
        fprintf(stderr, "Couldn't open device %s: %s\n", device, errbuf);
        return -1;
    }
    
    return 0;
}

void cleanup_pcap(pcap_t *handle) {
    if (handle != NULL) {
        pcap_close(handle);
    }
} 