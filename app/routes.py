import time

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   session, url_for)

from . import catalog

bp = Blueprint("trellis", __name__)

# One test user. The password is public because the app exists to be tested.
USERS = {"fern": "fiddlehead"}

# The search API answers slowly on purpose — a stand-in for a real backend
# under load. Browser tests must handle this without sleep() calls.
SEARCH_DELAY_SECONDS = 0.4


def current_cart() -> dict[str, int]:
    return session.setdefault("cart", {})


# --- Auth ---------------------------------------------------------------

@bp.route("/", methods=["GET"])
def index():
    if session.get("user"):
        return redirect(url_for("trellis.catalog_page"))
    return redirect(url_for("trellis.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if USERS.get(username) == password:
            session["user"] = username
            session["cart"] = {}
            return redirect(url_for("trellis.catalog_page"))
        error = "Wrong username or password."
    return render_template("login.html", error=error)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("trellis.login"))


# --- Catalog ------------------------------------------------------------

@bp.route("/catalog")
def catalog_page():
    if not session.get("user"):
        return redirect(url_for("trellis.login"))
    return render_template(
        "catalog.html",
        user=session["user"],
        plants=catalog.PLANTS,
        categories=catalog.CATEGORIES,
        cart_count=sum(current_cart().values()),
    )


@bp.route("/api/search")
def api_search():
    time.sleep(SEARCH_DELAY_SECONDS)  # deliberate: see module docstring
    results = catalog.search(
        query=request.args.get("q", ""),
        category=request.args.get("category", ""),
        in_stock_only=request.args.get("in_stock") == "1",
    )
    return jsonify({
        "count": len(results),
        "results": [
            {"id": p.id, "name": p.name, "category": p.category,
             "price": p.price, "in_stock": p.in_stock}
            for p in results
        ],
    })


# --- Cart ---------------------------------------------------------------

@bp.route("/cart")
def cart_page():
    if not session.get("user"):
        return redirect(url_for("trellis.login"))
    cart = current_cart()
    items = []
    for pid, qty in cart.items():
        plant = catalog.get(int(pid))
        if plant:
            items.append({"plant": plant, "qty": qty,
                          "line_total": round(plant.price * qty, 2)})
    return render_template("cart.html", items=items,
                           total=catalog.cart_total(cart),
                           cart_count=sum(cart.values()), user=session["user"])


@bp.route("/cart/add/<int:plant_id>", methods=["POST"])
def cart_add(plant_id):
    if not session.get("user"):
        return redirect(url_for("trellis.login"))
    plant = catalog.get(plant_id)
    if plant is None:
        return "No such plant", 404
    if not plant.in_stock:
        return "Out of stock", 409
    cart = current_cart()
    cart[str(plant_id)] = cart.get(str(plant_id), 0) + 1
    session.modified = True
    return redirect(url_for("trellis.catalog_page"))


@bp.route("/cart/remove/<int:plant_id>", methods=["POST"])
def cart_remove(plant_id):
    if not session.get("user"):
        return redirect(url_for("trellis.login"))
    cart = current_cart()
    cart.pop(str(plant_id), None)
    session.modified = True
    return redirect(url_for("trellis.cart_page"))


# --- Checkout -----------------------------------------------------------

@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not session.get("user"):
        return redirect(url_for("trellis.login"))
    cart = current_cart()
    if not cart:
        return redirect(url_for("trellis.catalog_page"))

    errors: dict[str, str] = {}
    form = {"name": "", "email": "", "address": ""}
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in form}
        errors = catalog.validate_order(**form)
        if not errors:
            order_id = f"TR-{int(time.time()) % 100000:05d}"
            total = catalog.cart_total(cart)
            session["cart"] = {}
            return render_template("confirm.html", order_id=order_id,
                                   total=total, name=form["name"].strip(),
                                   user=session["user"], cart_count=0)

    return render_template("checkout.html", errors=errors, form=form,
                           total=catalog.cart_total(cart),
                           cart_count=sum(cart.values()), user=session["user"])
