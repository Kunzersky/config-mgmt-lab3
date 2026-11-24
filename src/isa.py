"""Intermediate representation and ISA metadata."""

from dataclasses import dataclass

from src.constants import (
    ADD_SIZE,
    FIELD_A_OFFSET,
    FIELD_A_WIDTH,
    FIELD_ADD_D_OFFSET,
    FIELD_ADD_D_WIDTH,
    FIELD_B_OFFSET,
    FIELD_B_WIDTH,
    FIELD_C8_OFFSET,
    FIELD_C8_WIDTH,
    FIELD_C_OFFSET,
    FIELD_C_WIDTH,
    FIELD_D_OFFSET,
    FIELD_D_WIDTH,
    LOAD_CONST_SIZE,
    LOAD_MEM_SIZE,
    OP_ADD,
    OP_LOAD_CONST,
    OP_LOAD_MEM,
    OP_STORE_MEM,
    STORE_MEM_SIZE,
)


@dataclass(frozen=True)
class Instruction:
    """A single decoded or assembled instruction."""

    mnemonic: str
    operands: tuple[int, ...]
    line: int = 0


OP_SIZES = {
    OP_LOAD_CONST: LOAD_CONST_SIZE,
    OP_LOAD_MEM: LOAD_MEM_SIZE,
    OP_STORE_MEM: STORE_MEM_SIZE,
    OP_ADD: ADD_SIZE,
}

MNEMONIC_CODES = {
    "LOAD_CONST": OP_LOAD_CONST,
    "LOAD_MEM": OP_LOAD_MEM,
    "STORE_MEM": OP_STORE_MEM,
    "ADD": OP_ADD,
}

OPERAND_COUNTS = {
    "LOAD_CONST": 2,
    "LOAD_MEM": 3,
    "STORE_MEM": 2,
    "ADD": 3,
}

OPERAND_WIDTHS = {
    "LOAD_CONST": (32, 32),
    "LOAD_MEM": (32, 8, 32),
    "STORE_MEM": (32, 32),
    "ADD": (32, 32, 32),
}

FIELD_LAYOUTS = {
    "LOAD_CONST": (
        (FIELD_B_OFFSET, FIELD_B_WIDTH),
        (FIELD_C_OFFSET, FIELD_C_WIDTH),
    ),
    "LOAD_MEM": (
        (FIELD_B_OFFSET, FIELD_B_WIDTH),
        (FIELD_C8_OFFSET, FIELD_C8_WIDTH),
        (FIELD_D_OFFSET, FIELD_D_WIDTH),
    ),
    "STORE_MEM": (
        (FIELD_B_OFFSET, FIELD_B_WIDTH),
        (FIELD_C_OFFSET, FIELD_C_WIDTH),
    ),
    "ADD": (
        (FIELD_B_OFFSET, FIELD_B_WIDTH),
        (FIELD_C_OFFSET, FIELD_C_WIDTH),
        (FIELD_ADD_D_OFFSET, FIELD_ADD_D_WIDTH),
    ),
}

OPCODE_LAYOUT = (FIELD_A_OFFSET, FIELD_A_WIDTH)
