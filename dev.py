from __future__ import annotations

import argparse
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

from renderer import OUTPUT, existing_numbers, render_one


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    parser = argparse.ArgumentParser(description="Render and preview a post locally.")
    parser.add_argument(
        "number",
        nargs="?",
        type=int,
        help="Post number. If omitted, the latest post is used.",
    )
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    numbers = existing_numbers()
    if not numbers:
        raise SystemExit("No posts found in posts/.")

    number = args.number if args.number is not None else numbers[-1]
    if number not in numbers:
        raise SystemExit(f"Post {number:03d} does not exist.")

    render_one(number, screenshots=False)

    post_dir = OUTPUT / f"{number:03d}"
    url = f"http://127.0.0.1:{args.port}/preview.html"

    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(post_dir), **kw
    )

    with ReusableTCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"Previewing post {number:03d}")
        print(url)
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
