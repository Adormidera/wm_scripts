import sys
from argparse import ArgumentParser
from dataclasses import dataclass

from arf import DEFAULT_CONFIG_FILE, start


@dataclass
class ARFConfig:
    config_file: str


def cli():
    arg_parser = ArgumentParser()

    arg_parser.add_argument(
        "-c",
        "--config-file",
        type=str,
        action="store",
        default=DEFAULT_CONFIG_FILE,
        help=f"The config file to read (default: {DEFAULT_CONFIG_FILE})",
    )

    args = arg_parser.parse_args(sys.argv[1:])

    start(args.config_file, "something")


if __name__ == "__main__":
    cli()
