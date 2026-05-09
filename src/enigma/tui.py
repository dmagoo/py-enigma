"""Curses-based interactive TUI for the Enigma machine simulator."""

import curses


def _draw_header(win, config):
    rotors = "  ".join(config["rotors"])
    reflector = config.get("reflector", "")
    plugboard = config.get("plugboard", [])
    plug_str = " ".join(plugboard) if plugboard else "none"
    h, w = win.getmaxyx()
    line = f"  ENIGMA  |  Rotors: {rotors}  |  Reflector: {reflector}  |  Plugboard: {plug_str}"
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
        bar = "  /reset   /state   /help   /exit   |   Enter: clear   Backspace: undo display"
        win.addstr(h - 1, 0, bar[:w - 1], curses.A_DIM)


def _handle_command(cmd, machine, config):
    """Execute a slash command. Returns (status_message, should_quit, clear_io)."""
    cmd = cmd.strip().lower()
    if cmd == "exit":
        return ("", True, False)
    elif cmd == "reset":
        machine.reset()
        return ("rotors reset.", False, True)
    elif cmd == "state":
        rotors = "  ".join(config["rotors"])
        plug = " ".join(config.get("plugboard", [])) or "none"
        return (f"rotors: {rotors}  reflector: {config.get('reflector','')}  plugboard: {plug}", False, False)
    elif cmd in ("help", "h", "?"):
        return ("/reset  /state  /help  /exit   |   ESC to cancel command", False, False)
    else:
        return (f"unknown command: /{cmd}", False, False)


def _tui_main(stdscr, machine, config):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    input_buf  = ""
    output_buf = ""
    mode       = "normal"
    cmd_buf    = ""
    status     = ""

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
                # Remove last display char only — rotor state has already advanced, cannot be undone
                if input_buf:
                    input_buf  = input_buf[:-1]
                    output_buf = output_buf[:-1]

            elif ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                input_buf  = ""
                output_buf = ""
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

            elif ch == 27:  # ESC
                mode = "normal"
                cmd_buf = ""

            elif ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                status, quit_, clear_io = _handle_command(cmd_buf, machine, config)
                mode = "normal"
                cmd_buf = ""
                if quit_:
                    break
                if clear_io:
                    input_buf  = ""
                    output_buf = ""

            elif 32 <= ch <= 126:
                cmd_buf += chr(ch)

        redraw()


def run_tui(machine, config):
    """Launch the curses TUI. Cleans up the terminal on exit."""
    curses.wrapper(_tui_main, machine, config)
