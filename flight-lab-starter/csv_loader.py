
"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    seen = set()

    for path in paths:
        filename = os.path.basename(path)

        with open(path, "r", encoding="utf-8", newline="") as file:
            for line_number, line in enumerate(file, start=1):

                if line_number == 1:
                    continue

                if not line.strip():
                    continue

                if line.lstrip().startswith("#"):
                    continue

                fields = next(csv.reader([line]))

                error = validate_row(fields, airports)

                if error is None:
                    record = to_record(fields)

                    key = (
                        record["flight_id"],
                        record["departure_datetime"]
                    )

                    if key in seen:
                        error = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(record)

                if error is not None:
                    message = (
                        f"{filename}:{line_number}: "
                        f"{error} | {line.rstrip()}"
                    )

                    errors.append(message)

    return records, errors
