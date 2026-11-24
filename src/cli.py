"""Command-line entrypoint."""

import argparse
from pathlib import Path

from src.assembler import assemble
from src.codegen import encode_instruction, encode_program
from src.isa import MNEMONIC_CODES, Instruction

FIELD_NAMES = {
    "LOAD_CONST": ("B", "C"),
    "LOAD_MEM": ("B", "C", "D"),
    "STORE_MEM": ("B", "C"),
    "ADD": ("B", "C", "D"),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="УВМ assembler and interpreter",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    asm_parser = commands.add_parser("asm", help="assemble a text program")
    asm_parser.add_argument("--input", required=True, help="assembly source")
    asm_parser.add_argument("--output", help="output file")
    asm_parser.add_argument(
        "--test",
        action="store_true",
        help="print decoded instruction fields",
    )
    return parser


def _format_instruction(instruction: Instruction) -> str:
    fields = [f"A={MNEMONIC_CODES[instruction.mnemonic]}"]
    fields.extend(
        f"{name}={value}"
        for name, value in zip(
            FIELD_NAMES[instruction.mnemonic],
            instruction.operands,
        )
    )
    return f"{instruction.mnemonic}: " + ", ".join(fields)


def main(argv: list[str] | None = None) -> int:
    """Run the command-line application.

    Args:
        argv: Optional command-line arguments.

    Returns:
        Process exit status.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "asm":
        parser.error("this command is not available yet")
    instructions = assemble(Path(args.input).read_text(encoding="utf-8"))
    if args.test:
        for instruction in instructions:
            print(_format_instruction(instruction))
            print(encode_instruction(instruction).hex(" "))
        return 0
    if not args.output:
        parser.error("asm requires --output unless --test is used")
    Path(args.output).write_bytes(encode_program(instructions))
    print(f"Assembled {len(instructions)} instructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
