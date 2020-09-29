
from enigma import EnigmaMachine
from encipherers import Rotor, EntryDisc, Reflector, PlugBoard
from constants import *

def chunk_string(input_string, chunk_size=5, space_char=" "):
    return space_char.join(
        [
            input_string[i : i + chunk_size]
            for i in range(0, len(input_string), chunk_size)
        ]
    )


def makeEnigma1(rotor1, rotor2, rotor3, reflector, plug_board=None):
    return EnigmaMachine(
        [rotor1, rotor2, rotor3], reflector, EntryDisc(ETW_ENIGMA1), plug_board
    )


def makeEnigma4(rotor1, rotor2, rotor3, reflector, plug_board=None):
    return EnigmaMachine(
        [rotor1, rotor2, rotor3], reflector, EntryDisc(ETW_ENIGMA1), plug_board
    )


def basicTest():
    m = makeEnigma1(
        Rotor(ROTOR_IDENTITY),
        Rotor(ROTOR_IDENTITY),
        Rotor(ROTOR_IDENTITY),
        REFLECTOR_IDENTITY,
    )
    output = []
    output.append(m.transform_glyph("a"))
    output.append(m.transform_glyph("b"))
    output.append(m.transform_glyph("c"))
    output.append(m.transform_glyph("x"))
    output.append(m.transform_glyph("y"))
    output.append(m.transform_glyph("z"))
    return output


def simpleAdvancementTest():
    m = EnigmaMachine(
        [Rotor(ROTOR_IDENTITY)], Reflector(REFLECTOR_IDENTITY), EntryDisc(ETW_ENIGMA1)
    )
    return [m.next_glyph(c) for c in "aaaaaa"]


def testReset():
    m = EnigmaMachine(
        [Rotor(ROTOR_IDENTITY)], Reflector(REFLECTOR_IDENTITY), EntryDisc(ETW_ENIGMA1)
    )
    print("first run with aaaaaa")
    print(m.decode_string("aaaaaa"))
    print("second run with aaaaaa")
    print(m.decode_string("aaaaaa"))
    print("third run with aaaaaa after reset")
    m.reset()
    print(m.decode_string("aaaaaa"))
    return []


def enigma1DefaultTest():
    input_val = "AAAAA"
    expected = "BDZGO"
    m = makeEnigma1(
        Rotor(ROTOR_ENIGMA1_1),
        Rotor(ROTOR_ENIGMA1_2),
        Rotor(ROTOR_ENIGMA1_3),
        Reflector(REFLECTOR_ENIGMA1_UKW_B),
    )
    m.reset()
    print("Applying", input_val)
    print("Expecting", expected)
    output = m.decode_string(input_val)
    print("got", output)


def enigma1DefaultWithAdvancementTest():
    # input_val = 'bdzgo wcxlt ksbtm cdlpb muqof xyhcx tgyjf linhn xshiu nthie yizmq uwydp oultu wbukv mmwrp qewqq pgbdk obibe'
    # input_val = 'bdzgo wcxlt ksbtm cdlpb muqof xyhcx tgyjf'
    input_val = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    # input_val = 'bjelr qzvjw arxsn bxors tncfm eyyaq usqsw sqypa jckcz ejuml alzxgkogvxhnvicpcztmqkhddsqu'
    # input_val = 'BJELR QZVJW ARXSN BXORS TNCFM EYYAQ USQSW SQYPA JCKCZ EJUDS IUPPT CCBZU HRQRP WJBPC AAZPJ ZZW'
    # expected = 'asdfadsf'
    # input_val = ROTOR_ENIGMA1_1
    # input_val = 'a'
    m = makeEnigma1(
        Rotor(ROTOR_ENIGMA1_1, "A", "Q"),
        Rotor(ROTOR_ENIGMA1_2, "A", "E"),
        Rotor(ROTOR_ENIGMA1_3, "A", "V"),
        Reflector(REFLECTOR_ENIGMA1_UKW_B),
        # PlugBoard([("U","B")])
        PlugBoard([]),
    )
    m.reset()
    # m.print_rotors()
    print("Applying", input_val)
    # print('Expecting', expected)
    output = m.decode_string(input_val)
    # m.print_rotors()
    print("got:")
    print(chunk_string(chunk_string(output), 18, "\n"))


def setRotorTest():
    m = EnigmaMachine(
        [Rotor(ROTOR_IDENTITY), Rotor(ROTOR_IDENTITY)],
        Reflector(REFLECTOR_IDENTITY),
        EntryDisc(ETW_ENIGMA1),
    )
    m.print_rotors()
    m.set_rotor_positions("GA")
    m.print_rotors()


def tryUBoat():
    # RING settings for this machine: AAEL
    m = EnigmaMachine(
        [
            # TODO: greek component did not have nothces, allow NONE
            Rotor(GREEK_ENIGMAM4_BETA, "I", (), "A"),
            Rotor(ROTOR_ENIGMAM4_5, "G", ["Z"], "A"),
            Rotor(ROTOR_ENIGMAM4_6, "Z", ("Z", "M"), "E"),
            Rotor(ROTOR_ENIGMAM4_8, "Q", ("Z", "M"), "L"),
        ],
        Reflector(REFLECTOR_ENIGMAM4_UKW_C),
        EntryDisc(ETW_ENIGMA1),
        PlugBoard(
            [
                ("A", "E"),
                ("B", "F"),
                ("C", "M"),
                ("D", "Q"),
                ("H", "U"),
                ("J", "N"),
                ("L", "X"),
                ("P", "R"),
                ("S", "Z"),
                ("V", "W"),
            ]
        ),
    )

    output = m.decode_string(
        "TWNHYAZGBILSHEWPGLBPQLWQEKITIAFGZHWIMCWDFXPAFEILQZWFNRFTTQHUOADVLRLGAOQKVLWLSJHWOFJJSLUVEYNRRAJAQDKQBGMFYCEVKPFJPKOWHHQZYZEQRTQIKKXIXTFPOEMI"
    )
    # got = "GORGFIUHEDDEUAYOMPWUTOXIDHFGAZBAFWRTJXMTHCIVLCEKZNEHGJGYQSQWMTSZQBBVYWZMPCDPZZJTAVNTCISCGWTZZMZDLMFZGWOPJBFBTJKXFRSOIOFRSIRCVPLQBDCROJKNNXTF"
    # print(m.decode_string(got))
    # expects = "FXDXUUUOSTYFUNCQUUUFXWTTXVVVUUUEINSEINSNULDREIKKEISELEKKXXISTSECHSSTUENDLICHESDOCKENVORMITTAGSAMDREIXFUNFXINRENDSBURGGEMXFXDXUUUOSTMOEGLICHL"
    print(output)


def main():
    # print("basicTest")
    # print(''.join(basicTest()))
    # print("simpleAdvancementTest")
    # print(''.join(simpleAdvancementTest()))
    # print("simpleAdvancementTestString")
    # testReset()
    # enigma1DefaultTest()
    # enigma1DefaultWithAdvancementTest()
    # setRotorTest()
    tryUBoat()


if __name__ == "__main__":
    main()
