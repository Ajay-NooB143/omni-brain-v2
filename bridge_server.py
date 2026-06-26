"""OmniBrain V2 — Redis Bridge Server
HTTP API for VPS credential management + MT5 bridge.
No SSH needed between VPS instances — all config flows through Redis.
"""
import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from redis_utils import get_redis_connection
from redis_bridge import seed_default_credentials, set_credential

BRIDGE_PORT = int(os.getenv('BRIDGE_PORT', '8765'))
BRIDGE_KEY = os.getenv('BRIDGE_API_KEY', '')  # set this in .env!
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')


def _r():
    return get_redis_connection(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)


class BridgeHandler(BaseHTTPRequestHandler):
    def _auth(self):
        if BRIDGE_KEY and self.headers.get('X-API-Key') != BRIDGE_KEY:
            self.send_json(401, {'error': 'Unauthorized'})
            return False
        return True

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if not self._auth():
            return
        parsed = urlparse(self.path)

        if parsed.path == '/health':
            try:
                _r().ping()
                self.send_json(200, {'status': 'ok', 'redis': 'connected'})
            except Exception as e:
                self.send_json(503, {'status': 'error', 'redis': str(e)})

        elif parsed.path.startswith('/config/'):
            role = parsed.path.split('/config/')[1]
            key = f'creds:vps:{role}'
            data = _r().hgetall(key)
            if not data:
                self.send_json(404, {'error': f'No config for role: {role}'})
                return
            if 'pairs' in data:
                data['pairs'] = json.loads(data['pairs'])
            self.send_json(200, data)

        elif parsed.path == '/workers':
            raw = _r().get('config:workers')
            workers = json.loads(raw) if raw else []
            result = {}
            for wid in workers:
                wdata = _r().hgetall(f'creds:vps:{wid}')
                if wdata:
                    wdata['worker_id'] = wid
                    if 'pairs' in wdata:
                        wdata['pairs'] = json.loads(wdata['pairs'])
                    result[wid] = wdata
            self.send_json(200, {'workers': result})

        elif parsed.path == '/register':
            self.send_json(200, {
                'message': 'POST your role + IP to /register',
                'example': 'POST /register {"role":"worker-X","ip":"1.2.3.4","pairs":["BTC","ETH"]}'
            })

        else:
            self.send_json(404, {'error': 'Not found'})

    def do_POST(self):
        if not self._auth():
            return
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if parsed.path == '/register':
            role = body.get('role', '')
            ip = body.get('ip', '')
            if not role or not ip:
                self.send_json(400, {'error': 'role and ip required'})
                return
            key = f'creds:vps:{role}'
            existing = _r().hgetall(key)
            if existing:
                existing['ip'] = ip
                _r().hset(key, 'ip', ip)
            else:
                _r().hset(key, mapping={
                    'ip': ip,
                    'redis_host': REDIS_HOST,
                    'redis_port': str(REDIS_PORT),
                    'pairs': json.dumps(body.get('pairs', [])),
                    'account_balance': str(body.get('account_balance', 3333.33)),
                    'max_daily_loss': str(body.get('max_daily_loss', 2.0)),
                    'role': body.get('role', role),
                })
                if role not in (_r().get('config:workers') or '[]'):
                    _r().lpush('config:workers', role)
            self.send_json(200, {'status': 'registered', 'role': role, 'ip': ip})

        elif parsed.path == '/seed':
            seed_default_credentials()
            self.send_json(200, {'status': 'seeded'})

        elif parsed.path.startswith('/creds/'):
            key = parsed.path.split('/creds/')[1]
            for field, value in body.items():
                set_credential(key, field, value)
            self.send_json(200, {'status': 'updated', 'key': key})

        else:
            self.send_json(404, {'error': 'Not found'})

    def log_message(self, format, *args):
        sys.stderr.write(f"[BridgeServer] {args[0]} {args[1]} {args[2]}\n")


def main():
    print(f"OmniBrain Bridge Server — port {BRIDGE_PORT}")
    print(f"  Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"  API Key: {'set' if BRIDGE_KEY else 'NOT SET (insecure)'}")
    print()
    print("  POST /seed                  — seed default credentials into Redis")
    print("  POST /register              — register a VPS instance")
    print("  GET  /config/<role>         — get config for a role")
    print("  GET  /workers               — list all workers")
    print("  POST /creds/<key>           — set credential fields")
    print("  GET  /health                — health check")
    print()
    server = HTTPServer(('0.0.0.0', BRIDGE_PORT), BridgeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == '__main__':
    main()
