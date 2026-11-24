"""Machine-code encoder and decoder."""

from src.isa import (
    FIELD_LAYOUTS,
    MNEMONIC_CODES,
    OPCODE_LAYOUT,
    OP_SIZES,
    OPERAND_COUNTS,
    Instruction,
)


def encode_instruction(instruction: Instruction) -> bytes:
    """Encode one IR instruction as little-endian bytes.

    Args:
        instruction: Parsed instruction to encode.

    Returns:
        The encoded instruction bytes.

    Raises:
        ValueError: If operand count or value does not fit the ISA field.
    """
    mnemonic = instruction.mnemonic
    expected = OPERAND_COUNTS.get(mnemonic)
    if expected is None or len(instruction.operands) != expected:
        raise ValueError(f"invalid instruction: {mnemonic}")
    opcode = MNEMONIC_CODES[mnemonic]
    bit_value = _insert_field(0, opcode, OPCODE_LAYOUT)
    for operand, layout in zip(instruction.operands, FIELD_LAYOUTS[mnemonic]):
        bit_value = _insert_field(bit_value, operand, layout)
    return bit_value.to_bytes(OP_SIZES[opcode], byteorder="little")


def encode_program(instructions: list[Instruction]) -> bytes:
    """Encode instructions in source order.

    Args:
        instructions: Instructions to encode.

    Returns:
        Concatenated machine-code bytes.
    """
    return b"".join(encode_instruction(item) for item in instructions)


def _insert_field(
    bit_value: int,
    value: int,
    layout: tuple[int, int],
) -> int:
    offset, width = layout
    if value < 0 or value >= 1 << width:
        raise ValueError(f"value {value} does not fit in {width} bits")
    return bit_value | value << offset
