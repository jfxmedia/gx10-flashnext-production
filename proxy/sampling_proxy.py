#!/usr/bin/env python3
"""OpenAI-compatible proxy that supplies deterministic defaults only when omitted."""
import json
import os
import sys
from http import HTTPStatus
from http.client import HTTPConnection, HTTPSConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

HOP_BY_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade", "content-length", "host"}

def policy(body):
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return body, ()
    if not isinstance(payload, dict) or "messages" not in payload:
        return body, ()
    defaults = {"temperature": float(os.getenv("FLASHNEXT_DEFAULT_TEMPERATURE", "0")), "top_p": float(os.getenv("FLASHNEXT_DEFAULT_TOP_P", "1")), "top_k": int(os.getenv("FLASHNEXT_DEFAULT_TOP_K", "-1"))}
    injected = []
    for key, value in defaults.items():
        if key not in payload:
            payload[key] = value
            injected.append(key)
    return json.dumps(payload, separators=(",", ":")).encode(), tuple(injected)

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def forward(self):
        upstream = urlsplit(os.getenv("FLASHNEXT_PROXY_UPSTREAM", "http://127.0.0.1:8019"))
        if upstream.scheme not in {"http", "https"} or not upstream.hostname:
            return self.error(HTTPStatus.BAD_GATEWAY, "invalid upstream")
        body = self.rfile.read(int(self.headers.get("Content-Length", "0"))) if self.headers.get("Content-Length") else b""
        injected = ()
        if self.command in {"POST", "PUT", "PATCH"} and "application/json" in self.headers.get("Content-Type", ""):
            body, injected = policy(body)
        headers = {k:v for k,v in self.headers.items() if k.lower() not in HOP_BY_HOP}
        headers["Content-Length"] = str(len(body))
        cls = HTTPSConnection if upstream.scheme == "https" else HTTPConnection
        conn = cls(upstream.hostname, upstream.port, timeout=1800)
        try:
            conn.request(self.command, (upstream.path.rstrip("/") + self.path) or "/", body, headers)
            response = conn.getresponse()
            data = response.read()
            self.send_response(response.status, response.reason)
            for key, value in response.getheaders():
                if key.lower() not in HOP_BY_HOP:
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data)
            self.log_message("%s %s -> %s injected=%s", self.command, self.path, response.status, ",".join(injected) or "none")
        finally:
            conn.close()
    def error(self, status, message):
        data = json.dumps({"error":{"message":message,"type":"proxy_error"}}).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = forward
    def log_message(self, fmt, *args): print("[sampling-proxy] " + fmt % args, file=sys.stderr, flush=True)

if __name__ == "__main__":
    listen = urlsplit(os.getenv("FLASHNEXT_PROXY_LISTEN", "http://127.0.0.1:8021"))
    if not listen.hostname or not listen.port: raise SystemExit("FLASHNEXT_PROXY_LISTEN must include host and port")
    ThreadingHTTPServer((listen.hostname, listen.port), Handler).serve_forever()
