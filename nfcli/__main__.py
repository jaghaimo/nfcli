import argparse
import logging
from pathlib import Path
from typing import Dict

from nfcli.parser import parse_input
from nfcli.printer import print_fleet, print_ship
from nfcli.writer import write_ship

DESC = """Command line interface for converting Nebulous: Fleet Command fleet files into Record Sheet images."""

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument(
        "-i", "--input-fleet", type=str, required=True, help="fleet file to convert"
    )
    parser.add_argument(
        "-o", "--output-prefix", type=str, default="", help="output file prefix"
    )
    parser.add_argument(
        "-f", "--format", type=str, default="png", help="image format"
    )
    return parser

def parse_args() -> Dict:
    parser = get_parser()
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if not args.output_prefix:
        args.output_prefix = Path(args.input_fleet).stem + "_"
        logging.debug(f"Setting output prefix based on input fleet: {args.output_prefix}")
    return args

def main() -> int:
    args = parse_args()
    fleet = parse_input(args.input_fleet)
    print_fleet(fleet)
    for idx, ship in enumerate(fleet.ships):
        write_ship(ship, args.output_prefix + str(idx))


if __name__ == "__main__":
    status = main()
    exit(status)
