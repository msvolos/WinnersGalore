---
name: handicap-race
description: >-
  Handicap a horse race using Mike's value-hunting method (average earnings per
  start, recent form trend, jockey/trainer win rates, and a 3.5-to-1 minimum
  odds rule for finding a diamond in the rough). Use this whenever the user
  provides Daily Racing Form past performances (as a PDF, pasted text, or an
  open Chrome tab) and wants to handicap, analyze, break down, or pick a race,
  find value plays or longshots, or asks who to bet. Trigger even if the user
  does not say the word "handicap" as long as racing past performances are
  involved and they want an opinion on the race.
---

# Handicap a Race (Mike's Method)

Mike bets small win amounts and hunts for value, so the whole job is finding a
**diamond in the rough**: a horse the crowd is underrating that his numbers say
is live. Speed alone does not win him money because the fast, obvious horses are
bet down below a price worth taking. Keep that goal in front of you the whole
time. A correct handicap that only crowns the 7-5 favorite has failed him, even
if that horse wins.

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

This is Mike's first screen because it rewards horses that show up and hit the
board against their class, not just the odd big score. Two judgment calls matter:

- **Lightly raced this year gets weighted toward last year.** If a horse has
  only one or two starts this year, its current per-start number is noisy, so
  lean on last year's figure and treat this year as a small sample. Mike calls
  this out specifically.
- **A high per-start on few starts is a flag to investigate, not an automatic
  knock.** A horse who is 2-for-3 this year with a fat per-start number is
  exactly the improving type worth a look, especially at a price.

Lay the numbers out so the comparison is visible, then move on. Do not rank yet.

## Step 2 - Recent form trend

Read each horse's last three or four race lines and ask one question: **is this
horse getting stronger or weaker?** Look at the Beyer Speed Figures (the number
after the date/conditions), finishing positions, beaten lengths, and the trip
comment on the right.

- Rising Beyers, sharper finishes, and "gaining", "willingly", "drew clear"
  comments mean a horse on the improve. That is the good kind.
- Falling figures and "faded", "no rally", "outrun" mean a horse going the
  wrong way, discount it even if the connections are strong.
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
- The **closer-look / trainer paragraph**, which often flags angles like "wins
  at 18% with first-time turfers" or "this barn hits the board 40% with
  longshots at an average payoff of $13.93". For Mike's longshot hunting, a
  low win-percent barn that is known for live prices can be a plus, not a minus.

Strong connections raise confidence; weak win rates are a caution unless the
price and the longshot angle justify it.

## Step 4 - Apply the 3.5-to-1 odds rule

Mike will not bet a horse at shorter than **3.5 to 1** (7/2). The stake is too
small to bother below that. So:

- Take the morning-line odds for each horse. Anything **shorter than 3.5-1**
  (7-2), for example 7-5, 8-5, 2-1, 5-2, 3-1, is **off his list**. Name these
  horses and note if they are the class of the field, but set them aside. They
  are context for the shape of the race, not plays.
- Everything **3.5-1 (7/2) or longer** is playable and gets ranked.
- Morning line is only an estimate. If live tote odds are available (from the
  Chrome tab), prefer them and say which you used. Remind Mike that a horse can
  drift onto or off his list by post time, so the final call is the board.

## Step 5 - Rank the playable horses and name the diamond

Now synthesize the three factors for the horses that cleared the odds rule.
Weigh a rising trend and a fair price heavily, since that is where his edge
lives. A proven, improving horse at 8-1 is worth more to him than a flat,
fading horse at 4-1.

Layer in **smart context** that changes how much to trust the numbers:

- **Surface and distance switches.** First time on turf, first sprint after
  routes, first time long, dirt-to-synthetic, and so on. Flag these clearly. A
  horse **proven on today's surface and distance** (check the surface record
  line, e.g. `Turf(328) 5 2 2 0`) is more reliable than one projecting to it.
- **Probable scratches.** A horse cross-entered in another race the same weekend,
  or one whose last line is dated a day or two before today's card (it already
  ran and cannot come back that fast), is likely to scratch. Flag it and note
  that a scratch improves the prices on the others.
- **Class moves.** Dropping in class after facing tougher is a positive; jumping
  from claimers or maidens into a stakes is a question to raise.

Land on a clear recommendation: a top pick that best fits his profile (value +
rising form + fair connections), a second choice, and a deeper flyer or two if
the price is big enough to be interesting. Explain the one thing that could go
wrong with the top pick (the turf switch, the bounce risk, the old legs), so it
is an honest read.

## Output format

Deliver the analysis **in the chat** (no file unless Mike asks for one). Write
it as readable prose with light structure, in this order:

1. One line naming the race (track, race number, distance, surface, conditions).
2. The horses **off the list** on the odds rule, and any **probable scratches**,
   with a one-line reason each. This clears the deck the way he thinks.
3. The **playable horses, ranked**, each with a short paragraph walking his three
   steps (earnings per start, trend, connections) plus any surface/class flag.
   Lead each with the horse name and its odds.
4. A **bottom line**: the top pick, the second choice, and any flyer, phrased as
   how he would actually bet it.
5. Offer once, in a single line, to build it into a printable one-page sheet if
   he wants one for the track.

### Writing style (Mike's preferences, always apply)

- **No em-dashes.** Use parentheses for asides. An en-dash is fine only to
  separate a header.
- **American English spellings.**
- **Do not use the "not this, but that" phrasing.** State things directly.
- Keep the tone plain and confident, like a sharp friend at the rail, not a
  hedging report. Do not drown it in bold text or bullets; a ranked list with a
  paragraph per horse reads best.

## Worked example (compressed, for tone and shape)

Input: a Woodbine turf sprint stakes, seven horses.

Output shape:
> Woodbine Race 9, 5 furlongs on the inner turf, Ontario-bred stakes.
>
> Off the list on your odds rule: Outlaw Kid (7-5, fastest horse here, no value)
> and Poulin in O T (5-2, and he looks cross-entered / just ran yesterday, so
> likely a scratch anyway).
>
> **Dark Screen (8-1)** - the diamond. Per-start about $7,200 this year, but the
> trend is the sell: Beyers 58, 66, 76, 89, that 89 a career best last out
> beaten a neck, and it came on turf so nothing to project (5 turf starts, 2
> wins). Connections win at a low clip but are flagged as longshot specialists
> hitting the board 40% at a $13.93 average payoff. Rising, proven surface, live
> price. Only risk is bouncing off that top figure.
>
> **Cost of War (6-1)** - the improver. Highest per-start in the group (about
> $26,700 on 3 starts, two wins), Beyers climbing, strong barn (Aebly 20%, Casse
> 19%, 18% together). The catch is first time on turf and a top figure well
> below Dark Screen's.
>
> ...(remaining playable horses)...
>
> Bottom line: Dark Screen at 8-1 is the play, Cost of War the one to key against
> him if you buy the turf switch, and Mister Blue a small saver at 20-1 on the
> hot barn. Watch for a Poulin scratch, which only helps your prices.

Notice what the example does: it clears the under-priced horses first, ranks by
value and trend rather than raw speed, excuses a bad line with a reason, flags
the surface switch, and calls a probable scratch. That is the method.
