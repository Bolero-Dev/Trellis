"""The same critical paths as the Playwright suite, in Selenium.

Purpose: an honest side-by-side. Same app, same timing hazards, same
assertions in spirit — so the differences you see between this file and the
Playwright suite are framework differences, not test-design differences.
"""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .conftest import WAIT_SECONDS, by_testid, wait_text, wait_visible


def test_valid_login_lands_on_catalog(driver, live_server):
    driver.get(f"{live_server}/login")
    driver.find_element(*by_testid("username")).send_keys("fern")
    driver.find_element(*by_testid("password")).send_keys("fiddlehead")
    driver.find_element(*by_testid("login-submit")).click()

    WebDriverWait(driver, WAIT_SECONDS).until(EC.url_contains("/catalog"))
    assert "fern" in wait_visible(driver, "current-user").text


def test_wrong_password_shows_error(driver, live_server):
    driver.get(f"{live_server}/login")
    driver.find_element(*by_testid("username")).send_keys("fern")
    driver.find_element(*by_testid("password")).send_keys("wrong")
    driver.find_element(*by_testid("login-submit")).click()

    assert "Wrong username or password" in wait_visible(driver, "login-error").text


def test_late_featured_banner_appears(signed_in_driver):
    # The ~800ms-late element: without the explicit wait this is a
    # NoSuchElementException — the classic Selenium flake.
    banner = wait_visible(signed_in_driver, "featured-plant")
    assert "Featured today" in banner.text


def test_search_narrows_results_after_slow_api(signed_in_driver):
    signed_in_driver.find_element(*by_testid("search-box")).send_keys("fern")
    signed_in_driver.find_element(*by_testid("search-button")).click()

    # Must wait on the STATUS text, not the list: the list exists before the
    # slow API answers, so waiting on the wrong element passes vacuously.
    wait_text(signed_in_driver, "search-status", "1 plant found")
    items = signed_in_driver.find_elements(*by_testid("plant-1"))
    assert len(items) == 1 and "Fiddlehead Fern" in items[0].text


def test_full_purchase_journey(signed_in_driver, live_server):
    signed_in_driver.find_element(*by_testid("add-7")).click()      # Dahlia
    wait_text(signed_in_driver, "cart-count", "1")

    signed_in_driver.find_element(*by_testid("cart-link")).click()
    wait_visible(signed_in_driver, "to-checkout").click()

    signed_in_driver.find_element(*by_testid("order-name")).send_keys("Fern Gardener")
    signed_in_driver.find_element(*by_testid("order-email")).send_keys("fern@example.com")
    signed_in_driver.find_element(*by_testid("order-address")).send_keys("12 Greenhouse Lane, Portland")
    signed_in_driver.find_element(*by_testid("place-order")).click()

    heading = wait_visible(signed_in_driver, "confirm-heading")
    assert heading.text == "Order confirmed"
    assert wait_visible(signed_in_driver, "order-id").text.startswith("TR-")
