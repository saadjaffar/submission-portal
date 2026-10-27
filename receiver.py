import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ.get("RECEIVER_TOKEN", "")
OUTPUT = "test-report.json"
PORT = int(os.environ.get("PORT", "5001"))


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, text):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def do_POST(self):
        if self.path != "/report":
            return self._reply(404, "not found")
        if TOKEN and self.headers.get("X-Token") != TOKEN:
            return self._reply(401, "unauthorized")
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self._reply(400, "invalid json")
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {OUTPUT}: status={data.get('status')} "
              f"commit={str(data.get('commit_sha'))[:7]}")
        self._reply(200, "saved")


if __name__ == "__main__":
    print(f"Receiver listening on http://localhost:{PORT}/report")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()