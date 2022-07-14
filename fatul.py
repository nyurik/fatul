#!/usr/bin/env python3

#
# Copyright (C) 2022 by Yuri Astrakhan <YuriAstrakhan@gmail.com>.
# This code is licensed under the MIT license.
# The _make_iterencode() code is based on the Python JSON library's code.
#
# See https://github.com/nyurik/fatul for new versions and upgrade instructions.
#
# This utility converts Factorio blueprints to an alternative JSON representation
# that uses relative coordinates instead of entity_number values, and uses (x,y) sort.
# This minimizes changes between blueprint versions.

import argparse
import base64
import json
import re
import sys
import textwrap
import zlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from traceback import format_exception
from typing import List, Any, Literal, NewType, Tuple, Dict, get_args, Union, Optional

try:
    # Optionally allow clipboard access
    import pyperclip
except ImportError:
    pyperclip = None

MAX_LINE_LENGTH = 100
COORD_MULTIPLIER = 16
SORT_ORDER = {
    "name": "0",
    "item": "1",
    "label": "2",
    "description": "3",
    "_simple": "8",  # other keys with simple values
    "_complex": "9",  # other keys with list and dict values
}
COMPLEX_TYPES = {dict, list}
NUMBER_TYPES = (int, float)
IdsMode = Literal["refs", "mixed", "keep"]
SortMode = Literal["all", "entities", "keys", "none"]
Position = NewType("Position", Tuple[int, int])
EID = NewType("EID", int)


def main():
    # Top level
    parser = argparse.ArgumentParser(
        description="This tool helps to manage Factorio blueprints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Decode
    decoder = subparsers.add_parser(
        "decode", aliases=["d"], formatter_class=argparse.RawTextHelpFormatter,
        help="Decode a blueprint from clipboard, a file, or stdin")
    decoder.set_defaults(func=decode_cmd)
    decoder.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    decoder.add_argument("--ids", choices=get_args(IdsMode), default="refs",
                         help=textwrap.dedent("""\
                         How to process the entity_number and entity_id values - '%(default)s' by default
                            * refs  - convert entity_id and neighbours values to relative references.
                                      storing the delta x,y relative to the current entity.
                                      The original entity_id and entity_number values will be removed.
                            * mixed - Same as refs, but do not delete original entity_id values.
                            * keep  - Do not convert entity_id and neighbours values."""))
    decoder.add_argument("--sort", choices=get_args(SortMode), default="all",
                         help=textwrap.dedent("""\
                         Order keys and entities in the output. (default = '%(default)s').
                            * all      - apply all sorting rules.
                            * entities - sort entities by their position, trying to keep nearby entities together.
                            * keys     - sort object keys alphabetically, moving 'name' to the top.
                            * none     - do not sort."""))
    decoder.add_argument("--pretty", "-p", dest="compact", default=True, action="store_false",
                         help="Use standard JSON formatting instead of compact")
    decoder.add_argument("--no-shift", dest="normalize_pos", default=True, action="store_false",
                         help="Do not change entity positions. If not set, FaTul will attempt to normalize x,y values.")
    decoder.add_argument("destination", type=Path,
                         help="The destination file or directory to write to. "
                              "Use '-' to write to STDOUT as a single formatted JSON.")
    decoder.add_argument("source", type=Path, nargs="?",
                         help="Optional source file with the Factorio blueprint string. "
                              "Uses clipboard if not specified. Use '-' to read from STDIN.")

    # Dump
    dumper = subparsers.add_parser(
        "dump", formatter_class=argparse.RawTextHelpFormatter,
        help="Decode a blueprint from clipboard, a file, or stdin without any additional processing. "
             "This is identical to   decode --ids=keep --sort=none")
    dumper.set_defaults(func=dump_cmd)
    dumper.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    dumper.add_argument("--pretty", "-p", dest="compact", default=True, action="store_false",
                        help="Use standard JSON formatting instead of compact")
    dumper.add_argument("destination", type=Path,
                        help="The destination file or directory to write to. "
                             "Use '-' to write to STDOUT as a single formatted JSON.")
    dumper.add_argument("source", type=Path, nargs="?",
                        help="Optional source file with the Factorio blueprint string. "
                             "Uses clipboard if not specified. Use '-' to read from STDIN.")

    # Encode
    encoder = subparsers.add_parser(
        "encode", aliases=["e"],
        help="Encode a blueprint from a file, directory, or stdin")
    encoder.set_defaults(func=encode_cmd)
    encoder.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    encoder.add_argument("source", type=Path,
                         help="A JSON file or a directory with JSON files to encode. Only *.json files are processed.")
    encoder.add_argument("destination", type=Path, nargs="?",
                         help="The destination file to write to. By default, the result "
                              "is copied to clipboard. Use '-' to write to STDOUT.")

    args = parser.parse_args()
    if args is None:
        parser.print_help(file=sys.stderr)
    else:
        try:
            args.func(args)
        except Exception as ex:
            message = str(ex)
            if args.verbose or message == "":
                message += "\n\n" + "".join(format_exception(type(ex), ex, ex.__traceback__))
            parser.error(message)


def dump_cmd(args: argparse.Namespace):
    decode(args.source, args.destination, args.verbose, args.compact, "none", "keep", normalize_pos=False)


def decode_cmd(args: argparse.Namespace):
    decode(args.source, args.destination, args.verbose, args.compact, args.sort, args.ids, args.normalize_pos)


def decode(source: Path, destination: Path, verbose: bool, compact: bool, sort_mode: SortMode,
           ids_mode: IdsMode, normalize_pos: bool) -> None:
    if source is None:
        assert_clipboard()
        eprint("Reading blueprint string from clipboard")
        json_text = pyperclip.paste()
    elif str(source) == "-":
        eprint("Reading blueprint string from STDIN")
        json_text = "".join(sys.stdin.readlines())
    else:
        if not source.is_file():
            raise ValueError(f"Source file does not exist, or it is not a file: {source}")
        eprint(f"Reading blueprint string from {source}")
        json_text = source.read_text()
    data = Processor(verbose, sort_mode, ids_mode, normalize_pos).decode(json_text)
    if str(destination) == "-":
        print(to_pretty_json(data, compact))
    else:
        write_files(data, destination, compact, verbose)


def encode_cmd(args: argparse.Namespace):
    if str(args.source) == "-":
        eprint("Reading json from STDIN")
        data = json.loads("".join(sys.stdin.readlines()))
    elif args.source.is_file():
        eprint(f"Reading a json file from {args.source}")
        data = json.loads(args.source.read_text())
    elif args.source.is_dir():
        eprint(f"Reading json files from directory {args.source}")
        data = read_files(args.source, args.verbose)
    else:
        raise ValueError(f"Invalid source file or directory: {args.source}")
    processor = Processor(args.verbose, "none", "keep", normalize_pos=False)
    encoded = processor.encode(data)
    if args.destination is None:
        assert_clipboard()
        pyperclip.copy(encoded)
        eprint(f"Encoded blueprint string was copied to clipboard.")
    elif str(args.destination) == "-":
        print(encoded)
    else:
        eprint(f"Writing to {args.destination}")
        args.destination.write_text(encoded)


def write_files(data: dict, dest: Path, compact: bool, verbose: bool) -> None:
    label = get_label(data)
    if "blueprint_book" not in data:
        dest = dest.with_suffix(".json")
        eprint(f"Writing {label} to {dest}")
        dest.write_text(to_pretty_json(data, compact) + "\n")
        return
    if dest.is_file() or dest.suffix == ".json":
        eprint(f"WARNING: Destination "
               f"{'already exists' if dest.is_file() else 'has a .json extension, treating it as a file'}. "
               f"Saving entire blueprint book as a single file to {dest}")
        dest.write_text(to_pretty_json(data, compact) + "\n")
        return
    eprint(f"Creating {label} {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    book = data["blueprint_book"]
    blueprints = book.pop("blueprints", [])
    (dest / "_metadata.json").write_text(to_pretty_json(data, compact) + "\n")
    files = set()
    for bp in blueprints:
        name = get_label(bp).lower()
        name = re.sub(r"[/\\]+", "-", name)
        name = re.sub(r"[.:]+", "-", name)
        name = re.sub(r"  +", " ", name)
        name = name.strip("_-. ")
        if name in files:
            copy = 2
            while True:
                test_name = f"{name} ({copy})"
                if test_name not in files:
                    name = test_name
                    break
                copy += 1
        files.add(name)
        write_files(bp, dest / name, compact, verbose)


def get_non_index_key(data):
    keys = set(data.keys())
    keys.discard("index")
    if len(keys) != 1:
        raise ValueError(f"Expected a single sub-entry in the input data, found: {','.join(keys)}")
    return keys.pop()


def read_files(dir_path: Path, verbose: bool) -> dict:
    # Recursively reads a directory of JSON files and returns a dict with the blueprint book
    metadata_path = dir_path / "_metadata.json"
    if not metadata_path.is_file():
        raise ValueError(f"Missing metadata file: {metadata_path}")
    data = json.loads(metadata_path.read_text())
    assert type(data) == dict
    blueprints = []
    key = get_non_index_key(data)
    # Factorio orders blueprints before the rest of the keys
    data[key] = {"blueprints": blueprints, **data[key]}
    for path in dir_path.iterdir():
        if path.is_dir():
            blueprints.append(read_files(path, verbose))
        elif path.is_file():
            if path.suffix != ".json":
                eprint(f"Ignoring non-json file: {path}")
                continue
            if path.name == "_metadata.json":
                continue
            if verbose:
                eprint(f"Loading {path}")
            blueprints.append(json.loads(path.read_text()))
        else:
            eprint(f"Skipping unrecognized {path}")
    blueprints.sort(key=lambda v: v.get("index", 0))
    return data


def assert_clipboard():
    if pyperclip is None:
        raise ValueError("pyperclip library is required to use clipboard.\n"
                         "Install it with:   pip3 install pyperclip\n"
                         "See https://github.com/nyurik/fatul#readme")


@dataclass
class Entity:
    path: str
    pos: Position
    names: List[str]


class Processor:
    def __init__(self, verbose: bool, sort_mode: SortMode, ids_mode: IdsMode, normalize_pos: bool):
        self.verbose = verbose
        self.normalize_pos = normalize_pos
        self.sort_keys = sort_mode == "all" or sort_mode == "keys"
        self.sort_entities = sort_mode == "all" or sort_mode == "entities"
        self.remove_entity_number = ids_mode == "refs"
        self.use_rel_ids = ids_mode != "keep"
        self.generate_ids = False

    def decode(self, json_text: str) -> dict:
        if not json_text.startswith("0"):
            raise ValueError("Invalid blueprint string. It must start with a 0.")
        data = json.loads(zlib.decompress(base64.b64decode(json_text[1:])).decode("utf8"))
        self.process(data, generate_ids=False)
        return data

    def encode(self, data: dict) -> str:
        self.process(data, generate_ids=True)
        compressed = zlib.compress(bytes(to_json(data), "utf8"), level=9)
        return "0" + base64.b64encode(compressed).decode("utf8")

    def process(self, data: dict, generate_ids):
        if type(data) != dict or len(data) != 1:
            raise ValueError("Invalid blueprint string. It must contain exactly one object.")
        if self.verbose:
            eprint(f"Processing {get_label(data)}")
        self.generate_ids = generate_ids
        return self._recurse(data, [])

    def _recurse(self, data: Any, path: List[str]) -> None:
        path.append("")
        if type(data) == dict:
            has_entities = False
            for key, val in data.items():
                if type(val) in COMPLEX_TYPES:
                    path[-1] = key
                    if key == "entities" and type(val) == list and len(path) >= 2 and path[-2] == "blueprint":
                        has_entities = True
                    else:
                        self._recurse(val, path)
            if has_entities:
                EntitiesProcessor(self, data).process(path)
            if self.sort_keys:
                sort_dict(data)
        elif type(data) == list:
            for idx, val in enumerate(data):
                if type(val) in COMPLEX_TYPES:
                    path[-1] = str(idx)
                    self._recurse(val, path)
        path.pop()


class EntitiesProcessor:
    def __init__(self, processor: Processor, data: dict):
        self.normalize_pos = processor.normalize_pos
        self.sort_keys = processor.sort_keys
        self.sort_entities = processor.sort_entities
        self.remove_entity_number = processor.remove_entity_number
        self.use_rel_ids = processor.use_rel_ids
        self.generate_ids = processor.generate_ids
        self.data = data
        self.entity_ids: Dict[EID, Entity] = {}
        self.position_to_entity_id: Dict[Position, EID] = {}
        # If these values are non-zero, positions will be de-shifted to original
        self.shift_x = -self.data.get('shift_x', 0)
        self.shift_y = -self.data.get('shift_y', 0)
        if self.normalize_pos:
            # If normalizing, the original data must not have had these shifts
            assert self.shift_x == 0
            assert self.shift_y == 0

    def process(self, path):
        entities = self.data['entities']
        if self.normalize_pos:
            self.shift_x = self.calc_coordinate_shift(entities, "x")
            self.shift_y = self.calc_coordinate_shift(entities, "y")
            if (self.shift_x, self.shift_y) != (0, 0):
                self.data['shift_x'] = self.shift_x
                self.data['shift_y'] = self.shift_y
        else:
            self.data.pop("shift_x", None)
            self.data.pop("shift_y", None)
        if self.sort_entities:
            # Sort blueprint entities by their combined x,y position
            entities.sort(key=lambda v: position_to_morton_number(v.get("position")))
        missing_ids = []
        for idx, entity_data in enumerate(entities):
            path[-1] = str(idx)
            # Save and possibly remove entity_id values
            eid = self._process_entity(entity_data, path)
            if eid is None:
                missing_ids.append(idx)
        if self.generate_ids:
            new_id = EID(1)
            for idx in missing_ids:
                path[-1] = str(idx)
                while new_id in self.entity_ids:
                    new_id += 1
                self._process_entity(entities[idx], path, new_id)
        for idx, entity_data in enumerate(entities):
            path[-1] = str(idx)
            # Switch between entity_id and entity_rel (relative position)
            self._update_relative_ids(entity_data["entity_number"], entity_data)
            if self.remove_entity_number:
                del entity_data["entity_number"]
            if self.sort_keys:
                self._recurse_sort(entity_data)

    def _process_entity(self, entity_data: dict, path: List[str], new_id: Optional[EID] = None) -> Optional[EID]:
        # Validate entity_number - must be unique in the blueprint entities list
        def path_str():
            return ".".join(path)

        eid = entity_data.get("entity_number")
        if eid is None:
            if not self.generate_ids:
                raise ValueError(f"Missing entity_number in {path_str()}")
            if new_id is None:
                return None
            # Entity number is created as a first key by Factorio, keep it consistent
            tmp = entity_data.copy()
            entity_data.clear()
            entity_data["entity_number"] = new_id
            entity_data.update(tmp)
            eid = new_id
        else:
            assert new_id is None

        if eid < 1:
            raise ValueError(f"Invalid entity_number {eid} in {path_str()}")
        if eid in self.entity_ids:
            raise ValueError(f"Duplicate entity_number {eid} in {self.entity_ids[eid].path} and {path_str()}")
        # Validate position - must have x,y numbers, and be unique in the blueprint entities
        position = entity_data.get("position")
        if position is None:
            raise ValueError(f"Missing position in {path_str()}")
        x, y = position.get("x"), position.get("y")
        if type(x) not in NUMBER_TYPES or type(y) not in NUMBER_TYPES:
            raise ValueError(f"Unrecognized position object {to_json({position})} in {path_str()}")
        x -= self.shift_x
        y -= self.shift_y
        position["x"] = x
        position["y"] = y
        pos = Position((coord_to_int(x), coord_to_int(y)))
        name = entity_data.get("name")
        if pos in self.position_to_entity_id:
            # More than one entity at this position.
            # This could be a problem if there are any references to any of them.
            # The relative ID may need more data to distinguish it.
            eid = self.position_to_entity_id[pos]
            entity = self.entity_ids[eid]
            entity.names.append(name)
        else:
            self.entity_ids[eid] = Entity(path_str(), pos, [name])
            self.position_to_entity_id[pos] = eid
        return eid

    def _update_relative_ids(self, entity_number: EID, data: Any, parent_key: str = None) -> None:
        if type(data) == dict:
            for key, val in data.items():
                if type(val) in COMPLEX_TYPES:
                    self._update_relative_ids(entity_number, val, key)
            entity_id = data.get("entity_id")
            rel_id = data.get("entity_rel")
            if entity_id is not None:
                if rel_id is not None:
                    raise ValueError(f"Cannot have both entity_id and entity_rel in {entity_number}")
                # Validate referenced entity_id, even if we don"t use it
                rel_id = self.make_rel_id(entity_number, entity_id)
                if self.use_rel_ids:
                    del data["entity_id"]
                    data["entity_rel"] = rel_id
                    sort_dict(data)
            elif rel_id is not None:
                entity_id = self.parse_rel_id(entity_number, rel_id)
                if not self.use_rel_ids:
                    del data["entity_rel"]
                    data["entity_id"] = entity_id
                    sort_dict(data)
        elif type(data) == list:
            if len(data) > 0 and parent_key == "neighbours":
                list_is_int = all(type(v) == int for v in data)
                list_is_str = all(type(v) == str for v in data)
                if not list_is_str and not list_is_int:
                    raise ValueError(f"Invalid neighbour list {entity_number}: all values must be either ints or strs")
                if not self.generate_ids:
                    if not list_is_int:
                        raise ValueError(f"Invalid neighbour list {entity_number} - all values must be ints")
                if self.use_rel_ids != list_is_str:
                    # Convert entity IDs to relative IDs or vice versa
                    old_list = data.copy()
                    data.clear()
                    for val in old_list:
                        if self.use_rel_ids:
                            data.append(self.make_rel_id(entity_number, val))
                        else:
                            data.append(self.parse_rel_id(entity_number, val))
            else:
                for val in data:
                    if type(val) in COMPLEX_TYPES:
                        self._update_relative_ids(entity_number, val)

    def make_rel_id(self, entity_number: EID, entity_id: EID) -> str:
        assert type(entity_id) == int
        entity = self.entity_ids[entity_number]
        info = self.entity_ids.get(entity_id)
        if info is None:
            raise ValueError(f"Unrecognized entity ID {entity_id} in {entity.path}")
        if len(info.names) > 1:
            raise ValueError(f"Entity ID {entity_id} in {entity.path} is not unique at {entity.pos}. \n"
                             f"We never anticipated this to happen with a real Factorio blueprint, "
                             f"so please report it at https://github.com/nyurik/fatul/issues")
        x_diff = int_to_coord(info.pos[0] - entity.pos[0])
        y_diff = int_to_coord(info.pos[1] - entity.pos[1])
        return f"{x_diff},{y_diff}"

    def parse_rel_id(self, entity_number: EID, rel_id: str) -> EID:
        assert type(rel_id) == str
        entity = self.entity_ids[entity_number]
        rel_parts = rel_id.split(",", 2)
        if len(rel_parts) != 2:
            raise ValueError(f"Unrecognized relative ID {rel_id} in {entity.path}")
        pos = Position((entity.pos[0] + coord_to_int(float(rel_parts[0])),
                        entity.pos[1] + coord_to_int(float(rel_parts[1]))))
        entity_id = self.position_to_entity_id.get(pos)
        if entity_id is None:
            raise ValueError(f"No entities found for relative ID {rel_id} ({pos[0], pos[1]}) in {entity.path}")
        return entity_id

    def _recurse_sort(self, data: Any) -> None:
        if type(data) == dict:
            for val in data.values():
                if type(val) in COMPLEX_TYPES:
                    self._recurse_sort(val)
            sort_dict(data)
        elif type(data) == list:
            for val in data:
                if type(val) in COMPLEX_TYPES:
                    self._recurse_sort(val)

    @staticmethod
    def calc_coordinate_shift(entities: List[dict], coord: str):
        """Find the most "stable" value for the x or y position coordinate.
        First creates a histogram of all values, looks at the first 20%,
        and finds the biggest "jump", i.e. from 2,1,4,34,... -- the 34 would be it."""
        histogram = defaultdict(int)
        for entity in entities:
            position = entity.get("position")
            if position is None:
                continue  # any data validation is done later, no need to dup
            val = position.get(coord)
            if val is None:
                continue
            histogram[int(val)] += 1
        if not histogram:
            return 0
        histogram = list(histogram.items())
        min_entities = min((v[1] for v in histogram))
        max_entities = max((v[1] for v in histogram))
        threshold = min_entities + (max_entities - min_entities) / 4
        histogram.sort(key=lambda v: v[0])  # sort by position coordinate
        # Find first row/column which increases the number of entities by more than threshold
        return next((histogram[i] for i in range(len(histogram))
                     if (histogram[i][1] - (histogram[i - 1][1] if i > 0 else 0)) > threshold),
                    histogram[0])[0]


def sort_dict(data):
    """Sort dict in place.
    Order first by group (prefix) followed by the key name alphabetically.
    Put special keys like 'name' first, then simple values (strings/ints/...) then dicts/lists."""

    def _key_sorter(key: str):
        prefix = SORT_ORDER.get(key)
        if prefix is None:
            prefix = SORT_ORDER["_complex" if type(old_data[key]) in COMPLEX_TYPES else "_simple"]
        return prefix + key

    # Since Python 3.7+, dict key insertion order is officially preserved
    old_data = data.copy()
    data.clear()
    for k in sorted(old_data.keys(), key=_key_sorter):
        data[k] = old_data[k]


def position_to_morton_number(position):
    # Create a single interleaved number (Morton number) to use as a sorting key.
    # This approach tries to keep features that are nearby in the X,Y plane near each other in a list.
    # Adapted from http://graphics.stanford.edu/~seander/bithacks.html#InterleaveBMN
    if not position:
        return 0
    x, y = position.get("x"), position.get("y")
    if x is None or y is None:
        return 0

    def prepare_number(val):
        # Normalize to an unsigned 16 bit value
        val = min(max(coord_to_int(val) + (2 ** 15), 0), 2 ** 16 - 1)
        for shift, mask in [(8, 0x00FF00FF), (4, 0x0F0F0F0F), (2, 0x33333333), (1, 0x55555555)]:
            val = (val | (val << shift)) & mask
        return val

    return prepare_number(x) | (prepare_number(y) << 1)


def coord_to_int(val) -> int:
    res = round(val * COORD_MULTIPLIER)
    return res


def int_to_coord(val: int) -> Union[float, int]:
    res = float(val) / float(COORD_MULTIPLIER)
    return int(res) if res.is_integer() else res


def get_label(data: dict) -> str:
    key = get_non_index_key(data)
    return data[key].get("label", data[key].get("item", key))


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def to_json(data):
    return json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def to_pretty_json(data, compact=True):
    if compact:
        return "".join(_make_iterencode()(data, 0))
    else:
        return json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2)


def _make_iterencode():
    """This is a slightly modified version of the _make_iterencode function from the Python's core json module.
    It is modified to allow for a one-liner output for complex objects, if the objects are small enough."""

    # The _encoder is used for simple values (str, int, float) and to test the length of a complex one-line value.
    _encoder = json.JSONEncoder(ensure_ascii=False, check_circular=False, allow_nan=False,
                                separators=(", ", ": ")).encode
    _indent = " " * 2
    _item_separator = ","
    _key_separator = ": "

    def _encode_one_line(o):
        """Encode complex object using standard JSON encoder without line breaks,
        and test if the result is short enough."""
        # Possible optimization: estimate the result size by recursively adding string lengths and breaking early
        res = _encoder(o)
        return res if len(res) <= MAX_LINE_LENGTH else None

    def _iterencode_list(lst, _current_indent_level):
        if not lst:
            yield "[]"
            return
        buf = _encode_one_line(lst)
        if buf is not None:
            yield buf
            return
        _current_indent_level += 1
        newline_indent = "\n" + _indent * _current_indent_level
        separator = _item_separator + newline_indent
        buf = "[" + newline_indent
        first = True
        for value in lst:
            if first:
                first = False
            else:
                buf = separator
            if isinstance(value, str):
                yield buf + _encoder(value)
            elif value is None:
                yield buf + "null"
            elif value is True:
                yield buf + "true"
            elif value is False:
                yield buf + "false"
            elif isinstance(value, int):
                yield buf + _encoder(value)
            elif isinstance(value, float):
                yield buf + _encoder(value)
            else:
                yield buf
                if isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)
                yield from chunks
        _current_indent_level -= 1
        yield "\n" + _indent * _current_indent_level + "]"

    def _iterencode_dict(dct, _current_indent_level):
        if not dct:
            yield "{}"
            return
        buf = _encode_one_line(dct)
        if buf is not None:
            yield buf
            return
        _current_indent_level += 1
        newline_indent = "\n" + _indent * _current_indent_level
        item_separator = _item_separator + newline_indent
        yield "{" + newline_indent
        first = True
        for key, value in dct.items():
            if isinstance(key, str):
                pass
            elif isinstance(key, float):
                key = _encoder(key)
            elif key is True:
                key = "true"
            elif key is False:
                key = "false"
            elif key is None:
                key = "null"
            elif isinstance(key, int):
                key = _encoder(key)
            else:
                raise TypeError(f"keys must be str, int, float, bool or None, "
                                f"not {key.__class__.__name__}")
            if first:
                first = False
            else:
                yield item_separator
            yield _encoder(key)
            yield _key_separator
            if isinstance(value, str):
                yield _encoder(value)
            elif value is None:
                yield "null"
            elif value is True:
                yield "true"
            elif value is False:
                yield "false"
            elif isinstance(value, int):
                yield _encoder(value)
            elif isinstance(value, float):
                yield _encoder(value)
            else:
                if isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)
                yield from chunks
        _current_indent_level -= 1
        yield "\n" + _indent * _current_indent_level + "}"

    def _iterencode(o, _current_indent_level):
        if isinstance(o, str):
            yield _encoder(o)
        elif o is None:
            yield "null"
        elif o is True:
            yield "true"
        elif o is False:
            yield "false"
        elif isinstance(o, int):
            yield _encoder(o)
        elif isinstance(o, float):
            yield _encoder(o)
        elif isinstance(o, (list, tuple)):
            yield from _iterencode_list(o, _current_indent_level)
        elif isinstance(o, dict):
            yield from _iterencode_dict(o, _current_indent_level)
        else:
            raise TypeError(f"Object of type {o.__class__.__name__} "
                            f"is not JSON serializable")

    return _iterencode


if __name__ == "__main__":
    main()
