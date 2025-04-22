"""
Lightweight loader that exposes:

    * `INSTR`     - dict  mnemonic → spec
    * `DIRECTIVE` - dict  name     → spec/description
    * `REG`       - dict  register name/alias → int (0‑31)

Access helpers
--------------
>>> from mips_assembler.isa import INSTR, REG
>>> INSTR['add']['opcode'], REG['$t0']
(0, 8)
"""
from pathlib import Path 
import yaml

HERE = Path(__file__).with_suffix('')  # directory of this file

def _load_yaml(fname:str) -> dict:
    with (HERE / fname).open('r') as f:
        return yaml.safe_load(f)

INSTR = _load_yaml('instructions.yaml')
DIRECTIVE = _load_yaml('directives.yaml')

from .registers import REG, name_to_num, num_to_name

