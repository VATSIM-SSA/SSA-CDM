#!/usr/bin/env python3
"""Validation script for SSA-CDM data files."""

import os
import sys
import re

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
EXPECTED_FILES = ["CTOT.txt", "rate.txt", "sidinterval.txt", "taxizones.txt"]

errors = []


def error(fir, filename, line_num, message):
    errors.append(f"  {fir}/{filename}:{line_num} — {message}")


def is_valid_icao(code):
    return bool(re.match(r"^[A-Z]{4}$", code))


def validate_rate(fir, lines):
    for i, line in enumerate(lines, start=1):
        if line.startswith("#") or line.startswith("AIRPORT"):
            continue
        fields = line.split(":")
        if len(fields) != 9:
            error(fir, "rate.txt", i, f"expected 9 fields, got {len(fields)}")
            continue
        airport = fields[0]
        if not is_valid_icao(airport):
            error(fir, "rate.txt", i, f"invalid ICAO code: '{airport}'")
        rate_field = fields[8]
        parts = rate_field.split("_")
        if len(parts) != 2:
            error(fir, "rate.txt", i, f"rate field should be Rate_RateLvo, got: '{rate_field}'")
            continue
        for part in parts:
            if not part.isdigit() or int(part) <= 0:
                error(fir, "rate.txt", i, f"rate value should be a positive integer, got: '{part}'")


def validate_sidinterval(fir, lines):
    for i, line in enumerate(lines, start=1):
        if line.startswith("#"):
            continue
        fields = line.split(",")
        if len(fields) != 5:
            error(fir, "sidinterval.txt", i, f"expected 5 fields, got {len(fields)}")
            continue
        airport = fields[0]
        if not is_valid_icao(airport):
            error(fir, "sidinterval.txt", i, f"invalid ICAO code: '{airport}'")
        sep = fields[4]
        if not sep.isdigit() or int(sep) <= 0:
            error(fir, "sidinterval.txt", i, f"separation should be a positive integer, got: '{sep}'")


def validate_taxizones(fir, lines):
    for i, line in enumerate(lines, start=1):
        if line.startswith("#") or line.strip() == "":
            continue
        fields = line.split(":")
        # Each line: AIRPORT:RUNWAY + 4 coordinate pairs (8 fields) + ZONE_ID = 11 total
        if len(fields) != 11:
            error(fir, "taxizones.txt", i, f"expected 11 fields, got {len(fields)}")
            continue
        airport = fields[0]
        if not is_valid_icao(airport):
            error(fir, "taxizones.txt", i, f"invalid ICAO code: '{airport}'")
        zone_id = fields[10]
        if not zone_id.isdigit():
            error(fir, "taxizones.txt", i, f"zone ID should be numeric, got: '{zone_id}'")


def validate_ctot(fir, lines):
    for i, line in enumerate(lines, start=1):
        if line.startswith("#") or line.startswith("[") or line.startswith("Add"):
            continue
        fields = line.split(",")
        if len(fields) != 2:
            error(fir, "CTOT.txt", i, f"expected 2 fields, got {len(fields)}")


def validate_fir(fir_path, fir_name):
    files_present = os.listdir(fir_path)
    for expected in EXPECTED_FILES:
        if expected not in files_present:
            errors.append(f"  {fir_name}/ — missing file: {expected}")

    for filename in EXPECTED_FILES:
        filepath = os.path.join(fir_path, filename)
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        if filename == "rate.txt":
            validate_rate(fir_name, lines)
        elif filename == "sidinterval.txt":
            validate_sidinterval(fir_name, lines)
        elif filename == "taxizones.txt":
            validate_taxizones(fir_name, lines)
        elif filename == "CTOT.txt":
            validate_ctot(fir_name, lines)


def main():
    fir_dirs = []
    for entry in sorted(os.listdir(REPO_ROOT)):
        full_path = os.path.join(REPO_ROOT, entry)
        if os.path.isdir(full_path) and not entry.startswith("."):
            fir_dirs.append((entry, full_path))

    if not fir_dirs:
        print("No FIR directories found.")
        sys.exit(1)

    print(f"Validating {len(fir_dirs)} FIR(s): {', '.join(name for name, _ in fir_dirs)}")
    print()

    for fir_name, fir_path in fir_dirs:
        validate_fir(fir_path, fir_name)

    if errors:
        print(f"Found {len(errors)} error(s):\n")
        for err in errors:
            print(err)
        print()
        sys.exit(1)
    else:
        print("All files valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
