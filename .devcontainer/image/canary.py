#!/usr/bin/env python3
"""Canary listener for K7 Tripwire: records every request to canary.fieldagents.test:8081.

Never forwards anything. Each hit is one JSON line in /tmp/canary.log. Stdlib only.
"""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = "/tmp/canary.log"


class Canary(BaseHTTPRequestHandler):
    def _hit(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(min(length, 65536)).decode("utf-8", "replace") if length else ""
        with open(LOG, "a") as f:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "method": self.command,
                                "path": self.path, "body": body}) + "\n")
        self.send_response(204)
        self.end_headers()

    do_GET = do_POST = do_PUT = do_HEAD = _hit

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    open(LOG, "a").close()
    ThreadingHTTPServer(("127.0.0.1", 8081), Canary).serve_forever()
