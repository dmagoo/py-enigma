ROTOR_IDENTITY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Entry wheel (same for all known Enigma models)
ETW = ROTOR_IDENTITY

# Rotors I-V were used in Enigma I and M4.
# Rotors VI-VIII and the Greek wheels were added for the M4 (Navy).
ROTOR_I     = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_II    = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_III   = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
ROTOR_IV    = "ESOVPZJAYQUIRHXLNFTGKDCMWB"
ROTOR_V     = "VZBRGITYUPSDNHLXAWMJQOFECK"
ROTOR_VI    = "JPGVOUMFYQBENHZRDKASXLICTW"
ROTOR_VII   = "NZJHGRCXMYSWBOUFAIVLPEKQDT"
ROTOR_VIII  = "FKQHTLXOCBJSPDZRAMEWNIUYGV"

# Greek wheels occupy the 4th (leftmost) slot in the M4. They do not rotate.
GREEK_BETA  = "LEYJVCNIXWPBQMDRTAKZGFUHOS"
GREEK_GAMMA = "FSOKANUERHMBTIYCWLQPZXVGJD"

# Turnover positions: the letter visible in the window when the next rotor steps.
# Rotors VI, VII, and VIII have two notches.
TURNOVER_I     = ["Q"]
TURNOVER_II    = ["E"]
TURNOVER_III   = ["V"]
TURNOVER_IV    = ["J"]
TURNOVER_V     = ["Z"]
TURNOVER_VI    = ["Z", "M"]
TURNOVER_VII   = ["Z", "M"]
TURNOVER_VIII  = ["Z", "M"]

# Reflectors for Enigma I
REFLECTOR_UKW_A = "EJMZALYXVBWFCRQUONTSPIKHGD"
REFLECTOR_UKW_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
REFLECTOR_UKW_C = "FVPJIAOYEDRZXWGCTKUQSBNMHL"

# The M4 used physically thinner versions of UKW-B and UKW-C to make room for
# the 4th rotor. Same names historically, but different wiring.
REFLECTOR_UKW_B_M4 = "ENKQAUYWJICOPBLMDXZVFTHRGS"
REFLECTOR_UKW_C_M4 = "RDOBJNTKVEHMLFCWZAXGYIPSUQ"

# Rotors available per machine model
ENIGMA_I_ROTORS  = [ROTOR_I, ROTOR_II, ROTOR_III, ROTOR_IV, ROTOR_V]
ENIGMA_M4_ROTORS = [ROTOR_I, ROTOR_II, ROTOR_III, ROTOR_IV, ROTOR_V,
                    ROTOR_VI, ROTOR_VII, ROTOR_VIII]

# Commercial Enigma models (D, K) used a keyboard-layout entry wheel instead of identity.
ETW_QWERTY = "QWERTZUIOASDFGHJKPYXCVBNML"

# --- Enigma D / Enigma K (commercial, ~1926) --- UNVERIFIED: check wiring against a reference before use
ROTOR_D_I    = "LPGSZMHAEOQKVXRFYBUTNICJDW"
ROTOR_D_II   = "SLVGBTFXJQOHEWIRZYAMKPCNDU"
ROTOR_D_III  = "CJGDPSHKTURAWZXFMYNQOBVLIE"
REFLECTOR_D_UKW  = "IMETCGFRAYSQBZXWLHKDVUPOJN"
TURNOVER_D_I   = ["Y"]
TURNOVER_D_II  = ["E"]
TURNOVER_D_III = ["N"]

# Enigma K shares rotor wiring with Enigma D. Swiss K (Swiss military variant) has different
# rotor wiring — not added here pending a reliable source.

# --- Enigma T (Tirpitz, Japanese Navy) --- UNVERIFIED: check wiring against a reference before use
# Each rotor has 5 turnover notches — pass the full list to Rotor().
ETW_T        = "KZROUQHYAIGBLWVSTDXFPNMCJE"
ROTOR_T_I    = "KPTYUELOCVGRFQDANJMBSWHZXI"
ROTOR_T_II   = "UPHZLWEQMTDJXCAKSOIGVBYFNR"
ROTOR_T_III  = "QUDLYRFEKONVZAXWHMGPJBSICT"
ROTOR_T_IV   = "CIWTBKXNRESPFLYDAGVHQUOJZM"
ROTOR_T_V    = "UAXGISNJBVERDYLFZWTPCKOHMQ"
ROTOR_T_VI   = "XFUZGALVHCNYSEWQTDMRBKPIOJ"
ROTOR_T_VII  = "BJVFTXPLNAYOZIKWGDQERUCHSM"
ROTOR_T_VIII = "YMTPNZHWKODAJXELUQVGCBISRF"
TURNOVER_T_I    = ["W", "Z", "E", "K", "Q"]
TURNOVER_T_II   = ["W", "Z", "F", "L", "R"]
TURNOVER_T_III  = ["W", "Z", "G", "M", "S"]
TURNOVER_T_IV   = ["W", "Z", "J", "N", "T"]
TURNOVER_T_V    = ["Y", "C", "F", "K", "R"]
TURNOVER_T_VI   = ["X", "E", "I", "M", "Q"]
TURNOVER_T_VII  = ["Y", "C", "F", "K", "R"]
TURNOVER_T_VIII = ["X", "E", "I", "M", "Q"]
# REFLECTOR_T_UKW not added — wiring not recalled with sufficient confidence.

# --- Railway Enigma (Reichsbahn) --- UNVERIFIED: check wiring against a reference before use
ROTOR_RB_I    = "JGDQOXUSCAMIFRVTPNEWKBLZYH"
ROTOR_RB_II   = "NTZPSFBOKMWRCJDIVLAEYUXGHQ"
ROTOR_RB_III  = "JVIUBHTCDYAKZMPSWQLRNXOEGF"
REFLECTOR_RB_UKW = "QYHOGNECVPUZTFDJAXWMKISRBL"
TURNOVER_RB_I   = ["N"]
TURNOVER_RB_II  = ["E"]
TURNOVER_RB_III = ["Y"]
