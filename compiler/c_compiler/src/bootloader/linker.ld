/* Linker script for the bootloader */

MEMORY
{
    /* Bootloader starts at 0x0 */
    FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 64K
    /* RAM starts at 0x10000 */
    RAM (rwx) : ORIGIN = 0x00010000, LENGTH = 64K
}

SECTIONS
{
    /* Code and read-only data */
    .text :
    {
        *(.text)
        *(.rodata)
        *(.rodata.*)
        . = ALIGN(4);
    } > FLASH

    /* Initialized data */
    .data :
    {
        _data_start = .;
        *(.data)
        *(.data.*)
        . = ALIGN(4);
        _data_end = .;
    } > RAM AT > FLASH

    /* Uninitialized data */
    .bss :
    {
        _bss_start = .;
        *(.bss)
        *(.bss.*)
        *(COMMON)
        . = ALIGN(4);
        _bss_end = .;
    } > RAM

    /* Stack */
    .stack :
    {
        _stack_start = .;
        . = . + 4K;
        . = ALIGN(4);
        _stack_end = .;
    } > RAM

    /* Discard everything else */
    /DISCARD/ :
    {
        *(.comment)
        *(.eh_frame)
        *(.eh_frame_hdr)
        *(.note.gnu.build-id)
    }
}

/* Symbols for startup code */
PROVIDE(_start = 0x0);
PROVIDE(_stack_top = _stack_end); 