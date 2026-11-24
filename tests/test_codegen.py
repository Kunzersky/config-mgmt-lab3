"""Tests for little-endian instruction encoding."""

import pytest

from src.assembler import assemble
from src.cli import main
from src.codegen import encode_instruction, encode_program
from src.isa import Instruction

SPECIFICATION_BYTES = [
    bytes.fromhex("12 3a 00 00 a0 5f 00 00 00"),
    bytes.fromhex("69 3a 00 00 e0 5c 3c 00 00 00"),
    bytes.fromhex("8a 6d 00 00 20 58 00 00 00"),
    bytes.fromhex("8d 2b 00 00 e0 03 00 00 c0 22 00 00 00"),
]
SPECIFICATION_SOURCE = [
    "LOAD_CONST 464, 765",
    "LOAD_MEM 467, 231, 482",
    "STORE_MEM 876, 705",
    "ADD 348, 31, 278",
]


@pytest.mark.parametrize(
    ("source", "expected"),
    list(zip(SPECIFICATION_SOURCE, SPECIFICATION_BYTES)),
)
def test_encoding_matches_specification(
    source: str,
    expected: bytes,
) -> None:
    """Encode the four machine-code examples from the specification."""
    assert encode_instruction(assemble(source)[0]) == expected


def test_program_encoding_concatenates_variable_length_instructions() -> None:
    """Keep instructions in source order without padding."""
    instructions = assemble("\n".join(SPECIFICATION_SOURCE))
    expected = b"".join(SPECIFICATION_BYTES)
    assert encode_program(instructions) == expected


def test_encoder_rejects_values_outside_their_fields() -> None:
    """Reject invalid IR instead of truncating field bits."""
    invalid = Instruction("LOAD_MEM", (1, 256, 2))
    with pytest.raises(ValueError, match="does not fit"):
        encode_instruction(invalid)


def test_assembler_cli_writes_binary_and_reports_count(
    tmp_path,
    capsys,
) -> None:
    """Write the encoded file and report the instruction count."""
    source_path = tmp_path / "program.asm"
    output_path = tmp_path / "program.bin"
    source_path.write_text(SPECIFICATION_SOURCE[0], encoding="utf-8")
    result = main(
        [
            "asm",
            "--input",
            str(source_path),
            "--output",
            str(output_path),
        ]
    )
    assert result == 0
    assert output_path.read_bytes() == SPECIFICATION_BYTES[0]
    assert "Assembled 1 instructions" in capsys.readouterr().out


def test_assembler_cli_test_mode_prints_fields_and_bytes(
    tmp_path,
    capsys,
) -> None:
    """Print the decoded fields and byte sequence in diagnostic mode."""
    source_path = tmp_path / "program.asm"
    source_path.write_text(SPECIFICATION_SOURCE[0], encoding="utf-8")
    result = main(["asm", "--input", str(source_path), "--test"])
    output = capsys.readouterr().out
    assert result == 0
    assert "A=18, B=464, C=765" in output
    assert "12 3a 00 00 a0 5f 00 00 00" in output
