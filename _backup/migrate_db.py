"""
Database migration script to add account_mode column
"""
import sqlite3
import sys
from pathlib import Path
from config import DATA_DIR

def migrate_database():
    """Add account_mode column to existing database"""
    db_path = DATA_DIR / 'trade_copier.db'
    
    if not db_path.exists():
        print("Database not found. Creating new database...")
        # Import to create new database with updated schema
        from database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("New database created with updated schema.")
        return
    
    print(f"Migrating database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'account_mode' not in columns:
            print("Adding account_mode column...")
            cursor.execute("ALTER TABLE accounts ADD COLUMN account_mode VARCHAR DEFAULT 'spot'")
            conn.commit()
            print("Successfully added account_mode column")
        else:
            print("account_mode column already exists")
        
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()
