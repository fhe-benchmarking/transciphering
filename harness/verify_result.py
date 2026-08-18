#!/usr/bin/env python3

# Copyright (c) 2025 HomomorphicEncryption.org
# All rights reserved.
#
# This software is licensed under the terms of the Apache v2 License.
# See the LICENSE.md file for details.

"""
verify_result.py - correctness oracle for the mini-workload result
"""

import sys
from pathlib import Path
from utils import TextFormat

def main():

    """
    Usage:  python3 verify_result.py  <expected_file>  <result_file>  [label]
    Returns exit-code 0 if equal, 1 otherwise.
    Prints a message so the caller can log it. The optional label (e.g. MAX or
    IP) identifies which mini workload was verified.
    """

    if len(sys.argv) not in (3, 4):
        sys.exit("Usage: verify_result.py <expected> <result> [label]")

    expected_file = Path(sys.argv[1])
    result_file   = Path(sys.argv[2])
    label = f" {sys.argv[3]}" if len(sys.argv) == 4 else ""

    try:
        exp = list(map(int, expected_file.read_text().split()))
        res = list(map(int, result_file.read_text().split()))
    except Exception as e:
        print(f"[harness] failed to read files: {e}")
        sys.exit(1)

    if exp == res:
        print(f"{TextFormat.GREEN}         [harness] PASS{label}  (expected={exp}, got={res}){TextFormat.RESET}")
        sys.exit(0)
    else:
        print(f"{TextFormat.RED}         [harness] FAIL{label}  (expected={exp}, got={res}){TextFormat.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()