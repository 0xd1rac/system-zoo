MEMORY
{
    BOOTROM (rx) : ORIGIN = 0x00000000, LENGTH = 4K
    RAM (rwx)    : ORIGIN = 0x20000000, LENGTH = 1M
}

SECTIONS
{
    .text.boot : {
        *(.text.boot)
    } > BOOTROM

    .text : {
        *(.text)
    } > BOOTROM

    .rodata : {
        *(.rodata)
    } > BOOTROM

    .data : {
        *(.data)
    } > RAM

    .bss : {
        *(.bss)
    } > RAM
} 