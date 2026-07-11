"""Playwright fixtures.

pytest-playwright provides `page`; we add a logged-in variant so flow tests
don't repeat the login dance. Note what is ABSENT here versus the Selenium
conftest: no wait helpers, no timeout plumbing. Playwright's locators
auto-wait, so the framework carries that concern instead of the test author.
"""

import pytest


@pytest.fixture()
def signed_in_page(page, live_server):
    page.goto(f"{live_server}/login")
    page.get_by_test_id("username").fill("fern")
    page.get_by_test_id("password").fill("fiddlehead")
    page.get_by_test_id("login-submit").click()
    page.wait_for_url("**/catalog")
    return page
