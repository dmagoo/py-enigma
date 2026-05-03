import argparse
import json
import sys
from pathlib import Path

from .machine import EnigmaMachine
from .encipherers import Rotor, EntryDisc, Reflector, PlugBoard
from .constants import (
    ROTOR_I, ROTOR_II, ROTOR_III, ROTOR_IV, ROTOR_V,
    ROTOR_VI, ROTOR_VII, ROTOR_VIII, GREEK_BETA, GREEK_GAMMA,
    TURNOVER_I, TURNOVER_II, TURNOVER_III, TURNOVER_IV, TURNOVER_V,
    TURNOVER_VI, TURNOVER_VII, TURNOVER_VIII,
    REFLECTOR_UKW_A, REFLECTOR_UKW_B, REFLECTOR_UKW_C,
    REFLECTOR_UKW_B_M4, REFLECTOR_UKW_C_M4,
    ETW,
)

ROTOR_MAP = {
    "I":     (ROTOR_I,     TURNOVER_I),
    "II":    (ROTOR_II,    TURNOVER_II),
    "III":   (ROTOR_III,   TURNOVER_III),
    "IV":    (ROTOR_IV,    TURNOVER_IV),
    "V":     (ROTOR_V,     TURNOVER_V),
    "VI":    (ROTOR_VI,    TURNOVER_VI),
    "VII":   (ROTOR_VII,   TURNOVER_VII),
    "VIII":  (ROTOR_VIII,  TURNOVER_VIII),
    "BETA":  (GREEK_BETA,  []),
    "GAMMA": (GREEK_GAMMA, []),
}

REFLECTOR_MAP = {
    "UKW-A":    REFLECTOR_UKW_A,
    "UKW-B":    REFLECTOR_UKW_B,
    "UKW-C":    REFLECTOR_UKW_C,
    "UKW-B-M4": REFLECTOR_UKW_B_M4,
    "UKW-C-M4": REFLECTOR_UKW_C_M4,
}

_DATA_DIR = Path(__file__).parent / "data"


def _load_named_config(name):
    with open(_DATA_DIR / "historical-configs.json") as f:
        for c in json.load(f):
            if c["name"] == name:
                return c
    return None


def _resolve_config(args):
    config = {}

    if args.config:
        config = _load_named_config(args.config)
        if config is None:
            with open(args.config) as f:
                config = json.load(f)

    if args.rotors:
        config["rotors"] = args.rotors
    if args.positions:
        config["positions"] = args.positions
    if args.rings:
        config["rings"] = args.rings
    if args.reflector:
        config["reflector"] = args.reflector
    if args.plugboard:
        config["plugboard"] = args.plugboard

    missing = {"rotors", "reflector"} - config.keys()
    if missing:
        print(f"error: missing required config: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return config


def _build_machine(config):
    rotors = config["rotors"]
    positions = config.get("positions", ["A"] * len(rotors))
    rings = config.get("rings", ["A"] * len(rotors))
    plugboard_pairs = config.get("plugboard", [])

    rotor_list = [
        Rotor(wiring, pos, turnovers, ring)
        for r, pos, ring in zip(rotors, positions, rings)
        for wiring, turnovers in [ROTOR_MAP[r.upper()]]
    ]

    reflector = Reflector(REFLECTOR_MAP[config["reflector"].upper()])
    plugboard = PlugBoard([(p[0], p[1]) for p in plugboard_pairs]) if plugboard_pairs else None

    return EnigmaMachine(rotor_list, reflector, EntryDisc(ETW), plugboard)


def _read_message(args):
    if args.input:
        return Path(args.input).read_text().strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return input("Message: ").strip()


def main():
    parser = argparse.ArgumentParser(prog="enigma", description="Enigma machine simulator")
    parser.add_argument("--config",    metavar="NAME_OR_PATH", help="named historical config or path to a JSON file")
    parser.add_argument("--rotors",    nargs="+", metavar="ROTOR",    help="rotor names in order, e.g. I II III")
    parser.add_argument("--positions", nargs="+", metavar="POS",      help="starting positions, e.g. A A A")
    parser.add_argument("--rings",     nargs="+", metavar="RING",     help="ring settings, e.g. A A A")
    parser.add_argument("--reflector", metavar="REFLECTOR",           help="reflector name, e.g. UKW-B")
    parser.add_argument("--plugboard", nargs="+", metavar="PAIR",     help="plugboard pairs, e.g. AE BF CM")
    parser.add_argument("--input",     metavar="FILE",                help="read message from file")

    args = parser.parse_args()
    config = _resolve_config(args)
    machine = _build_machine(config)
    print(machine.decode_string(_read_message(args)))
