from __future__ import annotations
import typing
import pathlib
import os
import shutil
import itertools
import logging
import argparse

logger = logging.getLogger(__name__)


MONKER_RANGE_FILE_SUFFIX = '.rng'
PIO_RANGE_FILE_SUFFIX = '.txt'


class ActionTuple(tuple):

    def __new__ (cls, long_name: str, short_name: str):
        return super().__new__(cls, (long_name, short_name))

    def long_name(self):
        return self[0]

    def short_name(self):
        return self[1]


class MonkerNameTranslator:

    ACTION_LOOKUP = {
        0: ActionTuple("fold", "f"),
        1: ActionTuple("call", "c"),
        2: ActionTuple("pot", "r(100%)"),
        3: ActionTuple("all-in", "r(max)"),
        4: ActionTuple("50%", "r(50%)"),
        5: ActionTuple("min", "r(min)"),
        6: ActionTuple("bet", "bet"), # ??
        7: ActionTuple("25%", "r(25%)"),
        8: ActionTuple("2x", "r(2x)"),
        9: ActionTuple("75%", "r(75%)"),
        10: ActionTuple("%", "%")  # ??
    }

    @classmethod
    def translate_action(cls, monker_action: int) -> ActionTuple:
        if monker_action > 40000:
            pot_ratio = (monker_action - 40000)
            return ActionTuple(f"{pot_ratio}%", f"r({pot_ratio}%)")
        elif monker_action > 11:
            amount = (monker_action - 11)
            return ActionTuple(f"{amount}-sb", f"r({amount}sb)")
        elif monker_action < 11:
            return cls.ACTION_LOOKUP[monker_action]
        else:
            raise ValueError(f"Unexpected monker_action value {monker_action} !")

    @classmethod
    def gen_action_tuples_from_file_name(cls, file_name_without_ext: str) -> typing.Iterator[ActionTuple]:
        for elem in file_name_without_ext.split('.'):
            try:
                monker_action = int(elem)
            except ValueError:
                raise ValueError(f"Invalid Monker file name `{file_name_without_ext}`: Could not parse '{elem}' !")
            yield cls.translate_action(monker_action)


class MonkerRangeTranslator:


    @classmethod
    def gen_translate_range_lines(cls, contents: str) -> str:
        lines = contents.splitlines()
        for even_line, odd_line in zip(lines[::2], lines[1::2]):
            hand = even_line
            value = odd_line.split(";", maxsplit=1)[0] + ","
            yield f"{hand}:{value}"

    @classmethod
    def translate_range_content(cls, contents: str) -> str:
        return os.linesep.join(cls.gen_translate_range_lines(contents))


class PioRangeOutputBuilder:

    @classmethod
    def create_relative_parent_dir_path_for_actions(cls, action_tuples: typing.Tuple[ActionTuple, ...]):
        return pathlib.Path('/'.join(at.long_name() for at in action_tuples))

    @classmethod
    def create_relative_file_path_for_actions(cls, action_tuples: typing.Tuple[ActionTuple, ...]):
        parent_path = cls.create_relative_parent_dir_path_for_actions(action_tuples)
        return parent_path / ((''.join(at.short_name() for at in action_tuples)) + PIO_RANGE_FILE_SUFFIX)

    @classmethod
    def create_pio_range_file(cls, output_root_path: pathlib.Path, monker_rng_file_path: pathlib.Path):
        action_tuples = tuple(MonkerNameTranslator.gen_action_tuples_from_file_name(monker_rng_file_path.stem))
        dest_file_path = output_root_path / cls.create_relative_file_path_for_actions(action_tuples)
        dest_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(monker_rng_file_path, 'r') as f_in:
            logger.info(f"Writing PioSolver range file to `{dest_file_path}`")
            with open(dest_file_path, 'w') as f_out:                
                f_out.write(MonkerRangeTranslator.translate_range_content(f_in.read()))


    @classmethod
    def build_pio_range_files(cls, input_path: pathlib.Path, output_path: pathlib.Path):
        for monker_rng_file_path in input_path.glob('**/*'+MONKER_RANGE_FILE_SUFFIX):
            logger.info(f"Processing monker file `{monker_rng_file_path}`")
            rel_path = monker_rng_file_path.parent.relative_to(input_path)
            cls.create_pio_range_file(  output_root_path=output_path / rel_path,
                                        monker_rng_file_path=monker_rng_file_path  )

    @classmethod
    def clear_output_dir(cls, dir_path: pathlib.Path):
        shutil.rmtree(dir_path)
        dir_path.mkdir(parents=False, exist_ok=False)



class ArgValidator:

    VALID_MONKER_RNG_SUFFIXES = {MONKER_RANGE_FILE_SUFFIX}
    VALID_PIO_RNG_SUFFIXES = {PIO_RANGE_FILE_SUFFIX}

    @classmethod
    def is_valid_monker_rng_file(cls, file_path: pathlib.Path) -> bool:
        return ((file_path.is_file()) and
                (file_path.suffix in cls.VALID_MONKER_RNG_SUFFIXES) and
                (all(c=='.' or c.isdigit() for c in file_path.stem)))

    @classmethod
    def dir_contains_no_files(cls, dir_path: pathlib.Path) -> bool:
        return all((not p.is_file()) for p in dir_path.iterdir())

    @classmethod
    def ensure_valid_monker_range_path(cls, dir_path: pathlib.Path):
        if cls.dir_contains_no_files(dir_path):
            for child_path in dir_path.iterdir():
                cls.ensure_valid_monker_range_path(child_path)
        else:
            err_msg = f"Invalid monker range directory `{dir_path}`: Expected there to only be valid .rng files"
            assert all(cls.is_valid_monker_rng_file(child_path) for child_path in dir_path.iterdir()), err_msg

    @classmethod
    def is_valid_pio_range_file(cls, file_path: pathlib.Path) -> bool:
        return ((file_path.is_file()) and
                (file_path.suffix in cls.VALID_PIO_RNG_SUFFIXES))

    @classmethod
    def ensure_valid_pio_range_path(cls, dir_path: pathlib.Path):
        assert dir_path.is_dir(), f"Invalid directory `{dir_path}` for PioSolver ranges !"
        for child_path in dir_path.iterdir():
            if child_path.is_file():
                err_msg = f"Invalid directory for PioSolver ranges since it contains non-range file `{child_path}` !"
                assert cls.is_valid_pio_range_file(child_path), err_msg
            else:
                cls.ensure_valid_pio_range_path(child_path)

    @classmethod
    def ensure_valid_output_dir(cls, dir_path: pathlib.Path, force_overwrite: bool):
        cls.ensure_valid_pio_range_path(dir_path)
        is_empty = not any(dir_path.iterdir())
        if (not force_overwrite):
            assert is_empty, f"{dir_path} is not empty, use the -f flag to overwrite it !"


class MonkerToPioRangeTool:

    @classmethod
    def run(cls, input_path: pathlib.Path, output_path: pathlib.Path, force_overwrite: bool):
        ArgValidator.ensure_valid_monker_range_path(input_path)
        ArgValidator.ensure_valid_output_dir(dir_path=output_path, force_overwrite=force_overwrite)
        if force_overwrite:
            PioRangeOutputBuilder.clear_output_dir(output_path)
        PioRangeOutputBuilder.build_pio_range_files(input_path, output_path)

