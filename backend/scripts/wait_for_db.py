import sys
import time
import psycopg2
import os

# Add the parent directory to sys.path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings

def wait_for_db():
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        print("SQLite detected, skipping wait.")
        return

    # Replace postgresql+psycopg2 with postgresql or postgres for psycopg2 compatibility
    conn_url = db_url
    if conn_url.startswith("postgresql+psycopg2://"):
        conn_url = conn_url.replace("postgresql+psycopg2://", "postgresql://", 1)
    elif conn_url.startswith("postgres://"):
        conn_url = conn_url.replace("postgres://", "postgresql://", 1)

    # Detect if we are on Render and using an external URL
    is_render = os.environ.get("RENDER") == "true" or os.environ.get("RENDER") is not None
    is_external_render_db = ".render.com" in conn_url

    if is_render and is_external_render_db:
        print("=" * 80)
        print("WARNING: You are using the EXTERNAL Database URL (containing '.render.com') inside a Render environment.")
        print("Render PostgreSQL databases block external connections by default via Access Control lists (firewall).")
        print("To fix this, update your DATABASE_URL environment variable in your Render service settings to the INTERNAL Database URL.")
        print("The Internal Database URL is faster, free, and does not require IP allow-listing.")
        print("=" * 80)

    # Setup connection args, explicitly forcing sslmode if connecting to a Render DB externally
    connect_args = {}
    if "sslmode=" not in conn_url and is_external_render_db:
        connect_args["sslmode"] = "require"

    print("Checking database connection...")
    for i in range(30):
        try:
            conn = psycopg2.connect(conn_url, **connect_args)
            conn.close()
            print("Database connection established!")
            return
        except Exception as e:
            print(f"Waiting for Postgres... Attempt {i+1}/30 ({e})")
            time.sleep(3)
    
    print("Database connection failed. Exiting.")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()
