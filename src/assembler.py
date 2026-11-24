"""Text assembler for the educational virtual machine."""

from src.constants import (
    INSTRUCTION_PART_COUNT,
    MIN_UNSIGNED,
    ONE,
    OPERAND_TEXT_INDEX,
)
from src.isa import Instruction, MNEMONIC_CODES, OPERAND_COUNTS, OPERAND_WIDTHS


def assemble(source: str) -> list[Instruction]:
    """Parse assembly text into an instruction list.

    Args:
        source: Assembly program text.

    Returns:
        Parsed instructions in source order.

    Raises:
        ValueError: If an instruction or operand is invalid.
    """
    instructions = []
    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        instruction = _parse_line(raw_line, line_number)
        if instruction is not None:
            instructions.append(instruction)
    return instructions


def _parse_line(raw_line: str, line_number: int) -> Instruction | None:
    content = raw_line.split("#", maxsplit=1)[0].strip()
    if not content:
        return None
    parts = content.split(maxsplit=1)
    mnemonic = parts[0]
    if mnemonic not in MNEMONIC_CODES:
        raise ValueError(f"line {line_number}: unknown mnemonic {mnemonic!r}")
    operand_text = (
        parts[OPERAND_TEXT_INDEX]
        if len(parts) == INSTRUCTION_PART_COUNT
        else ""
    )
    operands = _parse_operands(operand_text, mnemonic, line_number)
    _validate_operands(operands, mnemonic, line_number)
    return Instruction(mnemonic, tuple(operands), line_number)


def _parse_operands(
    operand_text: str,
    mnemonic: str,
    line_number: int,
) -> list[int]:
    pieces = [piece.strip() for piece in operand_text.split(",")]
    if not operand_text:
        pieces = []
    expected = OPERAND_COUNTS[mnemonic]
    if len(pieces) != expected or any(not piece for piece in pieces):
        raise ValueError(
            f"line {line_number}: {mnemonic} expects {expected} operands"
        )
    try:
        return [int(piece, 0) for piece in pieces]
    except ValueError as error:
        raise ValueError(
            f"line {line_number}: operands must be integer literals"
        ) from error


def _validate_operands(
    operands: list[int],
    mnemonic: str,
    line_number: int,
) -> None:
    widths = OPERAND_WIDTHS[mnemonic]
    for index, (value, width) in enumerate(zip(operands, widths), start=1):
        if value < MIN_UNSIGNED or value >= ONE << width:
            raise ValueError(
                f"line {line_number}: operand {index} must fit in {width} bits"
            )
