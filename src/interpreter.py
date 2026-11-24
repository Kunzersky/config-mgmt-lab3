"""Interpreter for the educational virtual machine."""

from dataclasses import dataclass
from typing import Callable

from src.codegen import decode_instruction
from src.constants import MIN_UNSIGNED, ONE
from src.isa import Instruction
from src.memory import Memory

InstructionHandler = Callable[[Memory, Instruction], None]


@dataclass
class Interpreter:
    """Execute machine code against a separate data-memory space."""

    memory: Memory

    def run(self) -> int:
        """Execute all code-memory instructions in order.

        Returns:
            Number of instructions executed.
        """
        instruction_pointer = MIN_UNSIGNED
        instruction_count = MIN_UNSIGNED
        while instruction_pointer < len(self.memory.code_mem):
            instruction, instruction_pointer = decode_instruction(
                self.memory.code_mem,
                instruction_pointer,
            )
            execute_instruction(self.memory, instruction)
            instruction_count += ONE
        return instruction_count


def execute_instruction(memory: Memory, instruction: Instruction) -> None:
    """Execute a single memory instruction.

    Args:
        memory: Virtual machine memory.
        instruction: Decoded IR instruction.

    Raises:
        ValueError: If the instruction is not supported by this VM stage.
    """
    handlers: dict[str, InstructionHandler] = {
        "LOAD_CONST": _load_const,
        "LOAD_MEM": _load_mem,
        "STORE_MEM": _store_mem,
    }
    handler = handlers.get(instruction.mnemonic)
    if handler is None:
        raise ValueError(f"unsupported instruction: {instruction.mnemonic}")
    handler(memory, instruction)


def _load_const(memory: Memory, instruction: Instruction) -> None:
    address, value = instruction.operands
    memory.write_data(address, value)


def _load_mem(memory: Memory, instruction: Instruction) -> None:
    base, offset, destination = instruction.operands
    source = memory.read_data(base) + offset
    memory.write_data(destination, memory.read_data(source))


def _store_mem(memory: Memory, instruction: Instruction) -> None:
    base, source = instruction.operands
    destination = memory.read_data(base)
    memory.write_data(destination, memory.read_data(source))
