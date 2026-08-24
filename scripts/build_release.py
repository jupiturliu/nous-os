#!/usr/bin/env python3
"""Stable source-checkout entry point for the Release Builder Module."""

from nous_os.release.__main__ import main


if __name__ == "__main__":
    raise SystemExit(main(["build", *__import__("sys").argv[1:]]))
