"""Encipherers.

This module includes classess and helpers to simulate individual rotors and
other components of the enigma machine.

A glyph is the readable alphabet of the machine. Ordinals (ord) are numeric
positions that represent either the glyph position in the alphabet or the
pin position of inputs and outputs

"""

A_BASE = ord("A")

IDENTITY_MAP_STRING = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def glyph_to_ord(glyph):
    """Turn a character into an ordinal where a or A is 0 and z or Z is 25."""
    result = ord(glyph.upper()) - A_BASE
    if 0 <= result <= 25:
        return result
    raise ValueError()

def ord_to_glyph(num):
    """Turn an ordinal into a character (0=A, 25=Z)."""
    if not (0 <= num <= A_BASE):
        raise ValueError()

    return chr(num + A_BASE).upper()


def glyph_pairs_to_map_string(glyph_pairs):
    """Take a list of glyph pairs and swap each pair in the identity map."""
    base_map = [glyph_to_ord(c) for c in IDENTITY_MAP_STRING]

    for glyph_a, glyph_b in glyph_pairs:
        base_map[glyph_to_ord(glyph_a)] = glyph_to_ord(glyph_b)
        base_map[glyph_to_ord(glyph_b)] = glyph_to_ord(glyph_a)

    return ''.join([ord_to_glyph(ord) for ord in base_map])


def rotate_list(input_list, num_rotations):
    """Shifts a list or a string (abcd -> dabc)."""
    return input_list[num_rotations:] + input_list[:num_rotations]


class Encipherer:
    """Base encoder that handles mapping of input glyphs and ords."""

    _ord_map = None
    _ord_map_inverse = None

    def __init__(self, map_string):
        """Initialize the encipherer with a map string of glyphs."""
        self.set_ord_map(map_string)

    def set_ord_map(self, map_string):
        """Take an glyph string and turn it into an array of ordinals.

        Maintain an internal reverse map for fast lookups.
        """
        self._ord_map = [glyph_to_ord(c) for c in map_string]
        self._ord_map_inverse = [
            self._ord_map.index(i) for i in range(len(self._ord_map))
        ]

    def transform(self, input_ord):
        """Get the output given an ord input."""
        return self._ord_map[input_ord % len(self._ord_map)]

    def invert(self, input_ord):
        """Get the reverse output given an ord input."""
        return self._ord_map_inverse[input_ord % len(self._ord_map)]


class Reflector(Encipherer):
    """A special encipherer with no added logical functionality. A Reflector
    differs physically from rotors, but not logically."""

class EntryDisc(Encipherer):
    """A special encipherer with no added functionality."""


class PlugBoard(Encipherer):
    """A special encipherer with no added mechanical behavior, but represents
    a component used to swap glyphs.
    """

    def __init__(self, glyph_pairs):
        """ Special constructor takes a list of pairs. Returns essentially
        and identity encipherer w/ the pairs swapped
        """
        map_string = glyph_pairs_to_map_string(glyph_pairs)
        self.set_ord_map(map_string)


class Rotor(Encipherer):
    """A special version of an Encipherer with an internal rotation state."""

    #: int : the ordinal of the current "visible" glyph
    _rotation = 0
    _notch_alignment = [0]
    _ring_alignment = 0
    _original_rotation = 0
    """list of int: the ordinal of the active glyph(s) when the notch is
    triggered.

    It can be a list of ordinals for multi-notch rotors.
    """

    def __init__(
        self,
        map_string,
        rotation_glyph="A",
        notch_alignment_glyphs=["A"],
        ring_alignment_glyph="A",
    ):
        """Initialize the rotor.

        Takes a map string plus optional rotation and notch_alignment.
        """
        self.set_ord_map(map_string)
        self._rotation = glyph_to_ord(rotation_glyph)
        self._notch_alignment = [
            glyph_to_ord(glyph) for glyph in notch_alignment_glyphs
        ]
        self._ring_alignment = glyph_to_ord(ring_alignment_glyph)
        self._original_rotation = self._rotation

    def transform(self, input_ord):
        """Get the output, but do not advance machine state."""
        # -1 = B
        # 0 = A
        # 1 = Z
        # 2 = ?
        # need to decide if "notch" is relative to "A", or relative to set char

        # if self._ord_map[0] == 1:
        #    ring = 1
        relative_position = self._ord_map[
            (input_ord + (self._rotation - self._ring_alignment)) % len(self._ord_map)
        ]

        # back-apply the rotation to put the output in the right (global) position
        # relative to the next ring
        return (relative_position - (self._rotation - self._ring_alignment)) % len(
            self._ord_map
        )

    def invert(self, input_ord):
        """Get the output, but do not advance machine state."""
        ring = 0
        # if self._ord_map[0] == 1:
        #    ring = 1

        relative_position = self._ord_map_inverse[
            (input_ord + (self._rotation - self._ring_alignment)) % len(self._ord_map)
        ]
        return (relative_position - (self._rotation - self._ring_alignment)) % len(
            self._ord_map
        )

    def set_position(self, input_glyph):
        """Set the rotor position based on an input character."""
        self._rotation = glyph_to_ord(input_glyph) % len(self._ord_map)

    def reset(self):
        """Reset the rotor to its initial input parameters."""
        self._rotation = self._original_rotation

    def advance(self):
        """Move the rotor one glyph forward."""
        self._rotation = (self._rotation + 1) % len(self._ord_map)

    def is_at_turnover(self):
        """Return True if the visible glyph matches notch alignment."""
        return self._rotation in self._notch_alignment
