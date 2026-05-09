"""enigma-utils — data-management commands for py-enigma.

Commands
--------
  enigma-utils scan compile <file> [<file> ...]   merge scan JSON(s) into codebook(s)
  enigma-utils scan compile --all                  compile every file in data/scans/
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_SCANS_DIR    = Path(__file__).parent.parent.parent / "data" / "scans"
_CODEBOOKS_DIR = Path(__file__).parent.parent.parent / "data" / "codebooks"
_BACKUPS_DIR  = _CODEBOOKS_DIR / "backups"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _backup(path: Path) -> Path:
    _BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    dest = _BACKUPS_DIR / f"{path.stem}.{ts}.json"
    import shutil
    shutil.copy2(path, dest)
    return dest


def _entry_key(entry: dict) -> tuple:
    """Unique key for a codebook entry: (day, month_year)."""
    return (entry.get("day"), entry.get("month_year"))


# ---------------------------------------------------------------------------
# scan compile
# ---------------------------------------------------------------------------

def _compile_scan(scan_path: Path, verbose: bool) -> bool:
    """Merge one scan file into its codebook.  Returns True on success."""
    try:
        scan = _load_json(scan_path)
    except Exception as e:
        print(f"  error: cannot read {scan_path}: {e}", file=sys.stderr)
        return False

    scan_id    = scan.get("scan_id", scan_path.stem)
    codebook_id = scan.get("codebook_id")
    if not codebook_id:
        print(f"  error: {scan_path.name}: missing 'codebook_id'", file=sys.stderr)
        return False

    new_entries = scan.get("entries", [])
    if not new_entries:
        print(f"  warning: {scan_path.name}: no entries — skipped")
        return True

    codebook_path = _CODEBOOKS_DIR / f"{codebook_id}.json"

    # Load or initialise codebook
    if codebook_path.exists():
        codebook = _load_json(codebook_path)
        existing = {_entry_key(e): e for e in codebook.get("entries", [])}
        backed_up = _backup(codebook_path)
        if verbose:
            print(f"  backed up existing codebook -> {backed_up.name}")
    else:
        codebook  = {"codebook_id": codebook_id, "entries": []}
        existing  = {}

    conflicts  = []
    merged     = 0

    for entry in new_entries:
        key = _entry_key(entry)
        if key in existing:
            existing_entry = existing[key]
            # Check if this scan adds any non-null fields to an existing entry
            added_fields = []
            for field, value in entry.items():
                if value is not None and existing_entry.get(field) is None:
                    existing_entry[field] = value
                    added_fields.append(field)
            # Check for true conflicts (both non-null, different values)
            true_conflicts = []
            for field, value in entry.items():
                if (value is not None
                        and existing_entry.get(field) is not None
                        and existing_entry[field] != value):
                    true_conflicts.append(field)
            if true_conflicts:
                conflicts.append((key, true_conflicts))
                print(
                    f"  conflict: day={key[0]} month_year={key[1]} "
                    f"fields={true_conflicts} — kept existing value(s)",
                    file=sys.stderr,
                )
            else:
                if added_fields:
                    merged += 1
                    if verbose:
                        print(f"  patched day={key[0]}: added {added_fields}")
        else:
            existing[key] = dict(entry)
            merged += 1

    # Rebuild entries sorted by day descending (highest day first, matching source sheets)
    codebook["entries"] = sorted(
        existing.values(),
        key=lambda e: (e.get("month_year") or "", e.get("day") or 0),
        reverse=True,
    )

    # Record which scans contributed
    sources = codebook.setdefault("sources", [])
    if scan_id not in sources:
        sources.append(scan_id)

    _write_json(codebook_path, codebook)

    total = len(new_entries)
    print(
        f"  {scan_path.name} -> {codebook_id}.json  "
        f"({merged} merged, {total - merged - len(conflicts)} unchanged"
        + (f", {len(conflicts)} conflict(s)" if conflicts else "")
        + ")"
    )
    return True


def cmd_scan_compile(args) -> int:
    if args.all:
        if not _SCANS_DIR.exists():
            print(f"error: scans directory not found: {_SCANS_DIR}", file=sys.stderr)
            return 1
        paths = sorted(_SCANS_DIR.glob("*.json"))
        if not paths:
            print("No scan files found.")
            return 0
    else:
        paths = [Path(p) for p in args.files]

    print(f"Compiling {len(paths)} scan file(s)...")
    ok = all(_compile_scan(p, verbose=args.verbose) for p in paths)
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="enigma-utils",
        description="Data-management utilities for py-enigma",
    )
    sub = parser.add_subparsers(dest="group", metavar="COMMAND")
    sub.required = True

    # -- scan -----------------------------------------------------------------
    scan_p = sub.add_parser("scan", help="work with scan JSON files")
    scan_sub = scan_p.add_subparsers(dest="action", metavar="ACTION")
    scan_sub.required = True

    compile_p = scan_sub.add_parser(
        "compile",
        help="merge scan file(s) into compiled codebook(s)",
    )
    compile_p.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="scan JSON file(s) to compile",
    )
    compile_p.add_argument(
        "--all",
        action="store_true",
        help=f"compile every scan in {_SCANS_DIR}",
    )
    compile_p.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show per-entry detail",
    )
    compile_p.set_defaults(func=cmd_scan_compile)

    args = parser.parse_args()

    if not getattr(args, "files", None) and not getattr(args, "all", False):
        # scan compile with no files and no --all
        compile_p.print_help()
        sys.exit(1)

    sys.exit(args.func(args))
