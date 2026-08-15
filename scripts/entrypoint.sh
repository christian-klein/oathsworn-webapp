#!/bin/sh
set -e

# Start backup server daemon in the background
python3 /opt/backup_server.py &

# Start Caddy web server in foreground
exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
