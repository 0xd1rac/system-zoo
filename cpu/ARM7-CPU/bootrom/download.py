#!/usr/bin/env python3

import serial
import sys
import time
import struct

def send_program(port, data, address):
    # Open serial port
    ser = serial.Serial(port, 115200, timeout=1)
    
    # Wait for bootrom prompt
    while True:
        line = ser.readline().decode('ascii')
        if "Waiting for download" in line:
            break
    
    # Send start marker
    ser.write(bytes([0xAA]))
    
    # Send length (2 bytes)
    length = len(data)
    ser.write(struct.pack('<H', length))
    
    # Send destination address (4 bytes)
    ser.write(struct.pack('<I', address))
    
    # Send program data
    ser.write(data)
    
    # Wait for acknowledgment
    ack = ser.read(1)
    if ack != b'\x55':
        print("Error: No acknowledgment received")
        return False
    
    print(f"Program downloaded successfully to address 0x{address:08x}")
    return True

def main():
    if len(sys.argv) != 4:
        print("Usage: download.py <port> <binary_file> <address>")
        sys.exit(1)
    
    port = sys.argv[1]
    binary_file = sys.argv[2]
    address = int(sys.argv[3], 16)
    
    # Read binary file
    with open(binary_file, 'rb') as f:
        data = f.read()
    
    # Send program
    if send_program(port, data, address):
        print("Download complete")
    else:
        print("Download failed")
        sys.exit(1)

if __name__ == '__main__':
    main() 