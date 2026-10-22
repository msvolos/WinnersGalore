# DRF Race of the Day Tracker: daily agent instructions

Run this unattended every day. Do not ask the user questions. If something blocks you, write the reason in the `notes` column (or in `run-log.md`) and move on.

Tracker folder: the folder this file is in (all paths below are relative to it).

- `ledger.csv`: one row per Race of the Day (the source of truth)
- `handicaps\`: the full pre-race write-up for each race
- `recaps\`: the post-race recap for each race (same file name as its handicap)
- `DRF Tracker.xlsx`: formatted Excel workbook (dashboard KPIs, charts, ledger, bet log), rebuilt from `ledger.csv` every run by `build_workbook.py`. Never edit the workbook by hand; edit `ledger.csv` and rebuild. Do not create `summary.md`; the workbook replaces it.
- `run-log.md`: one short line appended per run

Two strategies are tracked on every race:
- **Top Pick:** $2 Win + $2 Place + $2 Show ($6) on the top pick.
- **Top 2 Picks:** the same $6 WPS on the top pick **and** $6 WPS on the second choice ($12 per race).
So every race needs results for both the top pick and the second choice. The workbook does all the strategy math; you only record each horse's result.

There are two runs a day:
- **Morning run (9 AM):** Steps 1 through 5, in order. Step 1 also writes a recap for any graded race that does not have one yet.
- **Evening run (10 PM):** only grade and recap **today's** race, while DRF still shows its chart with trip notes for free. Do Step 1 and Step 1b for today's ledger row only, then Step 4 and Step 5. Skip Steps 2 and 3 (no handicapping). If today's race has not run yet or its result is not posted, write `<date> evening: result not posted yet` to `run-log.md`, publish nothing, and stop; the morning run will catch it.

## Browser

Use **Claude in Chrome** (`mcp__claude-in-chrome__*` tools; load them with ToolSearch first). The user's Chrome is signed in to drf.com. A signed-out session sees only the first 4 horses ("Register to access premium Formulator Features"), so the Chrome session is required. Call `tabs_context_mcp` with `createIfEmpty: true` and work in your own tab. Close any tab you opened when you finish.

If Chrome is not connected, or the PP page shows the "Register to access" gate or "Login/Sign Up", do not handicap a partial field. Write `run-log.md`: `<date> BLOCKED: Chrome not connected / DRF signed out`, still run Step 4, and stop. Never type credentials. Never buy anything.

Key DRF URLs (use `CAN` instead of `USA` for Canadian tracks such as Woodbine):
- Race of the Day hub: `https://www.drf.com/race-of-the-day`
- PPs for one race (free on race day):
  `https://www.drf.com/pp-details/MM-DD-YYYY/TRACKCODE/RACENUMBER/D/USA`
  (example: `https://www.drf.com/pp-details/10-16-2026/RP/8/D/USA`). It redirects to `/formulator/pp-details/...`, which is fine.
- Results for a track and date (returns JSON):
  `https://www.drf.com/results/resultDetails/id/TRACKCODE/country/USA/date/MM-DD-YYYY`

DRF pages render with JavaScript, so read them with `javascript_tool` (`document.body.innerText` after waiting ~4s and scrolling to the bottom) or `get_page_text`. WebFetch will not work.

## Step 1: Grade every pending race (both picks)

For each `ledger.csv` row where `status` or `second_status` is `pending` and the `race_date` is before today (or is today and the race has run), open the results URL for that track and date. Do not use the `pp_url` for grading: once the race date has passed, that page shows a "Buy Now" paywall. The results page is JSON; this pulls one race:
```js
const j=JSON.parse(document.body.innerText); const r=j.races.find(x=>x.raceKey.raceNumber==RACENUMBER);
JSON.stringify({top3:r.runners.map(x=>[x.programNumberStripped,x.horseName.trim(),x.winPayoff,x.placePayoff,x.showPayoff]), alsoRan:r.alsoRan, scratches:r.scratches.map(s=>s.horseName||s)})
```
`top3` is the first three finishers in order, with each one's $2 Win/Place/Show prices. `alsoRan` lists the rest **in finish order** (the first also-ran finished 4th, the next 5th, and so on).

Grade the top pick (`pick_horse`) and the second choice (`second_choice`) the same way, assuming $2 Win + $2 Place + $2 Show ($6) on each:
- Finished 1st: returned = its Win + Place + Show prices
- Finished 2nd: returned = its Place + Show prices
- Finished 3rd: returned = its Show price
- Worse than 3rd: returned = 0
- Prices are already per $2, so use them as is. In a dead heat, use the prices listed for that horse.

Top pick fields: `finish_position`, `win_payout`, `place_payout`, `show_payout` (what its tickets paid, 0 where they lost), `wagered` = 6, `returned`, `net` = returned − 6, `winner`, `winner_win_payout`, `graded_on` = today, `status` = `graded`.
Second choice fields: `second_finish`, `second_win_payout`, `second_place_payout`, `second_show_payout`, `second_wagered` = 6, `second_returned`, `second_net` = returned − 6, `second_status` = `graded`.

- If a horse **scratched**: set its status to `scratched`, wagered/returned/net = 0 (refund), and say so in `notes`.
- If results are not posted yet (race cancelled or postponed), leave it `pending` and add a note. If a row is still pending 3+ days after `race_date`, set both statuses to `void`, with wagered/returned/net = 0.

## Step 1b: Write the race recap

For every graded race that has no file in `recaps\` yet, write `recaps\YYYY-MM-DD_TRACKCODE_R#.md` (same name as its handicap file). Look at `recaps\2026-10-21_KEE_R7.md` for the tone and shape.

**Gather the facts:**
- From the results JSON: finish order, the top three's $2 Win/Place/Show prices, `trackConditionDescription`, `distanceDescription`, `surfaceDescription`, the race name or class, fractions and final time (`r.fraction`: each `fractionN.timeInHundredths` plus `winningTime.timeInHundredths`), scratches, and the exacta and trifecta from `r.payoffs` (`wagerName`, `winningNumbers`, `payoffAmount`).
- **Trip notes, only on race day:** open the race's `pp_url` the same day. If it shows the "$2 Mutuel Prices" block, the chart below it has a trip comment for every horse (e.g. "SHOWA broke a step slow, ... drove clear"). Use those for the "What happened" section. After race day the page is paywalled ("Buy Now"); do not buy anything. In that case, put this line right under the result: `*DRF's free chart with trip notes was no longer available when this recap was written, so it uses the official result only.*`
- From the handicap write-up: the top pick's and second choice's cases, the pace read, the named risks, and what it said about the eventual winner.

**Write it** with this shape:
```
# Recap: <Track> Race <N>, <Day Mon DD>

**Result:** <Winner> won ($W, $P, $S), <2nd> 2nd, <3rd> 3rd. <Race name/class>, <distance> on a <condition> <surface> track in <final time> (<fractions>). Exacta <numbers> paid $<x>. <Scratches or "No scratches.">

## Our picks
- **<Top pick> (<ML>), top pick: <finish>.** <what its tickets paid> (**<+/- net>**).
- **<Second pick> (<ML>), second pick: <finish>.** <...> (**<+/- net>**).
- Top 2 Picks net for the race: **<+/- net>**.

## What happened
<How the race was run: pace (compare the fractions to the write-up's pace projection), where the winner and our picks were, trip trouble from the chart comments when available.>

## Grading the handicap
<What the write-up got right and wrong, honestly. Was the winner off the list, ranked, or dismissed? Did the named risk happen? Did a scratch call hold?>

## Takeaway
<One or two sentences: the lesson for the method, tied to patterns in earlier recaps when there is one.>
```
Rules: use the user's writing style (no em-dashes, American spelling, plain and confident, no "not this, but that" phrasing). Never invent trip details: describe positions or trouble only when the chart comments say so. A horse's approximate post-time odds are its $2 win price ÷ 2 − 1; when the winner or a pick went off below 3.5-1 even though its morning line was playable, say so, since the bet would not have qualified at post time. Keep it to about 250 to 350 words.

## Step 2: Find the race to handicap

1. Open `https://www.drf.com/race-of-the-day`. The page says e.g. "THURSDAY'S FEATURED RACE / Keeneland - Race 8", and below that lists "Upcoming Race of the Day PPs".
2. Get the PP URLs. The "Free PPs" buttons open new tabs with `window.open`, so capture them instead of clicking blindly:
   ```js
   window.__opened=[]; window.open=function(u){window.__opened.push(String(u)); return null};
   for (const el of [...document.querySelectorAll('a,button')].filter(e=>e.innerText.trim()==='Free PPs')) { el.click(); await new Promise(r=>setTimeout(r,800)); }
   window.__opened.filter(u=>u.includes('/pp-details/'))
   ```
   Fallback: build the URL yourself from today's date, the race number, and the track code (the track menu on the same page pairs each name with its code, e.g. Keeneland = KEE, Remington Park = RP, Woodbine = WO).
3. Pick the target race:
   - Normally it is **today's** featured race.
   - If today's race is already in `ledger.csv`, skip to Step 4.
   - If today's race **has already run** (the PP page shows a "$2 Mutuel Prices" result block or "OFF AT"), do NOT handicap it, since the result is on screen. Use the next upcoming Race of the Day that isn't in the ledger yet (usually tomorrow's). If none is available, log it and skip to Step 4.
   - If no Race of the Day exists today, log it and skip to Step 4.

## Step 3: Handicap it and record both picks

1. Open the race's PP URL in Chrome. Wait, scroll to the bottom so all horses load, and read the full page text. Confirm the horse count matches "Show Horses (N/N)" and that the "Register to access" gate is absent.
2. Use the Skill tool to run **`anthropic-skills:handicap-race`**, giving it the full PP text and naming the race (track, race number, date). This is an unattended run, so do not ask the user anything (which race, whether to print a sheet, etc.). Follow the skill's method fully, including the 3.5-to-1 minimum odds rule and its listed scratches. The skill names a top pick and a second choice; record both.
3. Save the full write-up to `handicaps\YYYY-MM-DD_TRACKCODE_R#.md` (race date), with the PP URL at the top.
4. Append one row to `ledger.csv`: race_date (YYYY-MM-DD), track_code, track_name, race_number, surface (and distance), pp_url, pick_program, pick_horse, pick_ml_odds (e.g. 8-1), second_choice, handicapped_on = today, status = `pending`, wagered = 6, notes = one-line reason for the pick, second_program, second_ml_odds, second_status = `pending`, second_wagered = 6. Leave the other result fields blank.
   - If the skill finds no horse at 3.5-1 or longer worth playing, record `status` = `no_play` (and `second_status` = `no_play`) with wagered/returned/net = 0 and the reason in notes.
   - If it names a top pick but no second choice, set `second_status` = `no_play` and `second_wagered` = 0.
   - Quote any CSV field that contains a comma. Keep the header row and column order unchanged.

## Step 4: Rebuild the Excel workbook

From the tracker folder, run:
1. `python build_workbook.py` (rebuilds `DRF Tracker.xlsx` from `ledger.csv`; every KPI and chart is a formula, so nothing needs computing by hand)
2. `powershell -NoProfile -ExecutionPolicy Bypass -File refresh_excel.ps1` (has Excel recalculate and save, so values show in OneDrive and phone previews; it must print `OK: recalculated, no formula errors`)

If step 1 says the file is open in Excel, or step 2 fails, the ledger is still correct: note `workbook not refreshed (<reason>)` in `run-log.md` and continue. The next run rebuilds it. If step 2 reports formula errors, list them in `run-log.md`.

## Step 5: Log, publish and finish

1. Append to `run-log.md`: `YYYY-MM-DD HH:MM | graded: <race: top pick finish (net), 2nd pick finish (net)> | recap: <race (trip notes | results only)> | new pick: <date track R# top pick (odds) / 2nd pick (odds)> | Top Pick net: $X | Top 2 net: $Y`. Top Pick net = sum of `net` over rows with `status` graded. Top 2 net = that plus the sum of `second_net` over rows with `second_status` graded. Start the line with `evening` after the time on evening runs.
2. Publish the mobile results page (GitHub Pages serves `docs/index.html` from the `main` branch of `msvolos/WinnersGalore`). From the tracker folder:
   ```
   python build_site.py
   git add -A
   git commit -m "Daily update YYYY-MM-DD"
   git push origin main
   ```
   Commit only files in this folder; `.gitignore` already leaves out the Excel workbook. Never force-push, rewrite history, or change git config or credentials. If the push fails (no network, sign-in expired), leave the commit in place, add `publish failed (<reason>)` to today's `run-log.md` line, commit that, and continue. The next run's push sends both.
3. Close the Chrome tabs you opened. End with a 2 to 3 line chat summary of the same.
