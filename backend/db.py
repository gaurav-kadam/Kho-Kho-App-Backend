import psycopg2
from dotenv import load_dotenv
import os

# ==============================
# Load environment variables
# ==============================
load_dotenv()

# Fetch variables (MATCH Django settings)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# ==============================
# Django DATABASE CONFIG (for reference)
# ==============================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "sslmode": "require",  # REQUIRED for Supabase
        },
    }
}

# ==============================
# Direct psycopg2 Connection
# ==============================
try:
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"  # VERY IMPORTANT for Supabase
    )

    print("✅ Connection successful!")

    cursor = connection.cursor()

    # Test query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("🕒 Current Time:", result[0])

    cursor.close()
    connection.close()

    print("✅ Connection closed.")

except Exception as e:
    print(f"❌ Failed to connect: {e}")