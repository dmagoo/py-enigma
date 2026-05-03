import unittest, re
from enigma import Rotor, EntryDisc, Reflector, PlugBoard
from enigma.encipherers import (
    glyph_to_ord,
    ord_to_glyph,
    glyph_pairs_to_map_string,
    rotate_list,
)

IDENTITY_MAP_STRING = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class TestCalc(unittest.TestCase):
    def test_glyph_to_ord(self):
        self.assertEqual(glyph_to_ord("A"), 0)
        self.assertEqual(glyph_to_ord("a"), 0)
        self.assertEqual(glyph_to_ord("Z"), 25)
        self.assertEqual(glyph_to_ord("z"), 25)
        with self.assertRaises(ValueError):
            glyph = glyph_to_ord("#")

    def test_ord_to_glyph(self):
        self.assertEqual(ord_to_glyph(0), "A")
        self.assertEqual(ord_to_glyph(25), "Z")
        with self.assertRaises(ValueError):
            c = ord_to_glyph(99)

    def test_glyph_pairs_to_map_string(self):
        swap_string = "ZYCDEFGHIJKLMNOPQRSTUVWXBA"
        self.assertEqual(
            glyph_pairs_to_map_string([("z", "a"), ("b", "y")]), swap_string
        )
        self.assertEqual(
            glyph_pairs_to_map_string([("a", "z"), ("b", "y")]), swap_string
        )

    def test_rotate_list(self):
        self.assertEqual(
            rotate_list(IDENTITY_MAP_STRING, 4), "EFGHIJKLMNOPQRSTUVWXYZABCD"
        )
        self.assertEqual(
            rotate_list(IDENTITY_MAP_STRING, -4), "WXYZABCDEFGHIJKLMNOPQRSTUV"
        )
        self.assertEqual(rotate_list(IDENTITY_MAP_STRING, 0), IDENTITY_MAP_STRING)
        self.assertEqual(rotate_list(IDENTITY_MAP_STRING, 26), IDENTITY_MAP_STRING)
        self.assertEqual(rotate_list(IDENTITY_MAP_STRING, 52), IDENTITY_MAP_STRING)


if __name__ == "__main__":
    unittest.main()
