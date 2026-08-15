#!/usr/bin/env python3
"""
backup_server.py - Lightweight REST API server for oathsworn-webapp volume backups.
Listens on port 8081 inside the container (reverse proxied by Caddy on /api/*).
"""

import json
import os
import re
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

BACKUP_DIR = os.environ.get('BACKUP_DIR', '/backups')
PORT = int(os.environ.get('PORT', 8081))

os.makedirs(BACKUP_DIR, exist_ok=True)


class BackupHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message, status=400):
        self._send_json({'error': message}, status=status)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/api/backups':
            backups = []
            if os.path.exists(BACKUP_DIR):
                for fname in sorted(os.listdir(BACKUP_DIR), reverse=True):
                    if fname.endswith('.json'):
                        fpath = os.path.join(BACKUP_DIR, fname)
                        try:
                            stat = os.stat(fpath)
                            with open(fpath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Extract summary info
                            chapters = (data.get('save', {}) or data).get('chapters', {})
                            active_chapters = [k for k, v in chapters.items() if v.get('sectionsList')]
                            
                            backups.append({
                                'filename': fname,
                                'size': stat.st_size,
                                'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'activeChapters': active_chapters,
                            })
                        except Exception as e:
                            backups.append({
                                'filename': fname,
                                'size': 0,
                                'mtime': '',
                                'error': str(e),
                            })
            self._send_json({'backups': backups})
        else:
            self._send_error('Not found', status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(length) if length > 0 else b'{}'
        try:
            body = json.loads(raw_body.decode('utf-8'))
        except Exception:
            self._send_error('Invalid JSON body')
            return

        if path == '/api/backups':
            # Create a new server backup snapshot
            name_input = body.get('name', '').strip()
            name_sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name_input) if name_input else ''
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if name_sanitized:
                fname = f"oathsworn_{name_sanitized}_{timestamp}.json"
            else:
                fname = f"oathsworn_backup_{timestamp}.json"

            fpath = os.path.join(BACKUP_DIR, fname)
            
            payload = {
                'timestamp': datetime.now().isoformat(),
                'version': 1,
                'save': body.get('save', {}),
                'settings': body.get('settings', {}),
            }

            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)

            self._send_json({'success': True, 'filename': fname, 'message': 'Backup created successfully'})

        elif path == '/api/backups/restore':
            filename = body.get('filename', '')
            if not filename or '/' in filename or '\\' in filename:
                self._send_error('Invalid filename')
                return

            fpath = os.path.join(BACKUP_DIR, filename)
            if not os.path.isfile(fpath):
                self._send_error('Backup file not found', status=404)
                return

            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._send_json({'success': True, 'data': data})
        else:
            self._send_error('Not found', status=404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        # Expect /api/backups/<filename>
        parts = path.split('/')
        if len(parts) == 4 and parts[1] == 'api' and parts[2] == 'backups':
            filename = unquote(parts[3])
            if not filename or '/' in filename or '\\' in filename:
                self._send_error('Invalid filename')
                return

            fpath = os.path.join(BACKUP_DIR, filename)
            if os.path.isfile(fpath):
                os.remove(fpath)
                self._send_json({'success': True, 'message': f'Deleted {filename}'})
            else:
                self._send_error('File not found', status=404)
        else:
            self._send_error('Not found', status=404)


def run():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, BackupHandler)
    print(f"Backup server listening on port {PORT}, storing in {BACKUP_DIR}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    run()
