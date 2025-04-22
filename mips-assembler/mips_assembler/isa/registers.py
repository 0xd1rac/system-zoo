
"""Canonical register table & convenience helpers."""

# Ordered tuples so both index and name mapping are easy to see/read

_REG_BARE = (
    "$zero", "$at",
    "$v0", "$v1",
    "$a0", "$a1", "$a2", "$a3",
    "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7",
    "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
    "$t8", "$t9",
    "$k0", "$k1",
    "$gp", "$sp", "$fp", "$ra",
)


# Add numeric aliases ($0 … $31) and *human aliases* (e.g. r0)
_REG_EXTRA = {f"${i}": i for i in range(32)}
_REG_EXTRA.update({f"r{i}": i for i in range(32)})

REG: dict[str,int] = {name: i for i, name in enumerate(_REG_BARE)}
REG.update(_REG_EXTRA)


def name_to_num(name:str) -> int:
    """Return integer index for `$t0` / `$15` / `r31`. Raises KeyError if bad."""
    return REG[name.lower()]

def num_to_name(num:int) -> str:
    """Return *canonical* name (e.g. 8 → `$t0`)."""
    if not 0 <= num < 32:
        raise ValueError(f"Invalid register number: {num}. Register number must be 0-31")
    return _REG_BARE[num]


