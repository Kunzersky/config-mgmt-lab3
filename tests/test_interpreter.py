"""Tests for virtual-machine memory and execution."""

import csv
from pathlib import Path

import pytest

from src.assembler import assemble
from src.codegen import encode_program
from src.interpreter import Interpreter
from src.memory import Memory

PROJECT_ROOT = Path(__file__).parents[1]


def _run_source(source: str) -> tuple[Memory, int]:
    memory = Memory(code_mem=encode_program(assemble(source)))
    count = Interpreter(memory).run()
    return memory, count


def test_copy_array_example_round_trips_ten_values() -> None:
    """Copy a ten-word array into a separate data-memory range."""
    source = (PROJECT_ROOT / "examples/copy_array.asm").read_text(
        encoding="utf-8"
    )
    memory, count = _run_source(source)
    expected = [17, 28, 39, 40, 51, 62, 73, 84, 95, 106]
    assert count == 21
    assert [memory.read_data(300 + index) for index in range(10)] == expected


def test_memory_operations_and_separate_code_memory() -> None:
    """Execute indirect load/store without modifying instruction bytes."""
    source = "\n".join(
        [
            "LOAD_CONST 10, 400",
            "LOAD_CONST 99, 123",
            "STORE_MEM 10, 99",
            "LOAD_MEM 10, 0, 20",
        ]
    )
    memory, count = _run_source(source)
    assert count == 4
    assert memory.read_data(400) == 123
    assert memory.read_data(20) == 123
    assert memory.code_mem == encode_program(assemble(source))


def test_csv_dump_supports_address_range(tmp_path) -> None:
    """Dump the requested half-open data-memory interval in CSV."""
    memory = Memory()
    memory.write_data(4, 255)
    memory.write_data(5, 256)
    output = tmp_path / "memory.csv"
    memory.dump_csv(output, (4, 6))
    with output.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))
    assert rows == [
        ["addr", "value_hex", "value_dec"],
        ["4", "0x000000ff", "255"],
        ["5", "0x00000100", "256"],
    ]


def test_csv_dump_without_range_omits_zero_cells(tmp_path) -> None:
    """Dump initialized nonzero cells by default."""
    memory = Memory()
    memory.write_data(8, 0)
    memory.write_data(9, 1)
    output = tmp_path / "memory.csv"
    memory.dump_csv(output)
    assert "9,0x00000001,1" in output.read_text(encoding="utf-8")
    assert "8," not in output.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "code",
    [b"\xff", bytes.fromhex("12 3a")],
)
def test_interpreter_rejects_unknown_or_truncated_code(code: bytes) -> None:
    """Report malformed machine code instead of silently stopping."""
    with pytest.raises(ValueError):
        Interpreter(Memory(code_mem=code)).run()
