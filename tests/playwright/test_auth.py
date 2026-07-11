"""Login flows through a real browser."""

from playwright.sync_api import Page, expect


def test_valid_login_lands_on_catalog(page: Page, live_server):
    page.goto(f"{live_server}/login")
    page.get_by_test_id("username").fill("fern")
    page.get_by_test_id("password").fill("fiddlehead")
    page.get_by_test_id("login-submit").click()

    expect(page).to_have_url(f"{live_server}/catalog")
    expect(page.get_by_test_id("current-user")).to_contain_text("fern")


def test_wrong_password_shows_error_and_stays(page: Page, live_server):
    page.goto(f"{live_server}/login")
    page.get_by_test_id("username").fill("fern")
    page.get_by_test_id("password").fill("wrong")
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_role("alert")).to_contain_text("Wrong username or password")
    expect(page).to_have_url(f"{live_server}/login")


def test_logout_returns_to_login(signed_in_page: Page, live_server):
    signed_in_page.get_by_test_id("logout").click()
    expect(signed_in_page).to_have_url(f"{live_server}/login")
