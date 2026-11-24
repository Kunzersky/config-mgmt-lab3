"""Separated code and sparse data memories with CSV export."""

import csv
from dataclasses import dataclass, field
from pathlib import Path

from src.constants import ADDRESS_SPACE_SIZE, MASK_32


@dataclass
class Memory:
    """A virtual machine's independent instruction and data spaces."""

    code_mem: bytes = b""
    data_mem: dict[int, int] = field(default_factory=dict)

    def read_data(self, address: int) -> int:
        """Return a data word, defaulting uninitialized cells to zero.

        Args:
            address: Data-memory address.

        Returns:
            The stored unsigned 32-bit word.

        Raises:
            ValueError: If the address is outside the 32-bit address space.
        """
        _validate_address(address)
        return self.data_mem.get(address, 0)

    def write_data(self, address: int, value: int) -> None:
        """Store an unsigned 32-bit data word.

        Args:
            address: Data-memory address.
            value: Value to store.

        Raises:
            ValueError: If the address or value is outside the valid range.
        """
        _validate_address(address)
        if value < 0 or value > MASK_32:
            raise ValueError(f"value is outside the 32-bit range: {value}")
        self.data_mem[address] = value

    def dump_csv(
        self,
        output_path: str | Path,
        address_range: tuple[int, int] | None = None,
    ) -> None:
        """Write selected data cells as address, hexadecimal, and decimal.

        Args:
            output_path: Destination CSV file.
            address_range: Optional half-open address interval.

        Raises:
            ValueError: If the requested interval is invalid.
        """
        addresses = _select_addresses(self.data_mem, address_range)
        with Path(output_path).open(
            "w",
            encoding="utf-8",
            newline="",
        ) as output_file:
            writer = csv.writer(output_file)
            writer.writerow(("addr", "value_hex", "value_dec"))
            for address in addresses:
                value = self.read_data(address)
                writer.writerow((address, f"0x{value:08x}", value))


def _validate_address(address: int) -> None:
    if address < 0 or address >= ADDRESS_SPACE_SIZE:
        raise ValueError(f"address is outside the 32-bit range: {address}")


def _select_addresses(
    data_mem: dict[int, int],
    address_range: tuple[int, int] | None,
) -> list[int] | range:
    if address_range is None:
        return sorted(
            address for address, value in data_mem.items() if value != 0
        )
    start, end = address_range
    if start < 0 or end < start or end > ADDRESS_SPACE_SIZE:
        raise ValueError("invalid address range")
    return range(start, end)
