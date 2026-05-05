import sqlite3

def initialize_database():
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()

    # Optional: cursor.execute("DROP TABLE IF EXISTS bookings") # Use this to reset during dev

    # 1. Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # 2. Resources
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            capacity INTEGER,
            location TEXT
        )
    ''')

    # 3. Equipment
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            assigned_room TEXT,
            status TEXT DEFAULT 'Available'
        )
    ''')

    # 4. Bookings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            room_id INTEGER,
            username TEXT,
            date TEXT,
            time_slot TEXT,
            purpose TEXT,
            FOREIGN KEY (room_id) REFERENCES resources (resource_id)
        )
    ''')
    
    # 5. Create Notices Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        date TEXT NOT NULL
    )
''')
    
    # SQL to create the logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        action TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
    conn.commit()
    conn.close()
    print("✅ Database is ready and synchronized with the Dashboard!")

if __name__ == "__main__":
    initialize_database()