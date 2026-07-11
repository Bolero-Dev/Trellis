#
# Trellis — app under test
#
# A deliberately small nursery storefront that exists to be tested. Its timing
# hazards (delayed search results, late-rendering elements) are load-bearing:
# they are exactly the behaviors that browser-automation frameworks differ on,
# which is the point of this repository.
#

from flask import Flask


def create_app():
    app = Flask(__name__)
    # Test application — this key protects nothing and pretends to less.
    app.secret_key = "trellis-app-under-test"
    from .routes import bp
    app.register_blueprint(bp)
    return app
