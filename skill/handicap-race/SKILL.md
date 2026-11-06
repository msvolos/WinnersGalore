---
name: handicap-race
description: >-
  Handicap a horse race using Mike's value method (average earnings per start,
  recent form trend, jockey/trainer win rates, then a fair-odds line on the
  real contenders to find the horse whose price beats its chance). Use this
  whenever the user provides Daily Racing Form past performances (as a PDF,
  pasted text, or an open Chrome tab) and wants to handicap, analyze, break
  down, or pick a race, find value plays or overlays, or asks who to bet.
  Trigger even if the user does not say the word "handicap" as long as racing
  past performances are involved and they want an opinion on the race.
---

# Handicap a Race (Mike's Method)

Mike bets small win/place/show amounts and wants the best return over time.
The job has two halves, in this order:

1. **Find the horses most likely to win.** Judge the whole field on figures,
   form and connections, favorites included.
2. **Bet the one whose price is better than its chance.** Put a fair-odds line
   on the real contenders and play the horse the board is underpricing.

A big price on its own is not value, and a short price on its own is not a
reason to pass. Value is the gap between the horse's real chance and the odds.
Mike's own tracked results drove this: picks at 7-2 to 5-1 held up, picks
reaching past 5-1 lost close to half their stake, and the morning-line
favorite outperformed both of the old picks. The old hard 3.5-to-1 floor kept
throwing out the most likely winners and kept pushing the pick toward
longshots.

## Step 0 - Get the past performances

The form arrives one of these ways:

- **PDF upload** (most common). Read it with the Read tool, passing `pages` to
  pull every page (a full card can run several pages). Each horse's block has a
  yearly earnings box, a stack of recent race lines, workout lines, and a
  trainer/closer-look paragraph.
- **Open Chrome tab**. If the user says the form is open in Chrome, use the
  `mcp__claude-in-chrome__*` tools: call `tabs_context_mcp` first, then
  `get_page_text` (or `read_page`) on the DRF tab. If the extension is not
  connected, say so plainly and ask the user to attach the PDF or paste the
  text instead. Do not stall retrying.
- **Pasted text**. Work directly from what they paste.

If you are unsure how to read the DRF layout (where the earnings table,
Beyers, or jockey/trainer percentages sit), read `references/drf-format.md`.

Confirm which race you are handicapping. A DRF file often holds one race, but if
several are present, ask which one unless the user already named it.

## Step 1 - Average earnings per start (this year and last)

For every horse, compute earnings divided by starts for the current year and the
prior year from the yearly box:

```
avg earnings/start = year earnings / year starts
```

This is a screen that rewards horses that show up and hit the board against
their class. Two judgment calls matter:

- **Lightly raced this year gets weighted toward last year.** If a horse has
  only one or two starts this year, its current per-start number is noisy, so
  lean on last year's figure and treat this year as a small sample.
- **A high per-start on few starts is a flag to investigate, not an automatic
  knock.** A horse who is 2-for-3 this year with a fat per-start number is
  often the improving type worth a look.

Lay the numbers out so the comparison is visible, then move on. Per-start is a
tiebreaker later, never the main case for a pick.

## Step 2 - Recent form trend

Read each horse's last three or four race lines and ask one question: **is this
horse getting stronger or weaker?** Look at the Beyer Speed Figures, finishing
positions, beaten lengths, and the trip comment on the right. Compare the best
recent figure to the race's Beyer par.

- Rising Beyers, sharper finishes, and "gaining", "willingly", "drew clear"
  comments mean a horse on the improve.
- Falling figures and "faded", "no rally", "outrun" mean a horse going the
  wrong way. Discount it even if the connections are strong.
- **Excuse a legitimately bad line.** A troubled trip ("blocked", "steadied",
  "broke slow", "wide"), or an obvious experiment (a sprinter tried around two
  turns, a turf horse on dirt, a big class jump) can be struck through rather
  than held against the horse. Say explicitly when you are throwing out a line
  and why, so Mike can disagree if he wants.

## Step 3 - Jockey and trainer

Pull the jockey win percentage and trainer win percentage (the decimal near
their names, e.g. `.21` = 21%). Also use, when shown:

- The **jockey/trainer combo** line (win % and ROI, often written like
  `J/T 2025-26 WO (53 .32 $2.35)` meaning 53 starts, 32% wins, $2.35 return per
  $2). A strong combo ROI is a real positive.
- The **closer-look / trainer paragraph**, which flags angles like "wins at
  18% with first-time turfers" or "hits the board 40% with longshots at an
  average payoff of $13.93".

Strong connections raise a horse's chance. Weak win rates lower it. A rider
under about 10% at the meet (or 0-for-the-meet on a real sample), or a J/T
combo under 10%, keeps a horse out of the top-pick spot; every top pick with
that flag missed the board in Mike's tracked races. A longshot-barn angle can
earn a horse the flyer spot, not the top spot.

## Step 4 - Name the contenders (whole field, favorites included)

Pick out the three to five horses with a real chance to win, regardless of
price. Use the factors above, in this order of weight:

1. **Figures and trend.** The best recent Beyers (at or near par, or the best
   in the field) on a rising or steady line.
2. **Connections.** Jockey, trainer and combo win rates.
3. **Smart context** that changes how much to trust the numbers:
   - **Surface and distance switches.** First time on turf, first sprint after
     routes, first time long, dirt-to-synthetic, and so on. A horse **proven
     on today's surface and distance** (check the surface record line, e.g.
     `Turf(328) 5 2 2 0`) is more reliable than one projecting to it.
   - **Class moves.** Dropping in class after facing tougher is a positive;
     jumping from claimers or maidens into a stakes is a question to raise.
   - **Pace.** Note who wants the lead and who closes. Use it as a tiebreaker
     only. A projected pace collapse is never the main reason to rate a horse
     highly: speed held up more often than it collapsed in Mike's tracked
     races, and closers picked on a pace meltdown went 0 for 5 in the money.
   - **Probable scratches.** A horse cross-entered in another race the same
     weekend, entered main-track-only on a turf race with the turf up, or one
     whose last line is a day or two before today's card, is likely to
     scratch. Flag it, leave it out of the contenders, and note that a scratch
     shifts the prices on the others.

Lightly raced improvers with a 20%+ jockey, trainer or combo were the profile
that hit the board most in the tracked results. Supporting angles (per-start
earnings, course-and-distance record, pace setup) went 0 for 8 in the money
when they were the main case for a top pick, so they break ties only.

## Step 5 - Fair-odds line and the value pick

Give each contender an honest **win chance** in percent. The contenders
together should usually total about 70 to 90%, leaving the rest for the
non-contenders. Be realistic: a standout favorite might be 40 to 50%, a
solid second choice 20 to 25%, a live outsider 8 to 12%.

Convert each chance to **fair odds**, and compare to the price:

```
fair odds (to 1) = 100 / win% - 1        (25% -> 3-1, 40% -> 1.5-1)
value ratio      = win% / 100 x (odds + 1)
```

Use live tote odds when available (say so), otherwise the morning line.

- **Overlay:** value ratio of **1.25 or more**. The horse pays at least 25%
  more than its chance is worth. This is a bet.
- **Fair:** about 1.0 to 1.25. Playable only as the second choice.
- **Underlay:** under 1.0. Do not bet it, however likely it is to win. Name it
  as the horse to beat.

**Price floor: 2-1.** Mike's stake is small, so a horse shorter than 2-1 is
not a bet even if it is an overlay. It stays in the analysis as the horse to
beat. (Horses from 2-1 to 3-1 are now fully playable; they were thrown out
under the old 7-2 rule.)

Choose the picks:

- **Top pick:** the contender with the best value ratio at 2-1 or longer that
  also clears the connections floor. When two are close (within about 0.1),
  take the one with the higher win chance. Do not prefer a horse just because
  its price is longer; the value ratio already counts the price.
- **Second choice:** the next best value ratio among the contenders at 2-1 or
  longer.
- **Flyer (optional):** a non-contender at a big price with one live angle
  (the pace meltdown, the longshot barn, the hidden figure). This is where
  contrarian stories belong.
- **No overlay on the board:** still name a top pick and second choice (the
  best two value ratios) so the race can be tracked, but say plainly that
  neither is an overlay at these odds and give the minimum price that would
  make each one a bet (the odds where the value ratio reaches 1.25:
  `100 x 1.25 / win% - 1`).

Explain the one thing that could go wrong with the top pick (the class jump,
the bounce risk, the old legs), so it is an honest read.

### At the window

The final call is the board. Give Mike each pick's minimum bettable price (the
odds where its value ratio is 1.25, and never below 2-1). If the top pick is
under that price at post and the second choice is still above its own, bet the
second choice. In the tracked races, picks that took money (went off shorter than
their morning line) hit the board 9 of 12 times, while picks that drifted out to about one
and a half times their morning line or more hit 1 of 6. A big drift is a
warning, not a gift.

## Output format

Deliver the analysis **in the chat** (no file unless Mike asks for one). Write
it as readable prose with light structure, in this order:

1. One line naming the race (track, race number, distance, surface, conditions,
   Beyer par if shown).
2. **Probable scratches**, with a one-line reason each.
3. **The contenders**, each with a short paragraph walking the method (figures
   and trend first, then connections, earnings and any surface, class or pace
   flag). Lead each with the horse name and odds. Below the paragraphs, a
   small table:

   | Horse | Odds | Win % | Fair odds | Value ratio | Call |
   |---|---|---|---|---|---|

   where Call is Overlay, Fair, Underlay, or Under 2-1.
4. One or two lines on the **rest of the field** (why they are not contenders,
   and any flyer).
5. A **bottom line**: the top pick, the second choice, any flyer, and each
   pick's minimum price at the window, phrased as how he would actually bet it.
6. Offer once, in a single line, to build it into a printable one-page sheet if
   he wants one for the track.

### Writing style (Mike's preferences, always apply)

- **No em-dashes.** Use parentheses for asides. An en-dash is fine only to
  separate a header.
- **American English spellings.**
- **Do not use the "not this, but that" phrasing.** State things directly.
- Keep the tone plain and confident, like a sharp friend at the rail, not a
  hedging report. Do not drown it in bold text or bullets; a paragraph per
  contender plus the one table reads best.

## Worked example (compressed, for tone and shape)

Input: a Woodbine turf sprint stakes, seven horses.

Output shape:
> Woodbine Race 9, 5 furlongs on the inner turf, Ontario-bred stakes, par 85.
>
> Probable scratch: Poulin in O T (5-2) ran yesterday and should not come back.
>
> **Outlaw Kid (7-5)** - the horse to beat. Beyers 88, 91, 92, two clear of
> anyone, Husbands/Casse 28% together. He wins this about 40% of the time, but
> 7-5 is under the 2-1 floor and fair for him is 3-2, so no bet.
>
> **Cost of War (5-2)** - the value. Beyers 79, 84, 90 on a rising line, about
> $26,700 a start on 3 starts, Aebly 20% and Casse 19% (18% together). First
> time on turf is the question, but his dam's foals win on grass. About 30%
> to win; fair odds 7-3, and 5-2 gives a value ratio of 1.05. Fair, not an
> overlay on the morning line.
>
> **Dark Screen (8-1)** - the overlay. Beyers 58, 66, 76, 89, the 89 a career
> best beaten a neck, and proven on turf (5 starts, 2 wins). Contreras 15%.
> About 15%; fair 5.7-1, and 8-1 gives 1.35.
>
> | Horse | Odds | Win % | Fair odds | Value ratio | Call |
> |---|---|---|---|---|---|
> | Outlaw Kid | 7-5 | 40% | 1.5-1 | 0.96 | Under 2-1 |
> | Cost of War | 5-2 | 30% | 2.3-1 | 1.05 | Fair |
> | Dark Screen | 8-1 | 15% | 5.7-1 | 1.35 | Overlay |
>
> The rest are 70s horses going nowhere; Mister Blue (20-1) is a flyer on the
> hot barn.
>
> Bottom line: Dark Screen is the play at 15-2 or better. Cost of War is the
> second choice and becomes a bet at about 3-1 or better (watch the board). Outlaw
> Kid is the one to beat.

Notice what the example does: it judges the whole field first, rates the
favorite honestly, prices every contender, and picks on value ratio rather
than raw speed or raw price. That is the method.
