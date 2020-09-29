"""Enigma machine simulator

The main engine that allows generic implementation of an enigma machine

# Wiring of components: https://www.cryptomuseum.com/crypto/enigma/wiring.htm
# A working simulator for verificaiton:
#  https://cryptii.com/pipes/enigma-machine
# A historical transmission for testing:
https://enigma.hoerenberg.com/index.php?cat=The%20U534%20messages&page=P1030660

# TODO: format for historical key sheets, and auto config

"""

from encipherers import glyph_to_ord, ord_to_glyph

class EnigmaMachine:
    """Base EnigmaMachine Class."""

    _rotor_list = None
    _reflector = None
    _entry_disc = None
    _plug_board = None

    #TODO: change constructor order?  Or maybe kwargs?
    def __init__(self, rotor_list, reflector, entry_disc, plug_board=None):
        """Initialize an EnigmaMachine with the necessary components."""
        self._rotor_list = rotor_list
        self._reflector = reflector
        self._entry_disc = entry_disc
        self._plug_board = plug_board

    def set_rotor_positions(self, rotor_string):
        """Take a string of glypes and set the rotor positions accordingly.

        The length of the string must match the number of rotors
        """
        if len(rotor_string) != len(self._rotor_list):
            raise "Rotor Count Mismatch"

        for i, rotor in enumerate(self._rotor_list):
            rotor.set_position(rotor_string[i])

    def advance(self):
        """Enigma rotors did not advance like an odometer as we'd expect.

        These rules apply:
        - The right rotor always steps.
        - If any rotor is at its turnover, it will step along with the rotor1
        - To its left (if there is one)
        - A rotor does not step more than once per character
        """
        # turn_map = [r.is_at_turnover() for r in reversed(self._rotor_list)]
        # for i in reversed(range(len(turn_map))):
        #   if turn_map[i]:
        #       self._rotor_list[i].advance()

        turn_map = [r.is_at_turnover() for r in reversed(self._rotor_list)]
        turn_map = [
            # i == 0 or turn_map[i-1] for i in reversed(range(len(turn_map)))
            i == 0 or turn_map[i - 1] or advance
            for i, advance in enumerate(turn_map)
        ]
        for i, advance in enumerate(reversed(turn_map)):
            if advance:
                self._rotor_list[i].advance()

        # self.print_rotors()

    def odometer_advance(self):
        """Advancement strategy works like an odometer."""
        advancing = True
        i = len(self._rotor_list) - 1
        while advancing and i > 0:
            rotor = self._rotor_list[i]
            rotor.advance()
            advancing = rotor.is_at_turnover()
            i = i - 1

    def transform_ord(self, input_ord):
        """Run an ordinal through all machinery and return output ord."""
        output = input_ord
        output = self._entry_disc.transform(output)
        if self._plug_board:
            output = self._plug_board.transform(output)

        for rotor in reversed(self._rotor_list):
            output = rotor.transform(output)

        output = self._reflector.transform(output)

        for rotor in self._rotor_list:
            output = rotor.invert(output)

        if self._plug_board:
            output = self._plug_board.transform(output)

        output = self._entry_disc.invert(output)
        return output

    def transform_glyph(self, input_glyph):
        """Get the output, but do not advance machine state."""
        output = self.transform_ord(glyph_to_ord(input_glyph))
        return ord_to_glyph(output)

    def next_glyph(self, input_glyph):
        """Advance the machine and get next output."""
        self.advance()
        return self.transform_glyph(input_glyph)

    def decode_string(self, input_val):
        """Run the simulation on an entire string."""
        return "".join([
            self.next_glyph(c) for c in input_val.replace(" ", "")
        ])

    def reset(self):
        """Reset the machine to the original state."""
        for rotor in self._rotor_list:
            rotor.reset()

    def print_rotors(self):
        """Print the current rotor rotation state as a string."""
        output = []
        for rotor in self._rotor_list:
            output.append(ord_to_glyph(rotor._rotation))
        print("".join(output))
