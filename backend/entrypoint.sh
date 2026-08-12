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
    
    if os.environ.get('RENDER') == 'true' and host.endswith('.render.com'):
        host = host.split('.')[0]
        db_url = f"{prefix}@{host}{rest[host_end:]}"
    else:
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

for i in range(30):
    try:
        conn = psycopg2.connect(db_url)
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
