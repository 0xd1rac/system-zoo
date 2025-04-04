# Network Packet Sniffer

A command-line network packet sniffer that captures and analyzes network traffic in real-time. This tool can capture and display information about TCP, UDP, and ICMP packets, including source/destination IP addresses, ports, and packet statistics.

## Features

- Real-time packet capture and analysis
- Support for TCP, UDP, and ICMP protocols
- Display of source and destination IP addresses and ports
- Packet statistics tracking
- Graceful shutdown with Ctrl+C

## Prerequisites

- Linux operating system
- GCC compiler
- libpcap development library

### Installing Dependencies

On Debian/Ubuntu:
```bash
sudo apt-get update
sudo apt-get install build-essential libpcap-dev
```

On CentOS/RHEL:
```bash
sudo yum groupinstall "Development Tools"
sudo yum install libpcap-devel
```

## Building

1. Clone the repository:
```bash
git clone <repository-url>
cd packet-sniffer
```

2. Build the project:
```bash
make
```

The executable will be created in the `bin` directory.

## Usage

Run the packet sniffer with default network interface:
```bash
sudo ./bin/packet_sniffer
```

Or specify a network interface:
```bash
sudo ./bin/packet_sniffer eth0
```

Note: Root privileges (sudo) are required to capture packets.

### Output Format

The sniffer displays the following information for each packet:
- Timestamp
- Source IP address
- Destination IP address
- Protocol (TCP/UDP/ICMP)
- Source and destination ports (for TCP/UDP)
- Packet length

Statistics are displayed when the program is terminated (Ctrl+C).

## Cleaning Up

To clean the build files:
```bash
make clean
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 