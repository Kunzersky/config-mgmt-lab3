"""Machine-code encoder and decoder."""

from src.isa import (
    FIELD_LAYOUTS,
    MNEMONIC_CODES,
    OPCODE_MNEMONICS,
    OPCODE_LAYOUT,
    OP_SIZES,
    OPERAND_COUNTS,
    Instruction,
)
from src.constants import MIN_UNSIGNED, ONE, OPCODE_MASK


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
    if value < MIN_UNSIGNED or value >= ONE << width:
        raise ValueError(f"value {value} does not fit in {width} bits")
    return bit_value | value << offset


def decode_instruction(
    code_mem: bytes,
    offset: int,
) -> tuple[Instruction, int]:
    """Decode one instruction from code memory.

    Args:
        code_mem: Machine-code bytes.
        offset: Byte offset of the next instruction.

    Returns:
        The decoded instruction and the offset after it.

    Raises:
        ValueError: If the opcode or instruction length is invalid.
    """
    if offset < MIN_UNSIGNED or offset >= len(code_mem):
        raise ValueError(f"invalid instruction offset: {offset}")
    opcode = code_mem[offset] & OPCODE_MASK
    size = OP_SIZES.get(opcode)
    if size is None:
        raise ValueError(f"unknown opcode {opcode} at offset {offset}")
    next_offset = offset + size
    if next_offset > len(code_mem):
        raise ValueError(f"truncated instruction at offset {offset}")
    bit_value = int.from_bytes(code_mem[offset:next_offset], "little")
    mnemonic = OPCODE_MNEMONICS[opcode]
    operands = tuple(
        _extract_field(bit_value, layout)
        for layout in FIELD_LAYOUTS[mnemonic]
    )
    return Instruction(mnemonic, operands), next_offset


def _extract_field(bit_value: int, layout: tuple[int, int]) -> int:
    offset, width = layout
    return bit_value >> offset & ((1 << width) - 1)
