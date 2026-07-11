"""Selenium fixtures.

Contrast with the Playwright conftest: here the waiting machinery is OURS to
build and maintain. Every helper below is boilerplate Playwright doesn't need
— which is a finding of this evaluation, not a complaint.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WAIT_SECONDS = 5


@pytest.fixture()
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Chrome(options=options)
    # Deliberately NO implicit wait: mixing implicit and explicit waits causes
    # unpredictable timeouts. All waiting is explicit and visible in the tests.
    yield drv
    drv.quit()


def by_testid(testid: str):
    return (By.CSS_SELECTOR, f'[data-testid="{testid}"]')


def wait_visible(driver, testid: str, timeout: int = WAIT_SECONDS):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(by_testid(testid))
    )


def wait_text(driver, testid: str, text: str, timeout: int = WAIT_SECONDS):
    return WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element(by_testid(testid), text)
    )


@pytest.fixture()
def signed_in_driver(driver, live_server):
    driver.get(f"{live_server}/login")
    driver.find_element(*by_testid("username")).send_keys("fern")
    driver.find_element(*by_testid("password")).send_keys("fiddlehead")
    driver.find_element(*by_testid("login-submit")).click()
    WebDriverWait(driver, WAIT_SECONDS).until(EC.url_contains("/catalog"))
    return driver
