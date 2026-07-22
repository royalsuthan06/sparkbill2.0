import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'arun_crackers_pos')

print(f"Testing connection to {DB_USER}@{DB_HOST}...")
try:
    # First, try connecting without database to check credentials
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("✓ Success! Credentials are correct!")
    
    # Check if database exists
    with connection.cursor() as cursor:
        cursor.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
        result = cursor.fetchone()
        if result:
            print(f"✓ Database '{DB_NAME}' exists!")
        else:
            print(f"✗ Database '{DB_NAME}' does NOT exist! Please create it first!")
    connection.close()
except pymysql.Error as e:
    print(f"✗ Error connecting to MySQL: {e}")
    print("\nPlease check:")
    print("1. MySQL server is running")
    print("2. DB_USER and DB_PASSWORD are correct in .env file")
    print("3. Your user has access to MySQL")
