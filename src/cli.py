"""Command-line entrypoint."""

import argparse
from pathlib import Path

from src.assembler import assemble
from src.codegen import encode_instruction, encode_program
from src.constants import RANGE_ENDPOINT_COUNT
from src.interpreter import Interpreter
from src.isa import MNEMONIC_CODES, Instruction
from src.memory import Memory

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
    run_parser = commands.add_parser("run", help="execute a machine-code file")
    run_parser.add_argument("--input", required=True, help="machine-code file")
    run_parser.add_argument("--dump", help="CSV data-memory output")
    run_parser.add_argument(
        "--range",
        type=_parse_range,
        dest="address_range",
        help="half-open data-memory range, start:end",
    )
    return parser


def _parse_range(value: str) -> tuple[int, int]:
    parts = value.split(":")
    if len(parts) != RANGE_ENDPOINT_COUNT:
        raise argparse.ArgumentTypeError("range must use start:end")
    try:
        return int(parts[0], 0), int(parts[1], 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "range addresses must be integer literals"
        ) from error


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
    if args.command == "run":
        return _run_command(args, parser)
    return _assemble_command(args, parser)


def _assemble_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
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


def _run_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    if args.address_range is not None and args.dump is None:
        parser.error("--range requires --dump")
    memory = Memory(code_mem=Path(args.input).read_bytes())
    instruction_count = Interpreter(memory).run()
    if args.dump:
        memory.dump_csv(args.dump, args.address_range)
    print(f"Executed {instruction_count} instructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
