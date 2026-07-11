"""Catalog data and pure logic.

No Flask imports here on purpose: everything in this module is unit-testable
without a server, which keeps the fast test tier fast.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Plant:
    id: int
    name: str
    category: str
    price: float
    stock: int

    @property
    def in_stock(self) -> bool:
        return self.stock > 0


PLANTS = [
    Plant(1, "Fiddlehead Fern", "shade", 14.00, 12),
    Plant(2, "Lavender", "sun", 9.50, 30),
    Plant(3, "Hosta", "shade", 11.00, 0),
    Plant(4, "Tomato Starter", "vegetable", 4.25, 48),
    Plant(5, "Columbine", "shade", 8.75, 7),
    Plant(6, "Rosemary", "herb", 6.00, 22),
    Plant(7, "Dahlia", "sun", 12.50, 16),
    Plant(8, "Pothos", "houseplant", 13.00, 9),
    Plant(9, "Basil", "herb", 3.75, 40),
    Plant(10, "Snowdrop", "shade", 7.25, 0),
]

CATEGORIES = sorted({p.category for p in PLANTS})


def get(plant_id: int) -> Plant | None:
    return next((p for p in PLANTS if p.id == plant_id), None)


def search(query: str = "", category: str = "", in_stock_only: bool = False) -> list[Plant]:
    """Case-insensitive substring search, optionally narrowed by category/stock."""
    q = query.strip().lower()
    results = PLANTS
    if q:
        results = [p for p in results if q in p.name.lower()]
    if category:
        results = [p for p in results if p.category == category]
    if in_stock_only:
        results = [p for p in results if p.in_stock]
    return results


def cart_total(cart: dict[str, int]) -> float:
    """cart maps plant-id (as str, since it round-trips through the session) to qty."""
    total = 0.0
    for pid, qty in cart.items():
        plant = get(int(pid))
        if plant is not None:
            total += plant.price * qty
    return round(total, 2)


def validate_order(name: str, email: str, address: str) -> dict[str, str]:
    """Returns a dict of field -> error message; empty dict means valid."""
    errors: dict[str, str] = {}
    if not name.strip():
        errors["name"] = "Name is required."
    if "@" not in email or email.strip().startswith("@") or email.strip().endswith("@"):
        errors["email"] = "Enter a valid email address."
    if len(address.strip()) < 8:
        errors["address"] = "Enter a full delivery address."
    return errors
