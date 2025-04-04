import os
import pytest
from pathlib import Path
from ..src.linker.elf_linker import ELFLinker

def test_elf_linker_initialization():
    """Test that the ELF linker initializes correctly with standard sections."""
    linker = ELFLinker()
    
    # Check that standard sections are created
    assert ".text" in linker.sections
    assert ".data" in linker.sections
    assert ".bss" in linker.sections
    assert ".symtab" in linker.sections
    assert ".strtab" in linker.sections
    assert ".shstrtab" in linker.sections
    assert ".rel.text" in linker.sections
    
    # Check that standard symbols are created
    assert "" in linker.symbol_table_map  # Null symbol
    assert "_start" in linker.symbol_table_map

def test_add_string_to_table():
    """Test adding strings to the string table."""
    linker = ELFLinker()
    
    # Add a string and get its offset
    offset1 = linker.add_string_to_table("test_string")
    assert offset1 > 0
    
    # Add the same string again and verify we get the same offset
    offset2 = linker.add_string_to_table("test_string")
    assert offset1 == offset2
    
    # Add a different string and verify we get a different offset
    offset3 = linker.add_string_to_table("another_string")
    assert offset3 > offset1

def test_add_symbol():
    """Test adding symbols to the symbol table."""
    linker = ELFLinker()
    
    # Add a symbol and get its index
    symbol_idx = linker.add_symbol("test_symbol", 0x1000, 0x100, 
                                 linker.STB_GLOBAL, linker.STT_FUNC, 1)
    assert symbol_idx > 0
    
    # Verify the symbol was added correctly
    symbol = linker.symbols[symbol_idx]
    assert symbol["name"] > 0  # Should have a valid string table offset
    assert symbol["value"] == 0x1000
    assert symbol["size"] == 0x100
    assert symbol["info"] == (linker.STB_GLOBAL << 4) | linker.STT_FUNC
    assert symbol["shndx"] == 1

def test_add_section():
    """Test adding sections to the ELF file."""
    linker = ELFLinker()
    
    # Add a new section
    section_idx = linker.add_section(".test", b"test data")
    assert section_idx > 0
    
    # Verify the section was added correctly
    assert ".test" in linker.sections
    assert linker.sections[".test"] == b"test data"
    
    # Verify the section header was added
    section = linker.section_headers[section_idx]
    assert section["name"] > 0  # Should have a valid string table offset
    assert section["type"] == linker.SHT_PROGBITS
    assert section["flags"] == linker.SHF_ALLOC
    assert section["size"] == len(b"test data")

def test_add_relocation():
    """Test adding relocation entries."""
    linker = ELFLinker()
    
    # Add a symbol first
    symbol_idx = linker.add_symbol("test_symbol", 0x1000, 0x100, 
                                 linker.STB_GLOBAL, linker.STT_FUNC, 1)
    
    # Add a relocation
    linker.add_relocation(".text", 0x100, "test_symbol", 0, linker.R_ARM_CALL)
    
    # Verify the relocation was added
    assert len(linker.relocations) == 1
    reloc = linker.relocations[0]
    assert reloc["offset"] == 0x100
    assert reloc["info"] == (symbol_idx << 8) | linker.R_ARM_CALL
    assert reloc["addend"] == 0

def test_write_elf(tmp_path):
    """Test writing an ELF file."""
    linker = ELFLinker()
    
    # Add some test data
    linker.add_assembly("mov r0, #0")
    linker.add_semihosting_exit()
    
    # Write the ELF file
    output_file = tmp_path / "test.elf"
    linker.write_elf(str(output_file))
    
    # Verify the file was created
    assert output_file.exists()
    assert output_file.stat().st_size > 0
    
    # Verify the file starts with ELF magic
    with open(output_file, 'rb') as f:
        magic = f.read(4)
        assert magic == b"\x7FELF"

def test_semihosting_write():
    """Test adding semihosting write calls."""
    linker = ELFLinker()
    
    # Add a write call
    test_string = "Hello, World!"
    linker.add_semihosting_write(test_string)
    
    # Verify the string was added to the data section
    assert test_string.encode('utf-8') + b"\0" in linker.sections[".data"]
    
    # Verify the write syscall was added to the text section
    assert len(linker.sections[".text"]) > 0

@pytest.mark.skipif(not os.path.exists("/usr/bin/qemu-arm"), 
                   reason="QEMU not installed")
def test_run_with_qemu(tmp_path):
    """Test running an ELF file with QEMU."""
    linker = ELFLinker()
    
    # Create a simple program that just exits
    linker.add_semihosting_exit()
    
    # Write and run the ELF file
    output_file = tmp_path / "test.elf"
    linker.write_elf(str(output_file))
    
    returncode, stdout, stderr = ELFLinker.run_with_qemu(str(output_file))
    assert returncode == 0 