"""Allow `python -m domainarena` to start the demo server."""
import sys
import os

# Ensure the package is importable
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from domainarena.web.demo import PORT  # noqa: E402

if __name__ == "__main__":
    print(f"Starting DomainArena demo on http://127.0.0.1:{PORT}")
    print(f"API available on http://127.0.0.1:8801")
    from http.server import ThreadingHTTPServer
    from domainarena.web.demo import Handler
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
