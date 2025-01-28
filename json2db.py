import sqlite3
import json

def json2db(json_path, db_path):
    # Load JSON data
    with open(json_path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables with integer primary key for quotes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        author TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote_id INTEGER NOT NULL,
        interpretation TEXT NOT NULL,
        FOREIGN KEY (quote_id) REFERENCES quotes (id)
    )
    ''')

    # Create indexes for faster SELECT queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_author ON quotes (author)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quote_id ON interpretations (quote_id)')

    # Insert data into tables
    for content in data.values():
        # Insert into quotes table and get the auto-incremented ID
        cursor.execute('''
        INSERT INTO quotes (text, author) VALUES (?, ?)
        ''', (content['text'], content['author']))
        quote_id = cursor.lastrowid  # Get the integer ID of the inserted row

        # Insert interpretations
        for interpretation in content.get('interpretations', []):
            cursor.execute('''
            INSERT INTO interpretations (quote_id, interpretation) VALUES (?, ?)
            ''', (quote_id, interpretation))

    # Commit and close
    conn.commit()
    conn.close()

    print("Database has been successfully created, populated, and indexed!")