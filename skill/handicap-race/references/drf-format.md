# Reading a Daily Racing Form past-performance block

Each horse in a DRF past-performances (PP) page is one block. Here is where the
numbers Mike's method needs actually sit, so you extract them correctly.

## Header area (top of each horse block)

- **Program number and horse name** on the left. The small number under the
  program number (e.g. `20-1`, `7-5`, `5-2`) is the **morning-line odds**. This
  is what the odds rule uses unless live tote odds are available.
- **Owner, silks** below the name.
- **Breeding line** (color, sex, foaling date, sire / dam / broodmare sire,
  auction price) on the right of the name.
- **Jockey name** with a stats block in parentheses, and **year win stats**.
  Format like `HERNANDEZ R M (257 55 40 41 .21) 2026: (393 76 .19)` means the
  meet/season line then the current-year line; the final decimal (`.19`) is the
  **jockey win percentage** (19%).
- **Trainer** line `Tr:` with the same shape. The final decimal is the
  **trainer win percentage**. Example: `Tr: Carroll Josie (102 23 11 17 .23)
  2026: (129 27 .21)`.
- **Weight** carried, shown like `L 118` (L = Lasix).

## Yearly earnings box (right side of header)

A small table with rows for **Life**, the **current year**, the **prior year**,
and surface splits (D.Fst dirt-fast, Wet, Synth, Turf, Dst = distance). Each row
reads: starts, wins, places (2nds), shows (3rds), earnings, and best Beyer.

Example:
```
Life  6 M 2 2  $43,249  76
2026  3 M 1 1  $20,755  76
2025  3 M 1 1  $22,444  66
```
So 2026 = 3 starts, $20,755 -> about $6,918 per start. 2025 = 3 starts, $22,444
-> about $7,481 per start. (`M` here is the maiden marker in some layouts; the
numeric wins/earnings are what matter for the per-start math.)

The **surface split rows** (Turf, Synth, D.Fst, Dst) give the proven-surface
record. `Turf(328) 5 2 2 0 $125,973` = 5 turf starts, 2 wins, proven on grass.
Use these for the surface/distance-switch check in Step 5.

## Race lines (the stack under the header)

Each past race is one row, most recent at the top. Left to right, roughly:

- **Date and track** (`26Jly26-4WO`), surface/going (`fst`, `fm`, `gd`, `sy`),
  distance (`5f`, `6f`, `1m`), and a small turf marker if run on grass.
- Fractional and final times, then the **race conditions/class** (e.g.
  `Md Sp Wt`, `OC 50k/n2x`, a stakes name, `Clm 25000`). This is class level.
- The **Beyer Speed Figure** for that race, usually the standout two-digit
  number early in the line (e.g. `76`, `89`). Rising Beyers = improving form.
- The **running line** (position and lengths at each call) and the **finish**,
  followed by jockey, weight, odds, and the field's top finishers.
- A short **trip comment** on the far right (`Reluctant, faltered`, `gaining
  4w`, `drew clear`, `blocked`). These justify excusing or crediting a line.

When Beyers or finishes jump around, read the trip comment before deciding if a
bad race was the horse's true form or a bad trip / wrong setup.

## Workouts and closer look

- **WORKS**: a line of recent workout times. Useful as a freshness/fitness
  signal but secondary to Mike's core factors.
- **TRAINER** line: split stats by category (turf sprints, first-time turf,
  routes to sprints, layoff, etc.) with win % and ROI. Great for angle-spotting.
- **Closer look / comment paragraph**: DRF analyst prose. Often names the key
  angle (surface switch, hot combo, longshot barn). Quote or paraphrase the
  useful bits, but treat it as one more input, not gospel.

## Jockey/trainer combo line

Look for `J/T 20xx-yy TRK (starts win% $roi)`, e.g.
`J/T 2025-26 WO (53 .32 $2.35)`: 53 starts together, 32% wins, $2.35 returned
per $2 bet. A combo with both a fair win % and an ROI above about $2.00 is a
genuine positive, and a high ROI on a low win % is exactly the longshot signal
Mike wants.
