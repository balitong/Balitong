import sqlite3

class Database:
    def __init__(self, db_url):
        self.connection = sqlite3.connect(db_url)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        # Create necessary tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS trades (
                                id INTEGER PRIMARY KEY,
                                action TEXT,
                                amount REAL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                              )''')
        self.connection.commit()

    def insert_trade(self, action, amount):
        # Insert a trade record
        self.cursor.execute('INSERT INTO trades (action, amount) VALUES (?, ?)', (action, amount))
        self.connection.commit()
