.section .text.boot
.global _start

// Constants
.equ UART_BASE, 0x10000000  // UART base address
.equ UART_DATA,  0x0         // UART data register offset
.equ UART_STATUS, 0x4        // UART status register offset
.equ UART_RX_READY, 0x1      // UART RX ready bit
.equ UART_TX_READY, 0x2      // UART TX ready bit
.equ RAM_BASE, 0x20000000    // RAM base address

_start:
    // Initialize stack pointer
    ldr sp, =0x20010000      // Set stack to top of RAM
    
    // Initialize UART
    bl uart_init
    
    // Send welcome message
    ldr r0, =welcome_msg
    bl uart_puts
    
    // Main download loop
download_loop:
    // Wait for start marker (0xAA)
    bl uart_getc
    cmp r0, #0xAA
    bne download_loop
    
    // Get length (2 bytes)
    bl uart_getc
    mov r1, r0
    bl uart_getc
    orr r1, r1, r0, lsl #8   // Combine into 16-bit length
    
    // Get destination address
    bl uart_getc
    mov r2, r0
    bl uart_getc
    orr r2, r2, r0, lsl #8
    bl uart_getc
    orr r2, r2, r0, lsl #16
    bl uart_getc
    orr r2, r2, r0, lsl #24  // Combine into 32-bit address
    
    // Download data
    mov r3, r2               // Save destination
download_data:
    bl uart_getc
    strb r0, [r3], #1       // Store byte and increment address
    subs r1, r1, #1         // Decrement counter
    bne download_data
    
    // Send acknowledgment
    mov r0, #0x55
    bl uart_putc
    
    // Jump to downloaded code
    bx r2

// UART initialization
uart_init:
    // Nothing to initialize in this simple version
    mov pc, lr

// Send character over UART
uart_putc:
    push {r1, lr}
1:  ldr r1, =UART_BASE
    ldr r1, [r1, #UART_STATUS]
    tst r1, #UART_TX_READY
    beq 1b
    ldr r1, =UART_BASE
    str r0, [r1, #UART_DATA]
    pop {r1, pc}

// Receive character from UART
uart_getc:
    push {r1, lr}
1:  ldr r1, =UART_BASE
    ldr r1, [r1, #UART_STATUS]
    tst r1, #UART_RX_READY
    beq 1b
    ldr r1, =UART_BASE
    ldr r0, [r1, #UART_DATA]
    pop {r1, pc}

// Send string over UART
uart_puts:
    push {r0, r1, lr}
1:  ldrb r1, [r0], #1
    cmp r1, #0
    beq 2f
    mov r0, r1
    bl uart_putc
    b 1b
2:  pop {r0, r1, pc}

// Data section
.section .rodata
welcome_msg:
    .asciz "ARM7 BootROM v1.0\r\nWaiting for download...\r\n" 