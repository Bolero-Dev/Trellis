"""Pure-logic tests: no server, no browser. The fastest tier of the pyramid."""

from app import catalog


class TestSearch:
    def test_no_filters_returns_everything(self):
        assert len(catalog.search()) == len(catalog.PLANTS)

    def test_query_is_case_insensitive_substring(self):
        names = [p.name for p in catalog.search(query="FeRn")]
        assert names == ["Fiddlehead Fern"]

    def test_category_filter(self):
        assert all(p.category == "shade" for p in catalog.search(category="shade"))
        assert len(catalog.search(category="shade")) == 4

    def test_in_stock_filter_drops_zero_stock(self):
        results = catalog.search(in_stock_only=True)
        assert all(p.stock > 0 for p in results)
        assert not any(p.name in ("Hosta", "Snowdrop") for p in results)

    def test_filters_compose(self):
        results = catalog.search(query="o", category="shade", in_stock_only=True)
        assert [p.name for p in results] == ["Columbine"]

    def test_no_match_returns_empty(self):
        assert catalog.search(query="triffid") == []


class TestCartMath:
    def test_total_sums_lines(self):
        # Lavender 9.50 x2 + Basil 3.75 x1
        assert catalog.cart_total({"2": 2, "9": 1}) == 22.75

    def test_unknown_ids_are_ignored(self):
        assert catalog.cart_total({"999": 3}) == 0.0

    def test_empty_cart_is_zero(self):
        assert catalog.cart_total({}) == 0.0


class TestOrderValidation:
    def test_valid_order_has_no_errors(self):
        assert catalog.validate_order("Fern G.", "fern@example.com",
                                      "12 Greenhouse Lane, Portland") == {}

    def test_blank_name_rejected(self):
        assert "name" in catalog.validate_order("  ", "a@b.com", "12 Greenhouse Lane")

    def test_bad_emails_rejected(self):
        for email in ("no-at-sign", "@leading", "trailing@"):
            assert "email" in catalog.validate_order("F", email, "12 Greenhouse Lane")

    def test_short_address_rejected(self):
        assert "address" in catalog.validate_order("F", "a@b.com", "short")
