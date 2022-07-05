import argparse
import logging
from typing import Dict

from nfcli import load_path
from nfcli.extractor import extract_slots
from nfcli.parser import parse_any
from nfcli.printer import printer_factory
from nfcli.writer import determine_output_file

DESC = """Command line interface for converting Nebulous: Fleet Command fleet and ship files to images."""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument("-e", "--extract", type=str, help="extract slot info")
    parser.add_argument("-i", "--input", type=str, help="fleet or ship file to convert")
    parser.add_argument("-p", "--print", action="store_true", help="print output to console")
    parser.add_argument("-s", "--style", type=str, default="auto", help="printer style: auto (default), column, stack")
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
    if args.input:
        xml_data = load_path(args.input)
        entity = parse_any(args.input, xml_data)
        if args.extract:
            extract_slots(args.extract, entity)
        if args.print:
            printer = printer_factory(args.style, entity)
            entity.print(printer)
        if args.write:
            output_file = determine_output_file(args.input, ".png")
            entity.write(output_file)
    else:
        parser = get_parser()
        parser.print_help()


if __name__ == "__main__":
    status = main()
    exit(status)
