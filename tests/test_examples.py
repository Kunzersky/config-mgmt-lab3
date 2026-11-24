"""End-to-end tests for vector addition programs."""

import csv
from pathlib import Path

import pytest

from src.cli import main

PROJECT_ROOT = Path(__file__).parents[1]
VECTOR_RESULTS = [
    list(range(129, 139)),
    [
        128,
        255,
        256,
        383,
        384,
        1152,
        65663,
        1000128,
        2147483775,
        4294967295,
    ],
    [
        428,
        378,
        128,
        170,
        65664,
        1000000128,
        123456917,
        2147483128,
        4000000128,
        127,
    ],
]


@pytest.mark.parametrize(
    ("example_number", "expected"),
    list(enumerate(VECTOR_RESULTS, start=1)),
)
def test_vector_addition_cli_dump(
    example_number: int,
    expected: list[int],
    tmp_path: Path,
) -> None:
    """Assemble, execute, and verify all ten CSV result cells."""
    source = PROJECT_ROOT / f"examples/vector_add_{example_number}.asm"
    machine_code = tmp_path / "vector.bin"
    dump = tmp_path / "vector.csv"
    assert main(
        [
            "asm",
            "--input",
            str(source),
            "--output",
            str(machine_code),
        ]
    ) == 0
    assert main(
        [
            "run",
            "--input",
            str(machine_code),
            "--dump",
            str(dump),
            "--range",
            "400:410",
        ]
    ) == 0
    with dump.open(encoding="utf-8", newline="") as output_file:
        rows = list(csv.DictReader(output_file))
    assert len(rows) == 10
    assert [int(row["addr"]) for row in rows] == list(range(400, 410))
    assert [int(row["value_dec"]) for row in rows] == expected
    assert [row["value_hex"] for row in rows] == [
        f"0x{value:08x}" for value in expected
    ]
