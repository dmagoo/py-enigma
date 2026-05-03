import unittest
from enigma import EnigmaMachine, Rotor, EntryDisc, Reflector, PlugBoard
from enigma.constants import *


class TestEnigmaMachine(unittest.TestCase):
    def test_enigma1_basic(self):
        # Well-known reference vector: AAAAA → BDZGO with rotors I/II/III, UKW-B, all positions A
        m = EnigmaMachine(
            [
                Rotor(ROTOR_I,   "A", TURNOVER_I),
                Rotor(ROTOR_II,  "A", TURNOVER_II),
                Rotor(ROTOR_III, "A", TURNOVER_III),
            ],
            Reflector(REFLECTOR_UKW_B),
            EntryDisc(ETW),
        )
        self.assertEqual(m.decode_string("AAAAA"), "BDZGO")

    def test_enigma1_symmetric(self):
        # Enigma is symmetric: encrypting the ciphertext with the same settings returns plaintext
        m = EnigmaMachine(
            [
                Rotor(ROTOR_I,   "A", TURNOVER_I),
                Rotor(ROTOR_II,  "A", TURNOVER_II),
                Rotor(ROTOR_III, "A", TURNOVER_III),
            ],
            Reflector(REFLECTOR_UKW_B),
            EntryDisc(ETW),
        )
        ciphertext = m.decode_string("HELLOWORLD")
        m.reset()
        self.assertEqual(m.decode_string(ciphertext), "HELLOWORLD")

    def test_reset(self):
        # Two runs from the same initial state must produce identical output
        m = EnigmaMachine(
            [
                Rotor(ROTOR_I,   "A", TURNOVER_I),
                Rotor(ROTOR_II,  "A", TURNOVER_II),
                Rotor(ROTOR_III, "A", TURNOVER_III),
            ],
            Reflector(REFLECTOR_UKW_B),
            EntryDisc(ETW),
        )
        first  = m.decode_string("AAAAAAAAAAA")
        m.reset()
        second = m.decode_string("AAAAAAAAAAA")
        self.assertEqual(first, second)

    def test_uboat_m4(self):
        # Real M4 U-boat intercept. Configuration and plaintext are historically documented.
        m = EnigmaMachine(
            [
                Rotor(GREEK_BETA,  "I", [],            "A"),
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
        self.assertTrue(plaintext.startswith("FXDXUUU"))


if __name__ == "__main__":
    unittest.main()
