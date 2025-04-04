import os
import pytest
from pathlib import Path
from ..src.main import compile_file
from ..src.linker.elf_linker import ELFLinker

@pytest.mark.skipif(not os.path.exists("/usr/bin/qemu-arm"), 
                   reason="QEMU not installed")
def test_hello_world(tmp_path):
    """Test compiling and running the hello world program."""
    # Get the path to the hello world example
    examples_dir = Path(__file__).parent.parent / "examples"
    hello_c = examples_dir / "hello.c"
    
    # Compile to ELF
    output_elf = tmp_path / "hello.elf"
    compile_file(str(hello_c), str(output_elf), generate_elf=True)
    
    # Run with QEMU
    returncode, stdout, stderr = ELFLinker.run_with_qemu(str(output_elf))
    assert returncode == 0
    assert stdout == "Hello, World!\n"
    assert stderr == "" 