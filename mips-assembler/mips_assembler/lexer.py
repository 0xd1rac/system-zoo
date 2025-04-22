""""
lexer.py
==========

Very small lexer that turns a source string containing MIPS assembly into a stream of *Token*
objects. Each knows its **type**, **text value**, and **line/column** where it starts - information you 
need for good error messages later. 

Typical use
-----------
>>> from mips_assembler.lexer import lex
>>> list(lex("loop: add $t0, $t0, $t1 #demo"))
[Token(type='LABEL',   value='loop:', line=1, col=0),
 Token(type='IDENT',   value='add',  line=1, col=6),
 Token(type='REGISTER',value='$t0',  line=1, col=10),
 Token(type='PUNCT',   value=',',    line=1, col=13),
 Token(type='REGISTER',value='$t0',  line=1, col=15),
 Token(type='PUNCT',   value=',',    line=1, col=18),
 Token(type='REGISTER',value='$t1',  line=1, col=20),
 Token(type='PUNCT',   value='#',    line=1, col=22),
 Token(type='COMMENT', value='demo', line=1, col=23)
 ]
"""

from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Iterator, Iterable


@dataclass(frozen=True)
class Token:
    type: str   #"IDENT", "PUNCT", "COMMENT", "LABEL", "REGISTER", "NUMBER", "STRING"
    value: str  # The literal text of the token
    line: int   # 1-based  line number
    col: int    # 0‑based column number 

# ───────────────────────────── regular expr. ───────────────────────────────
TOKEN_RE = re.compile(
    r"""
    (?P<COMMENT>   \#.*?$               ) |   # whole‑line or tail comment
    (?P<LABEL>     [A-Za-z_]\w* :       ) |   # e.g. "loop:"
    (?P<DIRECTIVE> \.[A-Za-z_]+         ) |   # ".text", ".word"
    (?P<REGISTER>  \$[A-Za-z0-9]+       ) |   # "$t0", "$31", "$ra"
    (?P<IMM>       -?(?:0x[0-9A-Fa-f]+|\d+)) |# decimal or hex immediates
    (?P<IDENT>     [A-Za-z_]\w*         ) |   # mnemonics, identifiers
    (?P<PUNCT>     [,() ]               ) |   # commas, parens, *single* space
    (?P<WS>        \s+                  )     # any other whitespace
    """,
re.VERBOSE | re.MULTILINE,
)

# Token types we silently discard (they're not needed by later stages)
_SKIP = {"WS", "COMMENT"}

# ─────────────────────────── lexer ───────────────────────────────────────
class Lexer:
    """
    Stateful iterator –  feed it a *source string*, iterate to get *Token*s.
    """
    
    def __init__(self, src: str):
        self._src = src 

    # ------------------------------------------------------------------ #
    # The heavy lifting – runs the regex and translates absolute offsets
    # into human‑friendly line/col pairs.
    # ------------------------------------------------------------------ #
    def __iter__(self) -> Iterator[Token]:
        # Pre-cpmputer start-of-line positons so we can map an absoluste
        # index 0> (line, col) in O(log N) using binary search 

        line_starts: list[int] = [-1]
        for i, ch in enumerate(self._src):
            if ch == "\n":
                line_starts.append(i)
        line_starts.append(len(self._src))   # sentinel “newline after file”
        
        import bisect 
        for m in TOKEN_RE.finditer(self._src):
            typ = m.lastgroup
            if typ in _SKIP:
                continue
            
            pos = m.start()

            # find rightmost newline *before* pos -> index in line_starts
            line_idx = bisect.bisect_right(line_starts, pos) - 1
            line_no = line_idx + 1  # 1-based line number
            col_no = pos - line_starts[line_idx] - 1  # 0-based column number

            yield Token(typ, m.group(typ), line_no, col_no)
        


# Convenience wrapper so callers don’t need to instantiate Lexer by hand
def lex(src: str | Iterable[str]) -> Iterator[Token]:
    """
    Lex *src* (str **or** iterable of lines) and yield Token objects.

    Example
    -------
    >>> code = ["add $t0,$t1,$t2", "j loop"]
    >>> for tok in lex(code):
    ...     print(tok)
    Token(type='IDENT', value='add', line=1, col=0)
    ...
    """
    if not isinstance(src, str):
        src = "".join(src)

    return iter(Lexer(src))