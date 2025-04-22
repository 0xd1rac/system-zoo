"""
Unit tests for mips_assembler.lexer 

Run with:
    pytest -q tests/test_lexer.py

"""
import pytest
from mips_assembler.lexer import lex

# ────────────────────────── helpers ────────────────────────────
def toks(src: str):
    """Return a list of Token objects for easier assertions."""
    return list(lex(src))


def ttypes(src: str):
    """Return just the token.type sequence (handy in many checks)."""
    return [t.type for t in toks(src)]

# ────────────────────────── test cases ─────────────────────────
def test_simple_instructions():
    """Test simple MIPS instructions."""
    src = "add $t0,$t1,$t2"
    tokens = toks(src)

     # type and value sequences are predictable
    assert [t.type for t in tokens] == [
        "IDENT",    # add
        "REGISTER", # $t0
        "PUNCT",    # ,
        "REGISTER", # $t1
        "PUNCT",    # ,
        "REGISTER", #$t2
        ]

    assert [t.value for t in tokens] == [
        "add", 
        "$t0", 
        ",", 
        "$t1", 
        ",", 
        "$t2"
        ]

    # first two column positions (0-based)
    