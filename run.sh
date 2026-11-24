#!/bin/sh
set -eu

case "${1:-}" in
    asm)
        shift
        exec python3 -m src.cli asm "$@"
        ;;
    run)
        shift
        exec python3 -m src.cli run "$@"
        ;;
    test)
        exec python3 -m pytest -q
        ;;
    *)
        printf 'Usage: %s {asm|run|test} [options]\n' "$0" >&2
        exit 2
        ;;
esac
