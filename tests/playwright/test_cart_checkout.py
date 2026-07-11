"""The money path: add to cart, survive a validation failure, place the order."""

import re

from playwright.sync_api import Page, expect


def test_add_to_cart_updates_badge_and_total(signed_in_page: Page):
    signed_in_page.get_by_test_id("add-2").click()   # Lavender $9.50
    expect(signed_in_page.get_by_test_id("cart-count")).to_have_text("1")

    signed_in_page.get_by_test_id("add-2").click()
    expect(signed_in_page.get_by_test_id("cart-count")).to_have_text("2")

    signed_in_page.get_by_test_id("cart-link").click()
    expect(signed_in_page.get_by_test_id("cart-total")).to_have_text("$19.00")


def test_remove_from_cart(signed_in_page: Page):
    signed_in_page.get_by_test_id("add-9").click()   # Basil
    signed_in_page.get_by_test_id("cart-link").click()
    signed_in_page.get_by_test_id("remove-9").click()
    expect(signed_in_page.get_by_test_id("cart-empty")).to_be_visible()


def test_checkout_validation_failure_preserves_cart(signed_in_page: Page):
    signed_in_page.get_by_test_id("add-6").click()   # Rosemary
    signed_in_page.get_by_test_id("cart-link").click()
    signed_in_page.get_by_test_id("to-checkout").click()

    signed_in_page.get_by_test_id("order-email").fill("not-an-email")
    signed_in_page.get_by_test_id("place-order").click()

    expect(signed_in_page.get_by_test_id("error-name")).to_be_visible()
    expect(signed_in_page.get_by_test_id("error-email")).to_contain_text("valid email")
    # The typo survives the round-trip; the user's work is not thrown away.
    expect(signed_in_page.get_by_test_id("order-email")).to_have_value("not-an-email")
    # And the cart is intact.
    expect(signed_in_page.get_by_test_id("cart-count")).to_have_text("1")


def test_full_purchase_journey(signed_in_page: Page):
    signed_in_page.get_by_test_id("add-7").click()   # Dahlia $12.50
    signed_in_page.get_by_test_id("cart-link").click()
    signed_in_page.get_by_test_id("to-checkout").click()

    signed_in_page.get_by_test_id("order-name").fill("Fern Gardener")
    signed_in_page.get_by_test_id("order-email").fill("fern@example.com")
    signed_in_page.get_by_test_id("order-address").fill("12 Greenhouse Lane, Portland")
    signed_in_page.get_by_test_id("place-order").click()

    expect(signed_in_page.get_by_test_id("confirm-heading")).to_be_visible()
    expect(signed_in_page.get_by_test_id("order-id")).to_have_text(re.compile(r"TR-\d{5}"))
    expect(signed_in_page.get_by_test_id("confirm-total")).to_have_text("$12.50")
    expect(signed_in_page.get_by_test_id("cart-count")).to_have_text("0")
