"""Tests for assembly parsing."""

import pytest

from src.assembler import assemble


@pytest.mark.parametrize(
    ("source", "mnemonic", "operands"),
    [
        ("LOAD_CONST 464, 765", "LOAD_CONST", (464, 765)),
        ("LOAD_MEM 467, 231, 482", "LOAD_MEM", (467, 231, 482)),
        ("STORE_MEM 876, 705", "STORE_MEM", (876, 705)),
        ("ADD 348, 31, 278", "ADD", (348, 31, 278)),
    ],
)
def test_specification_instruction_parses(
    source: str,
    mnemonic: str,
    operands: tuple[int, ...],
) -> None:
    """Parse each instruction from the specification test vectors."""
    instruction = assemble(source)[0]
    assert instruction.mnemonic == mnemonic
    assert instruction.operands == operands


def test_assembler_ignores_comments_and_accepts_hexadecimal() -> None:
    """Ignore comments and parse integer literals in hexadecimal."""
    instructions = assemble("# header\nLOAD_CONST 0x1d0, 0x2fd # value\n")
    assert len(instructions) == 1
    assert instructions[0].operands == (464, 765)


@pytest.mark.parametrize(
    "source",
    [
        "UNKNOWN 1, 2",
        "ADD 1, 2",
        "LOAD_MEM 1, 256, 3",
        "LOAD_CONST -1, 2",
        "LOAD_CONST first, 2",
    ],
)
def test_assembler_rejects_invalid_instructions(source: str) -> None:
    """Reject unknown commands, malformed operands, and invalid widths."""
    with pytest.raises(ValueError):
        assemble(source)
