# py-enigma

A Python simulator of the Enigma cipher machine. The Enigma was an electromechanical rotor cipher device used extensively by Nazi Germany during World War II; its messages were broken by Allied cryptanalysts at Bletchley Park, famously with help from Alan Turing. This library models the physical signal path — entry disc, plugboard, rotors, and reflector — including historically accurate rotor wiring, turnover mechanics, and double-stepping behavior, for both the standard Enigma I and the four-rotor M4 Navy variant.

## Setup

Requires Python 3.8+.

```bash
python -m venv env
source env/bin/activate       # Windows: env\Scripts\activate
pip install -e .
```

## Usage

```bash
enigma [--config NAME_OR_PATH] [--rotors ...] [--positions ...] [--rings ...] [--reflector ...] [--plugboard ...] [--input FILE]
```

| Flag | Description |
|------|-------------|
| `--config NAME_OR_PATH` | Load a named historical config or a path to a JSON config file |
| `--rotors I II III` | Rotor names in left-to-right order |
| `--positions A A A` | Starting position for each rotor |
| `--rings A A A` | Ring setting for each rotor |
| `--reflector UKW-B` | Reflector name |
| `--plugboard AE BF CM` | Plugboard swap pairs |
| `--input FILE` | Read message from a file instead of stdin |

**Rotors:** `I` `II` `III` `IV` `V` `VI` `VII` `VIII` `BETA` `GAMMA`

**Reflectors:** `UKW-A` `UKW-B` `UKW-C` `UKW-B-M4` `UKW-C-M4`

Individual flags override values from `--config`, so you can load a historical config and adjust a single setting without respecifying everything.

Message input is read from `--input`, piped stdin, or typed interactively if neither is provided.

Enigma is symmetric — the same settings encrypt and decrypt. Feed in ciphertext and you get plaintext out.

## Examples

```bash
# Named historical config — U-boat M4 intercept, November 1942
enigma --config uboat-p1030660 --input message.txt

# Pipe input
echo "HELLOWORLD" | enigma --config uboat-p1030660

# Manual config — Enigma I, rotors I/II/III, UKW-B
enigma --rotors I II III --positions A A A --reflector UKW-B

# Load a historical config and override the starting positions
enigma --config enigma1-default --positions Q E V

# Custom JSON config file
enigma --config ~/my-machine.json --input ciphertext.txt

# Full M4 config via individual args
enigma --rotors BETA V VI VIII --positions I G Z Q --rings A A E L --reflector UKW-C-M4 --plugboard AE BF CM DQ HU JN LX PR SZ VW
```

## Historical configs

Named configs are stored in `src/enigma/data/historical-configs.json`.

| Name | Description |
|------|-------------|
| `uboat-p1030660` | U-boat M4 intercept, U-534, November 1942 |
| `enigma1-default` | Enigma I, rotors I/II/III, all positions A, UKW-B |

## Custom config format

A user-supplied JSON config is a single object with the same keys:

```json
{
  "rotors":    ["I", "II", "III"],
  "positions": ["A", "A", "A"],
  "rings":     ["A", "A", "A"],
  "reflector": "UKW-B",
  "plugboard": ["AE", "BF"]
}
```

`positions`, `rings`, and `plugboard` are optional and default to all-A and no swaps respectively.

## API

```python
from enigma import EnigmaMachine, Rotor, EntryDisc, Reflector, PlugBoard
from enigma.constants import *

m = EnigmaMachine(
    [
        Rotor(GREEK_BETA,  "I", [],            "A"),
        Rotor(ROTOR_V,     "G", TURNOVER_V,    "A"),
        Rotor(ROTOR_VI,    "Z", TURNOVER_VI,   "E"),
        Rotor(ROTOR_VIII,  "Q", TURNOVER_VIII, "L"),
    ],
    Reflector(REFLECTOR_UKW_C_M4),
    EntryDisc(ETW),
    PlugBoard([("A","E"), ("B","F"), ("C","M"), ("D","Q"), ("H","U"),
               ("J","N"), ("L","X"), ("P","R"), ("S","Z"), ("V","W")]),
)

plaintext = m.decode_string("TWNHYAZGBILSHEWPGLBPQLWQ...")
```

| Method | Description |
|--------|-------------|
| `decode_string(text)` | Encipher/decipher a full message. Spaces are ignored. |
| `next_glyph(char)` | Advance rotors and return the transformed character. |
| `transform_glyph(char)` | Transform without advancing (lookahead). |
| `set_rotor_positions(string)` | Set rotor positions, e.g. `"AAA"`. |
| `reset()` | Return machine to its initial configuration. |

## enigma-utils

A second command ships with the same package for managing historical key-sheet data.

```bash
enigma-utils scan compile data/scans/scan-luftwaffe-2744.json
enigma-utils scan compile --all        # compile every file in data/scans/
enigma-utils scan compile --all -v     # verbose: show per-entry detail
```

Scan files are raw JSON transcriptions of historical key sheets stored in `data/scans/`. Compiled codebooks land in `data/codebooks/` and are tracked by git. Before overwriting an existing codebook a timestamped backup is written to `data/codebooks/backups/` (not tracked).

| Flag | Description |
|------|-------------|
| `--all` | Compile every scan file in `data/scans/` |
| `-v / --verbose` | Show per-entry backup and patch detail |

## Running tests

```bash
pytest
```

## Notes

- **Ring settings** offset the internal wiring relative to the alphabet ring, independently of the displayed rotor position.
- **Multi-notch rotors:** VI, VII, and VIII have two turnover notches (`Z` and `M`). Greek wheels (Beta, Gamma) have none.
- **No machine-model enforcement:** using a rotor from the wrong model still simulates correctly, just not historically accurately.
