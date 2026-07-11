"""Shared fixtures: the live server both browser suites run against."""

import threading

import pytest
from werkzeug.serving import make_server

from app import create_app

HOST = "127.0.0.1"
PORT = 5111


@pytest.fixture(scope="session")
def live_server():
    """Runs the real app in a background thread for browser tests.

    Session-scoped: one server for the whole run — the app is stateless
    per-session (carts live in signed cookies), so tests stay independent.
    """
    server = make_server(HOST, PORT, create_app(), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://{HOST}:{PORT}"
    server.shutdown()
    thread.join(timeout=5)
