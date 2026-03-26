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
    for line_num, line in lines:
        if line.startswith("#") or line.startswith("AIRPORT"):
            continue
        fields = line.split(":")
        if len(fields) != 9:
            error(fir, "rate.txt", line_num, f"expected 9 fields, got {len(fields)}")
            continue
        airport = fields[0]
        if not is_valid_icao(airport):
            error(fir, "rate.txt", line_num, f"invalid ICAO code: '{airport}'")
        rate_field = fields[8]
        parts = rate_field.split("_")
        if len(parts) != 2:
            error(fir, "rate.txt", line_num, f"rate field should be Rate_RateLvo, got: '{rate_field}'")
            continue
        for part in parts:
            if not part.isdigit() or int(part) <= 0:
                error(fir, "rate.txt", line_num, f"rate value should be a positive integer, got: '{part}'")


def validate_sidinterval(fir, lines):
    for line_num, line in lines:
        if line.startswith("#"):
            continue
        fields = line.split(",")
        if len(fields) != 5:
            error(fir, "sidinterval.txt", line_num, f"expected 5 fields, got {len(fields)}")
            continue
        airport = fields[0]
        if not is_valid_icao(airport):
            error(fir, "sidinterval.txt", line_num, f"invalid ICAO code: '{airport}'")
        sep = fields[4]
        if not sep.isdigit() or int(sep) <= 0:
            error(fir, "sidinterval.txt", line_num, f"separation should be a positive integer, got: '{sep}'")


def validate_taxizones(fir, lines):
    for line_num, line in lines:
        if line.startswith("#"):
            continue
        fields = line.split(":")
        # Each line: AIRPORT:RUNWAY + 4 coordinate pairs (8 fields) + ZONE_ID = 11 total
        if len(fields) != 11:
            error(fir, "taxizones.txt", line_num, f"expected 11 fields, got {len(fields)}")
            continue
        airport = fields[0]
        if not is_valid_icao(airport):
            error(fir, "taxizones.txt", line_num, f"invalid ICAO code: '{airport}'")
        zone_id = fields[10]
        if not zone_id.isdigit():
            error(fir, "taxizones.txt", line_num, f"zone ID should be numeric, got: '{zone_id}'")


def is_valid_ctot_time(value):
    if not re.match(r"^\d{4}$", value):
        return False
    hours, minutes = int(value[:2]), int(value[2:])
    return 0 <= hours <= 23 and 0 <= minutes <= 59


def validate_ctot(fir, lines):
    for line_num, line in lines:
        if line.startswith("#") or line.startswith("Add"):
            continue
        # Skip the format specification line
        if line.strip() == "[CID],[CTOT]":
            continue
        fields = line.split(",")
        if len(fields) != 2:
            error(fir, "CTOT.txt", line_num, f"expected 2 fields, got {len(fields)}")
            continue
        cid, ctot = fields[0].strip(), fields[1].strip()
        if not cid.isdigit():
            error(fir, "CTOT.txt", line_num, f"CID should be numeric, got: '{cid}'")
        if not is_valid_ctot_time(ctot):
            error(fir, "CTOT.txt", line_num, f"CTOT should be a valid time (0000-2359), got: '{ctot}'")


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
            lines = [(num, line.strip()) for num, line in enumerate(f, start=1) if line.strip()]

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
        if os.path.isdir(full_path) and not entry.startswith(".") and is_valid_icao(entry):
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
