"""
Database migration script to add new columns and tables.
Run this once to update your existing database schema.
"""

import sqlite3
import os

DB_PATH = "bill_tracker.db"

def migrate_database():
    """Add missing columns and tables to existing database."""

    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. No migration needed - will create fresh on startup.")
        return

    print(f"Migrating database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if store_name column exists in bills table
        cursor.execute("PRAGMA table_info(bills)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'store_name' not in columns:
            print("Adding store_name column to bills table...")
            cursor.execute("ALTER TABLE bills ADD COLUMN store_name VARCHAR")
            print("✓ Added store_name column")
        else:
            print("✓ store_name column already exists")

        # Check if item_id column exists in bill_items table
        cursor.execute("PRAGMA table_info(bill_items)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'item_id' not in columns:
            print("Adding item_id column to bill_items table...")
            cursor.execute("ALTER TABLE bill_items ADD COLUMN item_id INTEGER REFERENCES items(id) ON DELETE SET NULL")
            print("✓ Added item_id column")
        else:
            print("✓ item_id column already exists")

        # Create items table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                subcategory_id INTEGER NOT NULL REFERENCES subcategories(id) ON DELETE CASCADE,
                description VARCHAR,
                created_at DATETIME NOT NULL
            )
        """)
        print("✓ Items table ready")

        # Create item_keywords table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_keywords (
                id INTEGER PRIMARY KEY,
                item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                keyword VARCHAR NOT NULL,
                created_at DATETIME NOT NULL
            )
        """)
        print("✓ Item keywords table ready")

        conn.commit()
        print("\n✅ Database migration completed successfully!")
        print("You can now restart the backend server.")

    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
