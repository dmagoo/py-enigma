# Data Schema

This document describes the objects, fields, and file structure used to store historical Enigma key sheet data.

JSON files are the source of truth and live in the repo. SQLite is a derived artifact, rebuilt on demand via `enigma db build` and not committed to git.

---

## Objects

### Machine
Defines a physical cipher device and its constraints. Used to validate codebook entries on import.

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | string | Canonical machine identifier | `"enigma-i"` |
| `rotor_slots` | int | Number of rotor positions | `3` |
| `rotor_pool` | array of string | Valid rotor names for this machine | `["I","II","III","IV","V"]` |
| `fixed_reflector` | string or null | Reflector name if hardcoded; null if operator-settable | `"UKW-B"` |
| `has_plugboard` | bool | Whether the machine has a plugboard | `true` |

---

### KeySystem
A named operational network or group that used a specific machine. Each codebook belongs to a key system.

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | string | Canonical key system identifier | `"luftwaffe"` |
| `name` | string | Human-readable name from the sheet | `"Luftwaffen-Maschinen-Schlüssel"` |
| `machine_id` | string | Foreign key to Machine | `"enigma-i"` |
| `service` | string | Military branch | `"luftwaffe"` |
| `network` | string or null | Operational network or region, if present | `"triton"` |

---

### Codebook
A specific published monthly key book issued to a unit. Self-describing — repeats key system fields for readability. The database is normalized; the redundancy is a JSON convenience only.

| Field | Type | Level | Description | Example |
|---|---|---|---|---|
| `id` | string | codebook | Composite identifier | `"luftwaffe-2744"` |
| `codebook_number` | string | codebook | German codebook number from the sheet | `"2744"` |
| `serial_number` | string or null | codebook | Physical copy number | `"000082"` |
| `machine_id` | string | codebook | Foreign key to Machine (redundant with key system, kept for self-description) | `"enigma-i"` |
| `service` | string | codebook | Military branch (redundant, kept for self-description) | `"luftwaffe"` |
| `network` | string or null | codebook | Network/region (redundant, kept for self-description) | `null` |
| `classification` | string or null | codebook | Security classification from the sheet | `"geheim"` |
| `settings_scope` | string | codebook | `"complete"`, `"outer"`, or `"inner"` — Triton split its sheets | `"complete"` |
| `ref_id` | string or null | codebook | Allied archival reference if applicable | `"A557690"` |
| `entries` | array | codebook | Array of CodesheetEntry objects | see below |

---

### CodesheetEntry
A single day's settings within a codebook. The composite key `codebook_id` + `month_year` + `day` is unique across all data.

| Field | Type | Description | Example |
|---|---|---|---|
| `day` | int | Day of month | `31` |
| `month_year` | string | Month this entry covers, format `YYYY-MM` | `"1942-11"` |
| `rotor_order` | array of string | Rotor selection and order, left to right | `["III","V","IV"]` |
| `ring_settings` | array of int | Ring settings, numbers 1–26 | `[17,11,4]` |
| `plugboard` | array of string | Base plugboard pairs, active from start of day | `["TW","BI","UY","GP","CK","JQ","DL","RV","EM","AH"]` |
| `timed_plugboard` | object or null | Time-keyed replacement plugboard pairs — semantics unresolved, see Open Questions | `{"1500": ["NS","FO"], "2300": ["CI","JN"]}` |
| `starting_positions` | array of string or null | Initial rotor window positions | `["A","A","A"]` |
| `reflector` | string or null | Reflector name; null when implied by machine | `null` |
| `reflector_raw` | string or null | Raw value from "an der Umkehrwalze" column on Luftwaffe sheets — meaning unresolved, see Open Questions | `"TZ"` |
| `recognition_groups` | array of string or null | Recognition groups for key lookup | `["kim","pwh","sbx","csw"]` |

---

### MachineConfig
A resolved, runnable machine configuration. Output of the resolver. Contains only what the machine needs to operate.

| Field | Type | Description | Example |
|---|---|---|---|
| `machine_id` | string | Machine type | `"enigma-i"` |
| `reflector` | string | Reflector name | `"UKW-B"` |
| `rotor_order` | array of string | Rotor selection and order | `["III","V","IV"]` |
| `ring_settings` | array of int | Ring settings | `[17,11,4]` |
| `starting_positions` | array of string | Initial rotor positions | `["A","A","A"]` |
| `plugboard` | array of string | Active plugboard pairs | `["TW","BI","UY"]` |

---

### CodebookQuery
Input to the resolver. Combines a codebook entry reference with resolution context to produce a MachineConfig.

| Field | Type | Description | Example |
|---|---|---|---|
| `codebook_id` | string | Target codebook | `"luftwaffe-2744"` |
| `month_year` | string | Target month | `"1942-11"` |
| `day` | int | Target day | `31` |
| `time` | string or null | Time of day in HHMM format, used to resolve timed plugboard | `"1600"` |
| `strict` | bool | If true, throw when context is ambiguous; if false, return all possible configs | `false` |

---

## JSON File Structure

Scans are the raw archive. Codebooks are compiled output. You never hand-edit codebook files directly — fix the scan and recompile.

```
data/
  machines/
    enigma-i.json
    m4.json
  key-systems/
    luftwaffe.json
    heer.json
    kriegsmarine.json
  scans/
    nara-a557690.json
    bletchley-p1030660.json
    ...
  codebooks/
    luftwaffe-2744.json
    heer-74.json
    ...
  codebooks/backups/
    luftwaffe-2744.{ctime}.json
    ...
```

### Scan file
Each uploaded image is parsed into a scan file. One scan file per source image. The scan ID is derived from the archival reference if known (`nara-a557690`), or a short hash of the image file for unidentified sources.

A scan file has the same structure as a codebook file but represents only the entries visible on that specific page/sheet. Multiple scan files may contribute to the same codebook.

```json
{
  "scan_id": "nara-a557690",
  "source": "National Archives, REF ID A557690",
  "codebook_id": "luftwaffe-2744",
  "entries": [
    {
      "day": 31,
      "month_year": "1942-11",
      "rotor_order": ["III","V","IV"],
      "ring_settings": [17,11,4],
      "plugboard": ["TW","BI","UY","GP","CK","JQ","DL","RV","EM","AH"],
      "timed_plugboard": {"1500": ["NS","FO"], "2300": ["CI","JN"]},
      "starting_positions": null,
      "reflector": null,
      "reflector_raw": null,
      "recognition_groups": ["kim","pwh","sbx","csw"]
    }
  ]
}
```

### Compile workflow
`enigma scans compile` assembles all scan files for a codebook into a single compiled codebook file:

1. Back up existing codebook JSON if present: `codebooks/backups/luftwaffe-2744.{ctime}.json`
2. Merge all matching scan entries — keep existing, add new, no duplicates
3. Halt and report any conflicts (same `day` + `month_year`, different field values) for manual resolution
4. Write compiled output to `codebooks/luftwaffe-2744.json`

### Example machine file (`data/machines/enigma-i.json`)
```json
{
  "id": "enigma-i",
  "rotor_slots": 3,
  "rotor_pool": ["I","II","III","IV","V"],
  "fixed_reflector": null,
  "has_plugboard": true
}
```

### Example key system file (`data/key-systems/luftwaffe.json`)
```json
{
  "id": "luftwaffe",
  "name": "Luftwaffen-Maschinen-Schlüssel",
  "machine_id": "enigma-i",
  "service": "luftwaffe",
  "network": null
}
```

### Example codebook file (`data/codebooks/luftwaffe-2744.json`)
```json
{
  "id": "luftwaffe-2744",
  "codebook_number": "2744",
  "serial_number": "000082",
  "machine_id": "enigma-i",
  "service": "luftwaffe",
  "network": null,
  "classification": "geheim",
  "settings_scope": "complete",
  "ref_id": null,
  "entries": [
    {
      "day": 31,
      "month_year": "1942-11",
      "rotor_order": ["III","V","IV"],
      "ring_settings": [17,11,4],
      "plugboard": ["TW","BI","UY","GP","CK","JQ","DL","RV","EM","AH"],
      "timed_plugboard": {"1500": ["NS","FO"], "2300": ["CI","JN"]},
      "starting_positions": null,
      "reflector": null,
      "reflector_raw": null,
      "recognition_groups": ["kim","pwh","sbx","csw"]
    }
  ]
}
```

---

## Database Normalization

The JSON files are self-describing and contain redundant fields (`machine_id`, `service`, `network` on both key system and codebook). In SQLite these are normalized:

- `machines` table
- `key_systems` table — foreign key to `machines`
- `codebooks` table — foreign key to `key_systems`
- `codesheet_entries` table — foreign key to `codebooks`

The import pipeline resolves redundant fields and validates consistency before inserting.

---

## Validation Rules

Run before any database write:

1. All required fields are present
2. `machine_id` references a known machine definition
3. `key_system_id` references a known key system
4. `machine_id` on codebook matches its key system's `machine_id`
5. `rotor_order` values are all in the machine's `rotor_pool`
6. `ring_settings` values are all in range 1–26
7. No duplicate entries within a codebook (same `day` + `month_year`)
8. Conflicting near-duplicates (same `day` + `month_year`, different field values) halt the import and report to the operator

---

## Open Questions

### `reflector_raw`
The "an der Umkehrwalze" column appears on Luftwaffe sheets only. Its meaning is unresolved. Values are stored as-is in `reflector_raw` and not used by the machine. Do not attempt to interpret until a primary source is found.

### `timed_plugboard` semantics
The Luftwaffe sheets have `Zusatzstecker-verbindungen` columns labeled 1500 and 2300. It is unconfirmed whether these pairs are:
- **Deltas from base** — replace specific pairs from the day's base plugboard (stateless resolution)
- **Deltas from previous period** — replace pairs from the prior time period (sequential resolution)

This distinction is a blocker for implementing the resolver. Do not implement timed plugboard resolution until verified from a primary source.
