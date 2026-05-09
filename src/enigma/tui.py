"""Curses-based interactive TUI for the Enigma machine simulator."""

import curses

_VALID_ROTORS     = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "BETA", "GAMMA"}
_VALID_REFLECTORS = {"UKW-A", "UKW-B", "UKW-C", "UKW-B-M4", "UKW-C-M4"}

_HELP = (
    "/rotors [I II III | reset]   show or set rotor order  |  "
    "/rings [A A A]   show or set ring settings  |  "
    "/positions [A A A | reset]   show or set positions  |  "
    "/reflector [UKW-B]   show or set reflector  |  "
    "/plug [AE BF | clear | reset]   show, replace, clear, or reset plugboard  |  "
    "/reset   reset positions  |  /state   show full config  |  /exit   quit"
)

_CMDBAR_NORMAL = (
    "  /rotors   /rings   /positions   /reflector   /plug   /reset   /state   /help   /exit"
    "   |   Enter: clear input   Backspace: undo display"
)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _draw_header(win, config):
    rotors = "  ".join(config["rotors"])
    rings  = "  ".join(config.get("rings") or [])  or "A A A"
    reflector = config.get("reflector", "")
    plugboard = config.get("plugboard", [])
    plug_str = " ".join(plugboard) if plugboard else "none"
    h, w = win.getmaxyx()
    line = f"  ENIGMA  |  Rotors: {rotors}  |  Rings: {rings}  |  Reflector: {reflector}  |  Plugboard: {plug_str}"
    win.addstr(0, 0, line[:w - 1], curses.A_BOLD)
    win.hline(1, 0, "-", w - 1)


def _draw_rotors(win, machine, row):
    positions = [chr(r._rotation + ord("A")) for r in machine._rotor_list]
    x = 2
    for pos in positions:
        win.addstr(row,     x, "+---+")
        win.addstr(row + 1, x, f"| {pos} |", curses.A_BOLD | curses.A_REVERSE)
        win.addstr(row + 2, x, "+---+")
        x += 7


def _draw_io(win, input_buf, output_buf, row):
    h, w = win.getmaxyx()
    max_len = w - 12
    win.addstr(row,     2, "Input : ")
    win.addstr(row,     10, input_buf[-max_len:] if len(input_buf) > max_len else input_buf)
    win.addstr(row + 1, 2, "Output: ")
    win.addstr(row + 1, 10,
               (output_buf[-max_len:] if len(output_buf) > max_len else output_buf),
               curses.A_BOLD)


def _draw_status(win, status, row):
    h, w = win.getmaxyx()
    win.move(row, 0)
    win.clrtoeol()
    if status:
        win.addstr(row, 2, status[:w - 3], curses.A_DIM)


def _draw_cmdbar(win, mode, cmd_buf):
    h, w = win.getmaxyx()
    win.move(h - 1, 0)
    win.clrtoeol()
    win.hline(h - 2, 0, "-", w - 1)
    if mode == "command":
        win.addstr(h - 1, 0, f"/{cmd_buf}_", curses.A_REVERSE)
    else:
        win.addstr(h - 1, 0, _CMDBAR_NORMAL[:w - 1], curses.A_DIM)


# ---------------------------------------------------------------------------
# Command handling
# ---------------------------------------------------------------------------

def _current_positions(machine):
    return [chr(r._rotation + ord("A")) for r in machine._rotor_list]


def _handle_command(cmd, machine, config, initial_plugboard, rebuild_fn):
    """Execute a slash command.

    Returns (status_message, should_quit, clear_io, new_machine).
    new_machine is None unless the machine was rebuilt.
    """
    parts = cmd.strip().split()
    if not parts:
        return ("", False, False, None)

    verb = parts[0].lower()
    args = parts[1:]

    # -- exit ----------------------------------------------------------------
    if verb == "exit":
        return ("", True, False, None)

    # -- reset (positions only) ----------------------------------------------
    elif verb == "reset":
        machine.reset()
        return ("positions reset.", False, True, None)

    # -- state ---------------------------------------------------------------
    elif verb == "state":
        rotors = "  ".join(config["rotors"])
        rings  = " ".join(config.get("rings") or []) or "A A A"
        plug   = " ".join(config.get("plugboard", [])) or "none"
        pos    = "".join(_current_positions(machine))
        return (f"rotors: {rotors}  rings: {rings}  pos: {pos}  reflector: {config.get('reflector','')}  plug: {plug}", False, False, None)

    # -- help ----------------------------------------------------------------
    elif verb in ("help", "h", "?"):
        return (_HELP, False, False, None)

    # -- rotors --------------------------------------------------------------
    elif verb == "rotors":
        if not args:
            return (f"rotors: {' '.join(config['rotors'])}", False, False, None)
        if args[0].lower() == "reset":
            machine.reset()
            return ("positions reset.", False, True, None)
        # set rotor order
        if rebuild_fn is None:
            return ("cannot change rotors: no rebuild function available", False, False, None)
        new_rotors = [r.upper() for r in args]
        invalid = [r for r in new_rotors if r not in _VALID_ROTORS]
        if invalid:
            return (f"unknown rotor(s): {' '.join(invalid)}", False, False, None)
        config["rotors"] = new_rotors
        config["positions"] = ["A"] * len(new_rotors)
        new_machine = rebuild_fn(config)
        return (f"rotors set: {' '.join(new_rotors)}", False, True, new_machine)

    # -- rings ---------------------------------------------------------------
    elif verb == "rings":
        if not args:
            rings = config.get("rings") or []
            return (f"rings: {' '.join(rings) or 'A A A (default)'}", False, False, None)
        if rebuild_fn is None:
            return ("cannot change rings: no rebuild function available", False, False, None)
        new_rings = [r.upper() for r in args]
        if any(len(r) != 1 or not r.isalpha() for r in new_rings):
            return ("ring settings must be single letters A-Z, e.g. /rings S G L", False, False, None)
        if len(new_rings) != len(machine._rotor_list):
            return (f"need {len(machine._rotor_list)} ring setting(s), got {len(new_rings)}", False, False, None)
        config["rings"] = new_rings
        new_machine = rebuild_fn(config)
        return (f"rings set: {' '.join(new_rings)}", False, True, new_machine)

    # -- reflector -----------------------------------------------------------
    elif verb == "reflector":
        if not args:
            return (f"reflector: {config.get('reflector', 'none')}", False, False, None)
        if rebuild_fn is None:
            return ("cannot change reflector: no rebuild function available", False, False, None)
        name = args[0].upper()
        if name not in _VALID_REFLECTORS:
            return (f"unknown reflector: {name}  choices: {' '.join(sorted(_VALID_REFLECTORS))}", False, False, None)
        config["reflector"] = name
        new_machine = rebuild_fn(config)
        return (f"reflector set: {name}", False, True, new_machine)

    # -- positions -----------------------------------------------------------
    elif verb == "positions":
        n = len(machine._rotor_list)
        if not args:
            pos = " ".join(_current_positions(machine))
            return (f"positions: {pos}", False, False, None)
        if args[0].lower() == "reset":
            machine.reset()
            return ("positions reset.", False, True, None)
        # set positions — accept either space-separated letters or a single string
        pos_str = "".join(args).upper()
        if len(pos_str) != n:
            return (f"need {n} position(s), got {len(pos_str)}", False, False, None)
        if not pos_str.isalpha():
            return ("positions must be letters A-Z", False, False, None)
        machine.set_rotor_positions(pos_str)
        config["positions"] = list(pos_str)
        return (f"positions set: {' '.join(pos_str)}", False, False, None)

    # -- plug ----------------------------------------------------------------
    elif verb == "plug":
        if not args:
            plug = " ".join(config.get("plugboard", [])) or "none"
            return (f"plugboard: {plug}", False, False, None)
        if args[0].lower() == "clear":
            if rebuild_fn is None:
                return ("cannot change plugboard: no rebuild function available", False, False, None)
            config["plugboard"] = []
            new_machine = rebuild_fn(config)
            return ("plugboard cleared.", False, True, new_machine)
        if args[0].lower() == "reset":
            if rebuild_fn is None:
                return ("cannot change plugboard: no rebuild function available", False, False, None)
            config["plugboard"] = list(initial_plugboard)
            new_machine = rebuild_fn(config)
            return ("plugboard reset.", False, True, new_machine)
        # set pairs
        if rebuild_fn is None:
            return ("cannot change plugboard: no rebuild function available", False, False, None)
        new_pairs = [p.upper() for p in args]
        bad = [p for p in new_pairs if len(p) != 2 or not p.isalpha()]
        if bad:
            return (f"invalid pair(s): {' '.join(bad)} — use two letters, e.g. AE BF", False, False, None)
        config["plugboard"] = new_pairs
        new_machine = rebuild_fn(config)
        return (f"plugboard set: {' '.join(new_pairs)}", False, True, new_machine)

    # -- unknown -------------------------------------------------------------
    else:
        return (f"unknown command: /{verb}  (type /help)", False, False, None)


# ---------------------------------------------------------------------------
# Main TUI loop
# ---------------------------------------------------------------------------

def _tui_main(stdscr, machine, config, initial_plugboard, rebuild_fn):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    input_buf  = ""
    output_buf = ""
    mode       = "normal"
    cmd_buf    = ""
    status     = ""
    cmd_history    = []
    cmd_history_idx = None

    ROTOR_ROW  = 3
    STATUS_ROW = 7
    IO_ROW     = 9

    def redraw():
        stdscr.clear()
        _draw_header(stdscr, config)
        _draw_rotors(stdscr, machine, ROTOR_ROW)
        _draw_status(stdscr, status, STATUS_ROW)
        _draw_io(stdscr, input_buf, output_buf, IO_ROW)
        _draw_cmdbar(stdscr, mode, cmd_buf)
        stdscr.refresh()

    redraw()

    while True:
        try:
            ch = stdscr.getch()
        except KeyboardInterrupt:
            break

        if mode == "normal":
            if ch == ord("/"):
                mode = "command"
                cmd_buf = ""
                status = ""

            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                if input_buf:
                    input_buf  = input_buf[:-1]
                    output_buf = output_buf[:-1]

            elif ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                input_buf = ""
                status = ""

            elif ch == 4:  # Ctrl+D
                break

            elif 32 <= ch <= 126:
                c = chr(ch).upper()
                if c.isalpha():
                    out = machine.next_glyph(c)
                    input_buf  += c
                    output_buf += out
                    status = ""

        elif mode == "command":
            if ch in (curses.KEY_BACKSPACE, 127, 8):
                cmd_buf = cmd_buf[:-1]
                cmd_history_idx = None

            elif ch == 27:  # ESC
                mode = "normal"
                cmd_buf = ""
                cmd_history_idx = None

            elif ch == curses.KEY_UP:
                if cmd_history:
                    if cmd_history_idx is None:
                        cmd_history_idx = len(cmd_history) - 1
                    elif cmd_history_idx > 0:
                        cmd_history_idx -= 1
                    cmd_buf = cmd_history[cmd_history_idx]

            elif ch == curses.KEY_DOWN:
                if cmd_history and cmd_history_idx is not None:
                    if cmd_history_idx < len(cmd_history) - 1:
                        cmd_history_idx += 1
                        cmd_buf = cmd_history[cmd_history_idx]
                    else:
                        cmd_history_idx = None
                        cmd_buf = ""

            elif ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                if cmd_buf and (not cmd_history or cmd_history[-1] != cmd_buf):
                    cmd_history.append(cmd_buf)
                cmd_history_idx = None
                status, quit_, clear_io, new_machine = _handle_command(
                    cmd_buf, machine, config, initial_plugboard, rebuild_fn
                )
                mode = "normal"
                cmd_buf = ""
                if quit_:
                    break
                if new_machine is not None:
                    machine = new_machine
                if clear_io:
                    input_buf = ""

            elif 32 <= ch <= 126:
                cmd_buf += chr(ch)
                cmd_history_idx = None

        redraw()


def run_tui(machine, config, rebuild_fn=None):
    """Launch the curses TUI.

    rebuild_fn: callable(config) -> EnigmaMachine — required for /rotors and /plug commands.
    """
    initial_plugboard = list(config.get("plugboard") or [])
    curses.wrapper(_tui_main, machine, config, initial_plugboard, rebuild_fn)
