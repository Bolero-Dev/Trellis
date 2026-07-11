# Trellis

**A web-automation framework evaluation, with the evidence included.**

Trellis is three things in one repository: a small web app built to be tested
(a nursery storefront with *deliberate* timing hazards), a full **Playwright**
suite in Python, and a **Selenium** suite covering the same critical paths —
so the differences between the two frameworks are visible side by side, on
identical ground, instead of argued about in the abstract.

A trellis is the structure a climbing plant grows on. Same job here: the app
is the plant, the test architecture is what holds it up.

## Why the app under test is intentionally annoying

Real applications are slow and asynchronous in ways demo apps never are. So
Trellis's storefront ships two load-bearing hazards:

- the search API answers **~400ms late** (a stand-in for a backend under load),
  and results render only after it does;
- a "featured plant" banner renders **~800ms after page load** (a stand-in for
  every recommendation widget ever built).

These are exactly the behaviors that make naive browser tests flaky — grab the
DOM too early and the element isn't there yet. Both suites must survive both
hazards **without a single `sleep()`**, which is where the frameworks show
their character.

## The three tiers

| Tier | Command | What it proves | Speed |
|---|---|---|---|
| Logic + HTTP | `pytest` | business rules, routes, validation, cart math | ~1s, no browser |
| Playwright | `pytest tests/playwright` | real user flows through Chromium | ~15s |
| Selenium | `pytest tests/selenium_suite` | the same flows, for comparison | ~20s |

The fast tier exists because most defects don't need a browser to find —
the pyramid is respected even in a repo that exists to showcase browser
automation.

## Findings: Playwright vs. Selenium, same app, same tests

**Waiting.** Playwright's `expect(locator)` assertions poll until the
condition holds; the late banner and slow search need *zero* extra code.
In Selenium, every one of those waits is authored by hand (`WebDriverWait` +
`expected_conditions`), and choosing the *wrong wait target* passes vacuously
— see `test_search_narrows_results_after_slow_api`, where waiting on the list
instead of the status line would test nothing. The Selenium conftest carries
helper plumbing that Playwright's conftest simply doesn't have; diff the two
`conftest.py` files for the shortest version of this whole evaluation.

**Selectors.** Both suites target `data-testid` attributes (stable contract
between app and tests, immune to copy and styling changes). Playwright has
first-class `get_by_test_id`/`get_by_role`; Selenium reaches the same
elements through CSS selectors built by a helper we had to write.

**Failure forensics.** Playwright records traces on failure
(`--tracing retain-on-failure` in CI) — a full replay with DOM snapshots and
network. Selenium's out-of-the-box answer is a screenshot and a stack trace.

**Where Selenium still earns its keep.** Enormous existing install base,
every language binding under the sun, Grid for exotic browser/OS matrices,
and two decades of institutional knowledge. If a team's suite is already
Selenium and stable, that's an asset, not a liability — this repo's verdict
is about where *new* investment goes.

**Verdict.** For new Python test automation in 2026: Playwright, without much
hesitation — the waiting model alone eliminates the largest class of E2E
flakiness by construction. Keep Selenium fluency for the codebases that run
the world's regression suites, which is why the comparison suite exists at all.

## Running it

```bash
pip install -r requirements.txt
playwright install chromium

pytest                        # fast tier (~1s)
pytest tests/playwright       # Playwright suite
pytest tests/selenium_suite   # Selenium suite (needs Chrome installed)

flask --app app run           # or just click around: user fern / fiddlehead
```

CI runs all three tiers on every push (`.github/workflows/ci.yml`) and uploads
Playwright traces when anything fails.

## Layout

```
app/                    the app under test (Flask, ~300 lines, in-memory data)
  catalog.py            pure logic — unit-testable without a server
  routes.py             auth, catalog, slow search API, cart, checkout
tests/
  conftest.py           shared live-server fixture (real server, background thread)
  api/                  fast tier: logic + HTTP via Flask test client
  playwright/           the centerpiece suite
  selenium_suite/       same critical paths, explicit-wait style
```

---

Built by Liza Sloane — [github.com/Bolero-Dev](https://github.com/Bolero-Dev)
