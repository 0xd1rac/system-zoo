.section .text
.global _start

// Constants
.equ UART_BASE, 0x10000000
.equ UART_DATA,  0x0
.equ UART_STATUS, 0x4
.equ UART_TX_READY, 0x2

_start:
    // Send test message
    ldr r0, =test_msg
    bl uart_puts
    
    // Blink LED pattern (if available)
    mov r0, #0x1
    mov r1, #0
blink_loop:
    // Toggle LED
    eor r1, r1, r0
    str r1, [r0, #0x20000000]  // LED register
    
    // Delay
    mov r2, #0x100000
delay_loop:
    subs r2, r2, #1
    bne delay_loop
    
    b blink_loop

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

.section .rodata
test_msg:
    .asciz "Test program running in RAM!\r\n" 