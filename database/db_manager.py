import sqlite3

# --- USER AUTHENTICATION ---
def verify_user(username, password):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_user(username, password, role):
    try:
        conn = sqlite3.connect('smart_campus.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# --- RESOURCE / ROOM MANAGEMENT ---
def fetch_all_resources():
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources")
    data = cursor.fetchall()
    conn.close()
    return data

def add_resource(name, r_type, capacity, location):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO resources (name, type, capacity, location) VALUES (?, ?, ?, ?)",
                   (name, r_type, capacity, location))
    conn.commit()
    conn.close()

def delete_resource(resource_id):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resources WHERE resource_id = ?", (resource_id,))
    conn.commit()
    conn.close()

def search_resources(query):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    sql = "SELECT * FROM resources WHERE name LIKE ? OR type LIKE ?"
    cursor.execute(sql, (f'%{query}%', f'%{query}%'))
    data = cursor.fetchall()
    conn.close()
    return data

# --- EQUIPMENT MANAGEMENT ---
def fetch_all_equipment():
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment")
    data = cursor.fetchall()
    conn.close()
    return data

def add_equipment(name, qty, room):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO equipment (item_name, quantity, assigned_room) VALUES (?, ?, ?)",
                   (name, qty, room))
    conn.commit()
    conn.close()

# --- BOOKING ENGINE ---
def is_room_available(room_id, date, time_slot):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    query = "SELECT * FROM bookings WHERE room_id = ? AND date = ? AND time_slot = ?"
    cursor.execute(query, (room_id, date, time_slot))
    result = cursor.fetchone()
    conn.close()
    return result is None

def save_booking(room_id, username, date, time_slot, purpose):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings (room_id, username, date, time_slot, purpose) VALUES (?, ?, ?, ?, ?)",
                   (room_id, username, date, time_slot, purpose))
    conn.commit()
    conn.close()

def delete_booking(booking_id):
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()


def delete_equipment(item_id):
    """Removes equipment from the database using its unique ID."""
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipment WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()

def fetch_notices():
    conn = sqlite3.connect('smart_campus.db')
    data = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    conn.close()
    return data

def add_notice(title, content, date):
    conn = sqlite3.connect('smart_campus.db')
    conn.execute("INSERT INTO notices (title, content, date) VALUES (?, ?, ?)", (title, content, date))
    conn.commit()
    conn.close()

def get_analytics_data():
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    
    # Data for Room Usage (Bar Chart)
    room_usage = cursor.execute('''
        SELECT r.name, COUNT(b.id) 
        FROM resources r 
        LEFT JOIN bookings b ON r.resource_id = b.room_id 
        GROUP BY r.name
    ''').fetchall()

    # Data for Equipment Status (Pie Chart)
    eq_status = cursor.execute('''
        SELECT status, COUNT(item_id) 
        FROM equipment 
        GROUP BY status
    ''').fetchall()
    
    conn.close()
    return room_usage, eq_status

def add_log(user, action):
    """Call this whenever an action is performed."""
    conn = sqlite3.connect('smart_campus.db')
    conn.execute("INSERT INTO logs (user, action) VALUES (?, ?)", (user, action))
    conn.commit()
    conn.close()

def fetch_logs():
    """Retrieves the last 50 actions."""
    conn = sqlite3.connect('smart_campus.db')
    data = conn.execute("SELECT user, action, timestamp FROM logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return data

def initialize_db():
    conn = sqlite3.connect('smart_campus.db')
    cursor = conn.cursor()
    
    # Create Logs Table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user TEXT, action TEXT, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create Notices Table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS notices 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      title TEXT, content TEXT, date TEXT)''')
    
    conn.commit()
    conn.close()
