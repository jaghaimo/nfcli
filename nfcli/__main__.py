import argparse
import logging
from pathlib import Path
from typing import Dict

from nfcli import load_path
from nfcli.database import init_database
from nfcli.parser import parse_fleet
from nfcli.printer import printer_factory
from nfcli.writer import determine_output_file, write_fleet

DESC = """Command line interface for converting Nebulous: Fleet Command fleet files into Record Sheet images."""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument(
        "-i", "--input-fleet", type=str, required=True, help="fleet file to convert"
    )
    parser.add_argument("-p", "--print", action="store_true", help="print output to console")
    parser.add_argument(
        "-s",
        "--style",
        type=str,
        default="auto",
        help="printer style: auto (default), column, stack",
    )
    parser.add_argument("-w", "--write", action="store_true", help="write output to a file")
    return parser


def parse_args() -> Dict:
    parser = get_parser()
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
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
        output_file = determine_output_file(args.input_fleet, ".png")
        write_fleet(fleet, output_file)


if __name__ == "__main__":
    status = main()
    exit(status)
