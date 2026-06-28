"""
Database Migration Script
Adds the missing category_id column to the channel table
"""

import sqlite3

# Connect to the database
conn = sqlite3.connect('discord.db')
cursor = conn.cursor()

# Add the category_id column to the channel table
try:
    cursor.execute("ALTER TABLE channel ADD COLUMN category_id INTEGER REFERENCES category(id);")
    print("Successfully added category_id column to channel table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column category_id already exists in channel table")
    else:
        print(f"Error adding column: {e}")

# Commit changes and close connection
conn.commit()
conn.close()

print("Migration completed!")