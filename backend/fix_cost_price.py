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
print("Fixing cost_price column...")
print("=" * 50)

try:
    # Connect to MySQL
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print("✅ Connected to database successfully!")

    # Check if column exists
    cursor = connection.cursor()
    cursor.execute("SHOW COLUMNS FROM products LIKE 'cost_price'")
    result = cursor.fetchone()

    if result:
        print("✅ cost_price column already exists!")
    else:
        print("ℹ️ Adding cost_price column...")
        alter_sql = """
        ALTER TABLE products 
        ADD COLUMN cost_price DECIMAL(10,2) NOT NULL DEFAULT 0 
        AFTER price
        """
        cursor.execute(alter_sql)
        connection.commit()
        print("✅ cost_price column added successfully!")

    cursor.close()
    connection.close()
    print("\n🎉 Done!")

except pymysql.Error as e:
    print(f"\n❌ Error: {e}")
