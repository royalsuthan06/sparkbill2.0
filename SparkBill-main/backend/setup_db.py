import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'arun_crackers_pos')

print("=" * 50)
print("Arun Crackers POS - Database Setup")
print("=" * 50)

try:
    # Step 1: Connect to MySQL server (without database)
    print(f"\n1. Connecting to MySQL server at {DB_HOST}...")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("✓ Connected to MySQL server successfully!")

    # Step 2: Create database if it doesn't exist
    print(f"\n2. Creating database '{DB_NAME}' (if not exists)...")
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    connection.commit()
    print(f"✓ Database '{DB_NAME}' is ready!")

    # Step 3: Now let's connect to the database and import the schema
    print(f"\n3. Importing schema and sample data...")
    connection.select_db(DB_NAME)

    # Read the schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split into individual statements (simplified, works for our schema)
    statements = []
    current_statement = []
    for line in sql_content.split('\n'):
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith('--'):
            current_statement.append(line)
            if stripped_line.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []

    # Execute each statement
    with connection.cursor() as cursor:
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
    connection.commit()
    print("✓ Schema and sample data imported successfully!")

    print("\n" + "=" * 50)
    print("✅ Database setup complete! You can now run the app!")
    print("=" * 50)

except pymysql.Error as e:
    print(f"\n✗ Error: {e}")
    print("\nPlease check:")
    print("- MySQL server is running")
    print("- DB_USER and DB_PASSWORD in .env are correct")
    print("- Your user has privileges to create databases")
finally:
    if 'connection' in locals() and connection:
        connection.close()
