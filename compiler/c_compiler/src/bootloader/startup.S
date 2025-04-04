.section .text

.global _start

_start:
    /* Set up stack pointer */
    ldr r0, =_stack_top
    mov sp, r0
    
    /* Clear BSS section */
    ldr r0, =_bss_start
    ldr r1, =_bss_end
    mov r2, #0
    
1:
    cmp r0, r1
    beq 2f
    str r2, [r0], #4
    b 1b
    
2:
    /* Copy data section from flash to RAM */
    ldr r0, =_data_start
    ldr r1, =_data_end
    ldr r2, =_data_load_addr
    
1:
    cmp r0, r1
    beq 2f
    ldr r3, [r2], #4
    str r3, [r0], #4
    b 1b
    
2:
    /* Call C code */
    bl bootloader_main
    
    /* We should never return */
1:
    b 1b

/* Data load address (in flash) */
.data_load_addr:
    .word _data_start 