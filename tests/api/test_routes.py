"""HTTP-level tests via Flask's test client: real routes, no browser."""

import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def login(client, username="fern", password="fiddlehead"):
    return client.post("/login", data={"username": username, "password": password},
                       follow_redirects=True)


class TestAuth:
    def test_valid_login_reaches_catalog(self, client):
        resp = login(client)
        assert resp.status_code == 200
        assert b"Catalog" in resp.data

    def test_wrong_password_shows_error(self, client):
        resp = login(client, password="wrong")
        assert b"Wrong username or password" in resp.data

    def test_catalog_requires_login(self, client):
        resp = client.get("/catalog")
        assert resp.status_code == 302 and "/login" in resp.headers["Location"]


class TestSearchApi:
    def test_search_returns_shape_and_count(self, client):
        data = client.get("/api/search?q=fern").get_json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Fiddlehead Fern"
        assert set(data["results"][0]) == {"id", "name", "category", "price", "in_stock"}

    def test_in_stock_flag_filters(self, client):
        data = client.get("/api/search?in_stock=1").get_json()
        assert all(r["in_stock"] for r in data["results"])


class TestCart:
    def test_add_then_cart_shows_item_and_total(self, client):
        login(client)
        client.post("/cart/add/2")  # Lavender 9.50
        client.post("/cart/add/2")
        resp = client.get("/cart")
        assert b"Lavender" in resp.data
        assert b"$19.00" in resp.data

    def test_out_of_stock_add_is_rejected(self, client):
        login(client)
        resp = client.post("/cart/add/3")  # Hosta, stock 0
        assert resp.status_code == 409

    def test_remove_empties_cart(self, client):
        login(client)
        client.post("/cart/add/9")
        client.post("/cart/remove/9")
        assert b"Your cart is empty" in client.get("/cart").data


class TestCheckout:
    def test_empty_cart_redirects_to_catalog(self, client):
        login(client)
        resp = client.get("/checkout")
        assert resp.status_code == 302 and "/catalog" in resp.headers["Location"]

    def test_invalid_form_rerenders_with_errors_and_keeps_cart(self, client):
        login(client)
        client.post("/cart/add/9")
        resp = client.post("/checkout", data={"name": "", "email": "bad", "address": "x"})
        assert b"Name is required" in resp.data
        assert b"valid email" in resp.data
        # Cart must survive a failed checkout.
        assert b"Basil" in client.get("/cart").data

    def test_valid_order_confirms_and_clears_cart(self, client):
        login(client)
        client.post("/cart/add/9")
        resp = client.post("/checkout", data={
            "name": "Fern Gardener", "email": "fern@example.com",
            "address": "12 Greenhouse Lane, Portland",
        })
        assert b"Order confirmed" in resp.data
        assert b"TR-" in resp.data
        assert b"Your cart is empty" in client.get("/cart").data
