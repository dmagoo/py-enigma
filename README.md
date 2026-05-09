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

### Interactive mode

Pass `--interactive` to enter the curses TUI. Type letters to encipher in real time; the rotor positions update with each keypress. Commands are entered with a leading `/`:

| Command | Description |
|---------|-------------|
| `/rotors` | Show current rotor order |
| `/rotors I II III` | Change rotor order (rebuilds machine, clears input) |
| `/rotors reset` | Reset rotor positions to starting positions |
| `/rings` | Show current ring settings |
| `/rings S G L` | Set ring settings (rebuilds machine, clears input) |
| `/positions` | Show current rotor positions |
| `/positions A B C` | Set rotor positions |
| `/positions reset` | Reset rotor positions to starting positions |
| `/reflector` | Show current reflector |
| `/reflector UKW-B` | Set reflector (rebuilds machine, clears input) |
| `/plug` | Show current plugboard pairs |
| `/plug AE BF CM` | Replace all plugboard pairs |
| `/plug clear` | Remove all plugboard pairs |
| `/plug reset` | Restore plugboard to the pairs set at startup |
| `/reset` | Reset rotor positions (plugboard unchanged) |
| `/state` | Show full current config |
| `/help` | Show command reference |
| `/exit` | Quit |

Backspace removes the last display character (rotor state has already advanced — it cannot be undone). Enter clears the input line only — output accumulates so you can read it. Up/down arrow cycles through command history. Ctrl+D quits.

`--interactive` can be launched with no arguments; the machine defaults to rotors I II III and reflector UKW-B, which can be changed from inside the session.

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

## Indicator procedure

The day's codebook set the machine configuration (rotors, rings, reflector, plugboard) — the same for every message that day. The starting rotor position was chosen fresh by the operator per message and communicated to the receiver via an *indicator* embedded in the message header.

Standard Kriegsmarine procedure:
1. Set rotors to the daily *ground setting* (Grundstellung)
2. Encipher a chosen 3-letter message key — the output is the indicator
3. Transmit the indicator in the message header
4. Set rotors to the original message key and encipher the body

The receiver reverses step 2 to recover the message key, then decrypts the body.

A typical header looked like: `U35 DE W7 0630 = 46 = WTG PLT =` — where `WTG` is the ground setting and `PLT` is the enciphered message key.

```
# Set up the machine with the day's codebook settings
enigma --interactive
/rotors VIII II IV
/rings S G L
/reflector UKW-B
/plug BD CO EI GL JS KT NV PM QR WZ

# Step 1: decipher the indicator — set rotors to ground setting, type the indicator
/positions W T G
PLT
# Output line shows OOS — the actual message starting positions

# Step 2: set rotors to the derived positions and decrypt the body
/positions O O S
MUUQJZVQLORVMCOLYKXE...
```

## Notes

- **Ring settings** offset the internal wiring relative to the alphabet ring, independently of the displayed rotor position.
- **Multi-notch rotors:** VI, VII, and VIII have two turnover notches (`Z` and `M`). Greek wheels (Beta, Gamma) have none.
- **No machine-model enforcement:** using a rotor from the wrong model still simulates correctly, just not historically accurately.
