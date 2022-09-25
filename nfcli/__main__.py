import argparse
import logging
from typing import Dict

from rich.console import Console

from nfcli import determine_output_png, init_logger, load_path, nfc_theme
from nfcli.parsers import parse_any, parse_mods
from nfcli.sqlite import create_connection, fetch_usage_servers
from nfcli.steam import get_workshop_files

DESC = """Command line interface for converting Nebulous: Fleet Command fleet and ship files to images."""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument("-i", "--input", type=str, help="fleet or ship file to convert")
    parser.add_argument("-p", "--print", action="store_true", help="print output to console")
    parser.add_argument("-w", "--write", action="store_true", help="write output to a file")
    parser.add_argument("--stats", type=int, help="print bot usage stats")
    parser.add_argument("--workshop", type=int, help="download and parse Steam Workshop fleet")
    return parser


def parse_args() -> Dict:
    parser = get_parser()
    args = parser.parse_args()
    display_level = logging.DEBUG if args.debug else logging.WARNING
    init_logger(None, display_level)
    return args


def main() -> int:
    args = parse_args()
    entity = None
    if args.workshop:
        input_files = get_workshop_files(args.workshop)
        args.input = input_files[0] if input_files else None
    if args.input:
        xml_data = load_path(args.input)
        entity = parse_any(args.input, xml_data)
    if entity:
        if args.print:
            console = Console(theme=nfc_theme)
            mods = parse_mods(xml_data)
            entity.print(console, True, mods)
        if args.write:
            output_file = determine_output_png(args.input)
            entity.write(output_file)
    elif args.stats:
        connection = create_connection()
        print(fetch_usage_servers(connection, abs(args.stats)))
    else:
        parser = get_parser()
        parser.print_help()
    return 0


if __name__ == "__main__":
    status = main()
    exit(status)
