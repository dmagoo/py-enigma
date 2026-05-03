# py-enigma

A Python simulator of the Enigma cipher machine. The Enigma was an electromechanical rotor cipher device used extensively by Nazi Germany during World War II; its messages were broken by Allied cryptanalysts at Bletchley Park, famously with help from Alan Turing. This library models the physical signal path — entry disc, plugboard, rotors, and reflector — including historically accurate rotor wiring, turnover mechanics, and double-stepping behavior, for both the standard Enigma I and the four-rotor M4 Navy variant.

## Installation

```bash
pip install -e .
```

No runtime dependencies. Python 3.8+.

## Quick start

The example below decrypts a real M4 U-boat message. The machine is configured with the Greek Beta wheel, rotors V/VI/VIII, reflector UKW-C (thin), ring settings, and a 10-pair plugboard — matching a known historical intercept.

```python
from enigma import EnigmaMachine, Rotor, EntryDisc, Reflector, PlugBoard
from enigma.constants import *

m = EnigmaMachine(
    [
        Rotor(GREEK_BETA,  "I", [],            "A"),  # Greek wheel — no turnover notch
        Rotor(ROTOR_V,     "G", TURNOVER_V,    "A"),
        Rotor(ROTOR_VI,    "Z", TURNOVER_VI,   "E"),
        Rotor(ROTOR_VIII,  "Q", TURNOVER_VIII, "L"),
    ],
    Reflector(REFLECTOR_UKW_C_M4),
    EntryDisc(ETW),
    PlugBoard([
        ("A", "E"), ("B", "F"), ("C", "M"), ("D", "Q"), ("H", "U"),
        ("J", "N"), ("L", "X"), ("P", "R"), ("S", "Z"), ("V", "W"),
    ]),
)

plaintext = m.decode_string(
    "TWNHYAZGBILSHEWPGLBPQLWQEKITIAFGZHWIMCWDFXPAFEILQZWFNRFTTQHUOADVLR"
    "LGAOQKVLWLSJHWOFJJSLUVEYNRRAJAQDKQBGMFYCEVKPFJPKOWHHQZYZEQRTQIKKXIXTFPOEMI"
)
print(plaintext)
```

## API

### `EnigmaMachine`

```python
EnigmaMachine(rotor_list, reflector, entry_disc, plug_board=None)
```

| Method | Description |
|---|---|
| `decode_string(text)` | Encipher/decipher a full message. Spaces are ignored. |
| `next_glyph(char)` | Advance rotors and return the transformed character. |
| `transform_glyph(char)` | Transform without advancing (lookahead). |
| `set_rotor_positions(string)` | Set rotor positions, e.g. `"AAA"` or `"VGZ"`. |
| `reset()` | Return machine to its initial configuration. |

### `Rotor`

```python
Rotor(wiring, position="A", turnover_notches=[], ring_setting="A")
```

`wiring` is a 26-character string from `constants.py`. `turnover_notches` is a list of glyphs at which the next rotor steps; pass `[]` for Greek wheels, which have no notches.

### `Reflector` / `EntryDisc` / `PlugBoard`

```python
Reflector(wiring_string)
EntryDisc(wiring_string)
PlugBoard([("A", "B"), ("C", "D"), ...])   # list of letter-swap pairs
```

### Constants

Imported via `from enigma.constants import *`:

| Group | Names |
|---|---|
| Rotors (Enigma I) | `ROTOR_I` – `ROTOR_V`, `TURNOVER_I` – `TURNOVER_V` |
| Rotors (M4 Navy) | `ROTOR_VI` – `ROTOR_VIII`, `GREEK_BETA`, `GREEK_GAMMA` |
| Reflectors | `REFLECTOR_UKW_A/B/C`, `REFLECTOR_UKW_B_M4`, `REFLECTOR_UKW_C_M4` |
| Entry discs | `ETW`, `ETW_ENIGMA1` |

## Running tests

```bash
pytest
```

## Notes

- **Enigma is symmetric:** the same machine settings encrypt and decrypt. Feed ciphertext in and you get plaintext out.
- **No machine-model enforcement:** using a rotor from the wrong model still simulates correctly — just not historically accurately.
- **Ring settings:** the fourth argument to `Rotor()` offsets the internal wiring relative to the alphabet ring, independently of the displayed rotor position.
- **Multi-notch rotors:** rotors VI, VII, and VIII have two turnover notches (`Z` and `M`). `TURNOVER_VI/VII/VIII` reflect this.
