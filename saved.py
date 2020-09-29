
A_BASE = ord('A')

def char_to_int(char):
    """Turn a character into an ordinal where a or A is 0 and z or Z is 25."""
    return ord(char.upper()) - A_BASE


def int_to_char(num):
    """Turn an ordinal into a character (0=A, 25=Z)."""
    return chr(num + A_BASE).upper()


class Reflector:
    int_map = None

    def __init__(self, map_string):
        """Instantiate a reflector based on a map string."""
        self.int_map = [char_to_int(c) for c in map_string]

    def transform(self, input_val):
        """Get the output, but do not advance machine state."""
        return self.int_map[input_val % len(self.int_map)]

class EntryDisc:
    """Works like a rotor, but is static in position."""

    int_map = None

    def __init__(self, map_string):
        self.int_map = [char_to_int(c) for c in map_string]
        self.int_map_inverse = [
            self.int_map.index(i) for i in range(len(self.int_map))
        ]

    def transform(self, input_val):
        """Get the output, but do not advance machine state."""
        return self.int_map[input_val % len(self.int_map)]

    def invert(self, input_val):
        """Get the output, but do not advance machine state."""
        return self.int_map_inverse[input_val % len(self.int_map)]

# TODO: entry disc and reflector are really the same... make them
# extend / use the same base.  Rotor can extend this

class Rotor:
    _int_map_initial = None
    _rot_initial = 0
    notch_alignment = 0
    int_map = None
    int_map_inverse = None
    rot = 0

    def __init__(self, map_string, rot_initial="A", notch_alignment="A"):
        """Implement a generic rotor.

        Notch offset is where the notch is relative to A.
        Note that this A+notch_alignment would signify the letter that
        is visible when the notch is activated. This doesn't mean
        that the notch is physically at this location of the dial.

        """
        self._int_map_initial = [char_to_int(i) for i in map_string]
        self._rot_initial = char_to_int(rot_initial)
        self._notch_alignment = char_to_int(notch_alignment)
        self.reset()

    def set_position(self, input_char):
        """Set the rotor position based on an input character."""
        self.rot = char_to_int(input_char) % len(self.int_map)

    def reset(self):
        """Reset the rotor to its initial input parameters."""
        self.int_map = self._int_map_initial.copy()
        # cache the map for faster lookup
        self.int_map_inverse = [
            self.int_map.index(i) for i in range(len(self.int_map))
        ]
        self.rot = self._rot_initial

    def advance(self):
        self.rot = (self.rot + 1) % len(self.int_map)

    def is_at_turnover(self):
        return self.rot == self._notch_alignment

    def transform(self, input_val):
        """Get the output, but do not advance machine state."""
        relative_position = self.int_map[
            (input_val + self.rot) % len(self.int_map)
        ]
        return (relative_position - self.rot) % len(self.int_map)

    def invert(self, input_val):
        """Get the output, but do not advance machine state."""
        relative_position = self.int_map_inverse[
            (input_val + self.rot) % len(self.int_map)
        ]
        return (relative_position - self.rot) % len(self.int_map)
