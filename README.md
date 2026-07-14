# Trellis

I built Trellis to answer a question with evidence instead of opinions: if you're
starting new web test automation in 2026, should you use Playwright or Selenium?

So this repo is three things:

1. A small web app I built specifically to be tested — a plant nursery storefront
   with real timing problems, on purpose
2. A full Playwright suite
3. A Selenium suite covering the same user flows, so the two frameworks can be
   compared on identical ground

A trellis is the structure a climbing plant grows on. The app is the plant. The
test architecture is what holds it up.

## Why the app is slow on purpose

Real apps are slow and asynchronous in ways demo apps never are. So I gave mine
two deliberate hazards:

- the search API answers about 400ms late (pretend the backend is having a day)
- a "featured plant" banner renders about 800ms after page load (pretend it's a
  recommendation widget)

If a test grabs the DOM too early, the element isn't there yet. That's where most
flaky browser tests come from. Both suites have to survive both hazards without a
single `sleep()` — and how much work that takes is the actual comparison.

## The three tiers

| Tier | Command | What it covers | Speed |
|---|---|---|---|
| Logic + HTTP | `pytest` | business rules, routes, validation, cart math | ~1s, no browser |
| Playwright | `pytest tests/playwright` | real user flows in Chromium | ~15s |
| Selenium | `pytest tests/selenium_suite` | the same flows, for comparison | ~20s |

Most bugs don't need a browser to find. The fast tier exists because I respect
the test pyramid even in a repo that's about browser automation.

## What I found

**Waiting.** In Playwright I never wrote a wait — `expect()` polls until the
condition holds, so the slow search and the late banner cost me zero extra code.
In Selenium I wrote every wait myself, and I had to pick the right thing to wait
on: in `test_search_narrows_results_after_slow_api`, waiting on the list instead
of the status text would pass without testing anything. That trap doesn't exist
in the Playwright version.

The shortest version of this whole evaluation: diff the two `conftest.py` files.
Playwright's is about 15 lines. Selenium's is about 60. The extra lines are
waiting machinery I had to build and now have to maintain.

**Selectors.** Both suites target `data-testid` attributes, so tests don't break
when copy or styling changes. Playwright has this built in (`get_by_test_id`);
in Selenium I wrote a helper for it.

**When things fail.** Playwright records a full trace on failure in CI — DOM
snapshots, network, the works. Selenium gives you a screenshot and a stack trace.
When my own test failed (more on that below), Playwright's error showed me the
status element resolving five times as "Searching…" and nine times as the final
text. That's the debugging experience, side by side.

**Where Selenium still earns its keep.** Huge install base, every language
binding, Grid for weird browser/OS combinations, and twenty years of teams who
know it cold. If your suite is already Selenium and it's stable, that's an asset.
This verdict is about where new work goes, not about rewriting what works.

**My verdict:** for new Python web automation, Playwright — the auto-waiting
model removes the biggest cause of flaky E2E tests before you write a line. I
keep the Selenium fluency because most of the world's regression suites still
run on it, and that's exactly why the comparison suite is here.

## The bug I shipped

My first CI run failed. Not the app — my test. I asserted that "shade + in stock"
returns 3 plants, and it returns 2, because I miscounted my own catalog (Hosta
and Snowdrop are shade plants with zero stock). The app was right and I wasn't.

I left the story in the test's comments instead of scrubbing it, because wrong
expectations are the most common bug in test code, and pretending otherwise
helps nobody.

## Running it

```bash
pip install -r requirements.txt
playwright install chromium

pytest                        # fast tier (~1s)
pytest tests/playwright       # Playwright suite
pytest tests/selenium_suite   # Selenium suite (needs Chrome)

flask --app app run           # or just poke around: user fern / fiddlehead
```

CI runs all three tiers on every push and keeps Playwright traces when
anything fails.

## Layout

```
app/                    the app under test (Flask, ~300 lines, in-memory data)
  catalog.py            pure logic — testable without a server
  routes.py             auth, catalog, the slow search API, cart, checkout
tests/
  conftest.py           shared live-server fixture (real server, background thread)
  api/                  fast tier: logic + HTTP through Flask's test client
  playwright/           the main suite
  selenium_suite/       same critical paths, explicit-wait style
```

---

Built by Liza Sloane — [github.com/Bolero-Dev](https://github.com/Bolero-Dev)
