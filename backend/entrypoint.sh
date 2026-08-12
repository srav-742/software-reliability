#!/bin/sh
set -e

echo "Waiting for database connection..."
python -c "
import time, os, psycopg2
db_url = os.environ.get('DATABASE_URL', '')
if '@' in db_url:
    parts = db_url.split('@', 1)
    prefix, rest = parts[0], parts[1]
    host_end = len(rest)
    for char in [':', '/']:
        idx = rest.find(char)
        if idx != -1 and idx < host_end:
            host_end = idx
    host = rest[:host_end]
    if ' ' in host:
        host = host.replace(' ', '-')
    
    db_url = f"{prefix}@{host}{rest[host_end:]}"
    if host.endswith('.render.com') and 'sslmode=' not in db_url:
        if '?' in db_url:
            db_url += '&sslmode=require'
        else:
            db_url += '?sslmode=require'

if db_url.startswith('sqlite'):
    print('SQLite database detected, skipping PostgreSQL connection check.')
    exit(0)

if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

if db_url.startswith('postgresql+psycopg2://'):
    db_url = db_url.replace('postgresql+psycopg2://', 'postgresql://', 1)

if not db_url.startswith('postgresql://'):
    print('Non-PostgreSQL URL detected, skipping PostgreSQL wait check.')
    exit(0)

is_render = os.environ.get('RENDER') == 'true' or os.environ.get('RENDER') is not None
is_external_render_db = '.render.com' in db_url

if is_render and is_external_render_db:
    print('=' * 80)
    print('WARNING: You are using the EXTERNAL Database URL (containing \'.render.com\') inside a Render environment.')
    print('Render PostgreSQL databases block external connections by default via Access Control lists (firewall).')
    print('To fix this, update your DATABASE_URL environment variable in your Render service settings to the INTERNAL Database URL.')
    print('The Internal Database URL is faster, free, and does not require IP allow-listing.')
    print('=' * 80)

connect_args = {}
if 'sslmode=' not in db_url and is_external_render_db:
    connect_args['sslmode'] = 'require'

for i in range(30):
    try:
        conn = psycopg2.connect(db_url, **connect_args)
        conn.close()
        print('Database connection established!')
        break
    except Exception as e:
        print(f'Waiting for Postgres... ({e})')
        time.sleep(2)
else:
    print('Failed to connect to database in time.')
    exit(1)
"

echo "Running Alembic database migrations..."
alembic upgrade head

echo "Starting Uvicorn web server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
