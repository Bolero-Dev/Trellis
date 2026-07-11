"""Catalog behaviors — including both deliberate timing hazards.

None of these tests contains a sleep. That is the entire point: the search
API answers ~400ms late and the featured banner renders ~800ms late, and
Playwright's auto-waiting assertions absorb both.
"""

from playwright.sync_api import Page, expect


def test_late_featured_banner_appears(signed_in_page: Page):
    # Renders ~800ms after load. expect() polls until it exists (or times out).
    expect(signed_in_page.get_by_test_id("featured-plant")).to_be_visible()


def test_search_narrows_results_after_slow_api(signed_in_page: Page):
    signed_in_page.get_by_test_id("search-box").fill("fern")
    signed_in_page.get_by_test_id("search-button").click()

    # The list rebuilds only after the delayed API answers; these assertions
    # wait for that state rather than checking the DOM immediately.
    expect(signed_in_page.get_by_test_id("search-status")).to_contain_text("1 plant found")
    expect(signed_in_page.get_by_test_id("plant-list").locator("li")).to_have_count(1)
    expect(signed_in_page.get_by_test_id("plant-1")).to_contain_text("Fiddlehead Fern")


def test_category_and_stock_filters_compose(signed_in_page: Page):
    signed_in_page.get_by_test_id("category-filter").select_option("shade")
    signed_in_page.get_by_test_id("in-stock-only").check()
    signed_in_page.get_by_test_id("search-button").click()

    expect(signed_in_page.get_by_test_id("search-status")).to_contain_text("3 plants found")
    expect(signed_in_page.get_by_test_id("plant-3")).to_have_count(0)  # Hosta: out of stock


def test_no_match_says_so(signed_in_page: Page):
    signed_in_page.get_by_test_id("search-box").fill("triffid")
    signed_in_page.get_by_test_id("search-button").click()

    expect(signed_in_page.get_by_test_id("search-status")).to_contain_text("No plants matched")
    expect(signed_in_page.get_by_test_id("plant-list").locator("li")).to_have_count(0)


def test_out_of_stock_add_button_is_disabled(signed_in_page: Page):
    expect(signed_in_page.get_by_test_id("add-3")).to_be_disabled()  # Hosta
