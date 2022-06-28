import argparse
import logging
from pathlib import Path
from typing import Dict

from nfcli import load_path
from nfcli.database import init_database
from nfcli.parser import parse_fleet
from nfcli.printer import printer_factory
from nfcli.writer import write_fleet

DESC = """Command line interface for converting Nebulous: Fleet Command fleet files into Record Sheet images."""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument("-f", "--format", type=str, default="png", help="image format")
    parser.add_argument(
        "-i", "--input-fleet", type=str, required=True, help="fleet file to convert"
    )
    parser.add_argument(
        "-o", "--output-prefix", type=str, default="", help="output file prefix"
    )
    parser.add_argument(
        "-p", "--print", action="store_true", help="print output to console"
    )
    parser.add_argument(
        "-s",
        "--style",
        type=str,
        default="auto",
        help="printer style: auto (default), column, stack",
    )
    parser.add_argument(
        "-w", "--write", action="store_true", help="write output to a file"
    )
    return parser


def parse_args() -> Dict:
    parser = get_parser()
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if not args.output_prefix:
        args.output_prefix = Path(args.input_fleet).stem
        logging.debug(
            f"Setting output prefix based on input fleet: {args.output_prefix}"
        )
    return args


def main() -> int:
    args = parse_args()
    init_database()
    xml_data = load_path(args.input_fleet)
    fleet = parse_fleet(xml_data)
    if args.print:
        printer = printer_factory(args.style, len(fleet.ships))
        printer.print(fleet)
    if args.write:
        write_fleet(fleet, args.output_prefix)


if __name__ == "__main__":
    status = main()
    exit(status)
