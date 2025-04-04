import os
import struct
import subprocess
from typing import List, Dict, Optional, Tuple, BinaryIO

class ELFLinker:
    """
    A simple ELF linker for ARM architecture that generates executables
    compatible with QEMU semihosting.
    """
    
    # ELF file format constants
    EI_NIDENT = 16
    EI_CLASS = 4
    EI_DATA = 5
    EI_VERSION = 6
    EI_OSABI = 7
    EI_ABIVERSION = 8
    
    # ELF class
    ELFCLASS32 = 1
    
    # ELF data encoding
    ELFDATA2LSB = 1
    
    # ELF file type
    ET_EXEC = 2
    
    # ELF machine type
    EM_ARM = 40
    
    # ELF version
    EV_CURRENT = 1
    
    # ELF OS ABI
    ELFOSABI_SYSV = 0
    
    # Section flags
    SHF_ALLOC = 0x2
    SHF_EXECINSTR = 0x4
    SHF_WRITE = 0x1
    
    # Section types
    SHT_PROGBITS = 0x1
    SHT_SYMTAB = 0x2
    SHT_STRTAB = 0x3
    SHT_RELA = 0x4
    SHT_NOBITS = 0x8
    
    # Symbol binding
    STB_GLOBAL = 1
    
    # Symbol type
    STT_FUNC = 2
    STT_OBJECT = 1
    
    # Relocation types
    R_ARM_ABS32 = 2
    R_ARM_CALL = 28
    R_ARM_JUMP24 = 29
    
    def __init__(self):
        self.sections: Dict[str, bytes] = {}
        self.section_headers: List[Dict] = []
        self.symbols: List[Dict] = []
        self.relocations: List[Dict] = []
        self.string_table: bytes = b"\0"
        self.string_table_map: Dict[str, int] = {"": 0}
        self.symbol_table_map: Dict[str, int] = {}
        
        # Add standard sections
        self.add_section(".shstrtab", b"")
        self.add_section(".symtab", b"")
        self.add_section(".strtab", b"")
        self.add_section(".text", b"")
        self.add_section(".data", b"")
        self.add_section(".bss", b"")
        self.add_section(".rel.text", b"")
        
        # Add standard symbols
        self.add_symbol("", 0, 0, 0, 0, 0)  # Null symbol
        self.add_symbol("_start", 0, 0, STB_GLOBAL, STT_FUNC, 1)  # _start symbol
    
    def add_string_to_table(self, string: str) -> int:
        """Add a string to the string table and return its offset."""
        if string in self.string_table_map:
            return self.string_table_map[string]
        
        offset = len(self.string_table)
        self.string_table += string.encode('utf-8') + b"\0"
        self.string_table_map[string] = offset
        return offset
    
    def add_symbol(self, name: str, value: int, size: int, binding: int, type: int, section_idx: int) -> int:
        """Add a symbol to the symbol table and return its index."""
        name_idx = self.add_string_to_table(name)
        symbol = {
            "name": name_idx,
            "value": value,
            "size": size,
            "info": (binding << 4) | type,
            "other": 0,
            "shndx": section_idx
        }
        self.symbols.append(symbol)
        symbol_idx = len(self.symbols) - 1
        self.symbol_table_map[name] = symbol_idx
        return symbol_idx
    
    def add_section(self, name: str, data: bytes, 
                   section_type: int = SHT_PROGBITS,
                   flags: int = SHF_ALLOC) -> int:
        """Add a section and return its index."""
        name_idx = self.add_string_to_table(name)
        section = {
            "name": name_idx,
            "type": section_type,
            "flags": flags,
            "addr": 0,  # Will be filled in during layout
            "offset": 0,  # Will be filled in during layout
            "size": len(data),
            "link": 0,
            "info": 0,
            "addralign": 0,
            "entsize": 0
        }
        self.section_headers.append(section)
        self.sections[name] = data
        return len(self.section_headers) - 1
    
    def add_relocation(self, section: str, offset: int, symbol: str, 
                      addend: int, type: int) -> None:
        """Add a relocation entry."""
        symbol_idx = self.symbol_table_map.get(symbol, 0)
        relocation = {
            "offset": offset,
            "info": (symbol_idx << 8) | type,
            "addend": addend
        }
        self.relocations.append(relocation)
    
    def layout_sections(self) -> None:
        """Layout sections in memory and file."""
        # Start at 0x10000 for text section
        text_addr = 0x10000
        data_addr = 0x20000
        bss_addr = 0x30000
        
        # Update section addresses and offsets
        file_offset = 0x34 + len(self.section_headers) * 0x28  # Header size + section headers
        
        for i, section in enumerate(self.section_headers):
            name = list(self.string_table_map.keys())[list(self.string_table_map.values()).index(section["name"])]
            
            if name == ".text":
                section["addr"] = text_addr
                section["offset"] = file_offset
                file_offset += section["size"]
            elif name == ".data":
                section["addr"] = data_addr
                section["offset"] = file_offset
                file_offset += section["size"]
            elif name == ".bss":
                section["addr"] = bss_addr
                section["offset"] = file_offset
                file_offset += section["size"]
            elif name == ".shstrtab":
                section["offset"] = file_offset
                file_offset += section["size"]
            elif name == ".symtab":
                section["link"] = self.section_headers.index(next(s for s in self.section_headers 
                    if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".strtab"))
                section["info"] = 1  # First global symbol index
                section["entsize"] = 0x10  # Symbol entry size
                section["offset"] = file_offset
                file_offset += section["size"]
            elif name == ".strtab":
                section["offset"] = file_offset
                file_offset += section["size"]
            elif name == ".rel.text":
                section["link"] = self.section_headers.index(next(s for s in self.section_headers 
                    if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".symtab"))
                section["info"] = self.section_headers.index(next(s for s in self.section_headers 
                    if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".text"))
                section["entsize"] = 0xC  # Relocation entry size
                section["offset"] = file_offset
                file_offset += section["size"]
    
    def write_elf_header(self, f: BinaryIO) -> None:
        """Write the ELF header to the file."""
        # e_ident
        f.write(b"\x7FELF")  # ELF magic
        f.write(struct.pack("<B", self.ELFCLASS32))  # 32-bit
        f.write(struct.pack("<B", self.ELFDATA2LSB))  # Little-endian
        f.write(struct.pack("<B", self.EV_CURRENT))  # Current version
        f.write(struct.pack("<B", self.ELFOSABI_SYSV))  # System V ABI
        f.write(struct.pack("<B", 0))  # ABI version
        f.write(b"\0" * 7)  # Padding
        
        # e_type
        f.write(struct.pack("<H", self.ET_EXEC))
        
        # e_machine
        f.write(struct.pack("<H", self.EM_ARM))
        
        # e_version
        f.write(struct.pack("<I", self.EV_CURRENT))
        
        # e_entry (entry point)
        text_section = next(s for s in self.section_headers 
            if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".text")
        f.write(struct.pack("<I", text_section["addr"]))
        
        # e_phoff (program header offset)
        f.write(struct.pack("<I", 0))  # No program headers
        
        # e_shoff (section header offset)
        f.write(struct.pack("<I", 0x34))  # After ELF header
        
        # e_flags
        f.write(struct.pack("<I", 0))
        
        # e_ehsize (ELF header size)
        f.write(struct.pack("<H", 0x34))
        
        # e_phentsize (program header entry size)
        f.write(struct.pack("<H", 0))
        
        # e_phnum (number of program headers)
        f.write(struct.pack("<H", 0))
        
        # e_shentsize (section header entry size)
        f.write(struct.pack("<H", 0x28))
        
        # e_shnum (number of section headers)
        f.write(struct.pack("<H", len(self.section_headers)))
        
        # e_shstrndx (section name string table index)
        shstrtab_idx = self.section_headers.index(next(s for s in self.section_headers 
            if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".shstrtab"))
        f.write(struct.pack("<H", shstrtab_idx))
    
    def write_section_headers(self, f: BinaryIO) -> None:
        """Write section headers to the file."""
        for section in self.section_headers:
            f.write(struct.pack("<I", section["name"]))
            f.write(struct.pack("<I", section["type"]))
            f.write(struct.pack("<I", section["flags"]))
            f.write(struct.pack("<I", section["addr"]))
            f.write(struct.pack("<I", section["offset"]))
            f.write(struct.pack("<I", section["size"]))
            f.write(struct.pack("<I", section["link"]))
            f.write(struct.pack("<I", section["info"]))
            f.write(struct.pack("<I", section["addralign"]))
            f.write(struct.pack("<I", section["entsize"]))
    
    def write_sections(self, f: BinaryIO) -> None:
        """Write section data to the file."""
        for section in self.section_headers:
            name = list(self.string_table_map.keys())[list(self.string_table_map.values()).index(section["name"])]
            if name in self.sections:
                f.seek(section["offset"])
                f.write(self.sections[name])
    
    def write_symbol_table(self, f: BinaryIO) -> None:
        """Write symbol table to the file."""
        symtab_section = next(s for s in self.section_headers 
            if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".symtab")
        f.seek(symtab_section["offset"])
        
        for symbol in self.symbols:
            f.write(struct.pack("<I", symbol["name"]))
            f.write(struct.pack("<I", symbol["value"]))
            f.write(struct.pack("<I", symbol["size"]))
            f.write(struct.pack("<B", symbol["info"]))
            f.write(struct.pack("<B", symbol["other"]))
            f.write(struct.pack("<H", symbol["shndx"]))
    
    def write_string_table(self, f: BinaryIO) -> None:
        """Write string table to the file."""
        strtab_section = next(s for s in self.section_headers 
            if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".strtab")
        f.seek(strtab_section["offset"])
        f.write(self.string_table)
    
    def write_relocations(self, f: BinaryIO) -> None:
        """Write relocation entries to the file."""
        rel_section = next(s for s in self.section_headers 
            if list(self.string_table_map.keys())[list(self.string_table_map.values()).index(s["name"])] == ".rel.text")
        f.seek(rel_section["offset"])
        
        for reloc in self.relocations:
            f.write(struct.pack("<I", reloc["offset"]))
            f.write(struct.pack("<I", reloc["info"]))
            f.write(struct.pack("<i", reloc["addend"]))
    
    def write_elf(self, output_file: str) -> None:
        """Write the complete ELF file."""
        self.layout_sections()
        
        with open(output_file, 'wb') as f:
            self.write_elf_header(f)
            self.write_section_headers(f)
            self.write_sections(f)
            self.write_symbol_table(f)
            self.write_string_table(f)
            self.write_relocations(f)
    
    def add_assembly(self, assembly_code: str) -> None:
        """Add ARM assembly code to the text section."""
        # This is a simplified version - in a real implementation,
        # you would parse the assembly and convert it to machine code
        # For now, we'll just add a placeholder
        self.sections[".text"] = b"\x00\x00\xa0\xe3"  # mov r0, #0 (return 0)
    
    def add_semihosting_exit(self) -> None:
        """Add semihosting exit call to the text section."""
        # ARM semihosting exit call
        # mov r0, #0 (return code 0)
        # mov r7, #1 (SYS_EXIT)
        # svc 0x123456 (semihosting call)
        self.sections[".text"] = (
            b"\x00\x00\xa0\xe3"  # mov r0, #0
            b"\x01\x70\xa0\xe3"  # mov r7, #1
            b"\x00\x00\x00\xef"  # svc 0x0
        )
    
    def add_semihosting_write(self, string: str) -> None:
        """Add semihosting write call to print a string."""
        # Add string to data section
        string_addr = len(self.sections[".data"])
        self.sections[".data"] += string.encode('utf-8') + b"\0"
        
        # Add write syscall to text section
        # mov r0, #1 (stdout)
        # ldr r1, =string_addr
        # mov r2, #len(string)
        # mov r7, #4 (SYS_WRITE)
        # svc 0x123456 (semihosting call)
        self.sections[".text"] += (
            b"\x01\x00\xa0\xe3"  # mov r0, #1
            b"\x00\x10\x90\xe5"  # ldr r1, [r0, #string_addr]
            b"\x" + format(len(string), 'x').zfill(2) + b"\x20\xa0\xe3"  # mov r2, #len(string)
            b"\x04\x70\xa0\xe3"  # mov r7, #4
            b"\x00\x00\x00\xef"  # svc 0x0
        )
    
    @staticmethod
    def run_with_qemu(elf_file: str) -> Tuple[int, str, str]:
        """Run the ELF file with QEMU using semihosting."""
        try:
            result = subprocess.run(
                ["qemu-arm", "-L", "/usr/arm-linux-gnueabi", elf_file],
                capture_output=True,
                text=True,
                check=True
            )
            return 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except FileNotFoundError:
            return -1, "", "QEMU not found. Please install QEMU with ARM support." 