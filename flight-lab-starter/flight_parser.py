
"""Flight Schedule Parser and Query Tool - command-line entry point."""

import sys
import argparse
import json
import logging
import csv
from pathlib import Path
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "251ADB034"
FIRST_NAME = "Azar"
LAST_NAME = "Hsaanaliyev"


def read_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    source = parser.add_mutually_exclusive_group(required=True)

    source.add_argument("-i", metavar="FILE")
    source.add_argument("-d", metavar="FOLDER")
    source.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    try:
        args = parser.parse_args(argv)

        if args.j is None and args.a is None:
            parser.error("-a is required with -i or -d")

        if args.j is not None and args.o is not None:
            parser.error("-o cannot be used with -j")

    except SystemExit as error:
        return error.code

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)

    handler = None

    try:
        if args.j is not None:
            db = read_json(args.j)

            if not isinstance(db, list):
                raise ValueError("Database must be a JSON array")

            if not all(isinstance(record, dict) for record in db):
                raise ValueError("Database must contain objects")

        else:
            output_path = Path(args.o if args.o is not None else "db.json")
            log_path = output_path.parent / "errors.log"

            handler = logging.FileHandler(
                log_path,
                mode="w",
                encoding="utf-8"
            )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            logger.addHandler(handler)

            airports = load_airports(args.a)

            if args.i is not None:
                paths = [args.i]

            else:
                folder = Path(args.d)

                paths = sorted(
                    str(path)
                    for path in folder.iterdir()
                    if path.is_file() and path.name.endswith(".csv")
                )

                if not paths:
                    raise ValueError("No CSV files found in folder")

            db, errors = parse_files(paths, airports)

            for error in errors:
                logger.warning(error)

            write_json(output_path, db)

        if args.q is not None:
            queries = read_json(args.q)

            if isinstance(queries, dict):
                pass

            elif isinstance(queries, list):
                if not all(isinstance(query, dict) for query in queries):
                    raise ValueError("Query array must contain objects")

            else:
                raise ValueError("Queries must be an object or array of objects")

            responses = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            response_path = Path(args.r) / filename

            write_json(response_path, responses)

        return 0

    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
