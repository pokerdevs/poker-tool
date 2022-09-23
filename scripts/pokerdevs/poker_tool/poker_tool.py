from __future__ import annotations
import typing
import pathlib
import logging
import argparse
from pokerdevs.poker_tool import (
    __version__,
    MonkerToPioRangeTool
)


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Pokertool")
    parser.add_argument("-v", "--version", action="version", version=f"poker-tool version {version(__version__)}")
    subparsers = parser.add_subparsers(dest='command', help='Which tool do you want to use ?')
    monker_to_pio_parser = subparsers.add_parser('monker-to-pio', help='Convert MonkerSolver ranges to PioSolver format')
    monker_to_pio_parser.add_argument("-i", "--input-path", type=str, required=True, help="Path to input directory containing Monker .rng files")
    monker_to_pio_parser.add_argument("-o", "--output-path", type=str, required=True, help="Path to output directory to put the PioSolver range files")
    monker_to_pio_parser.add_argument("-f", "--force-overwrite", action='store_true', default=False, required=False, help="Force overwrite of output dir")
    args = parser.parse_args()
    # configure the logger
    logging.basicConfig(level=logging.INFO)
    try:
        if args.command == 'monker-to-pio':
            MonkerToPioRangeTool.run(   input_path=pathlib.Path(args.input_path),
                                        output_path=pathlib.Path(args.output_path),
                                        force_overwrite=args.force_overwrite  )
        elif args.command is None:
            raise RuntimeError(f"You need to specify a tool to use !")
        else:
            raise RuntimeError(f"Unknown tool option `{args.command}` !")
    except Exception as e:
        print(f"Failed due to exception: {e}")


if __name__ == "__main__"   :
    main()


