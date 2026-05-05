import sqlite3
from database.db_manager import add_user

def populate_database():
    try:
        conn = sqlite3.connect('smart_campus.db')
        cursor = conn.cursor()

        print("Cleaning up old data...")
        # Clear existing data to prevent duplicates
        cursor.execute("DELETE FROM resources")
        cursor.execute("DELETE FROM equipment")
        cursor.execute("DELETE FROM users") # Careful: this removes all users

        # 1. Add Rooms and Labs
        campus_resources = [
            ('Classroom 101', 'Classroom', 30, 'North Wing'),
            ('Classroom 102', 'Classroom', 35, 'North Wing'),
            ('Lecture Hall A', 'Lecture Hall', 120, 'Main Building'),
            ('Computer Lab 1', 'Lab', 25, 'IT Block'),
            ('Computer Lab 2', 'Lab', 25, 'IT Block'),
            ('Physics Lab', 'Lab', 20, 'Science Block'),
            ('Chemistry Lab', 'Lab', 20, 'Science Block'),
            ('Seminar Room', 'Seminar Room', 15, 'Library 2nd Floor'),
            ('Main Auditorium', 'Hall', 500, 'Administration Block')
        ]
        cursor.executemany(
            "INSERT INTO resources (name, type, capacity, location) VALUES (?, ?, ?, ?)", 
            campus_resources
        )

        # 2. Add Equipment
        equipment_list = [
            ('Projector', 5, 'Main Store'),
            ('Laptop', 10, 'IT Office'),
            ('Microscope', 15, 'Science Lab')
        ]
        cursor.executemany(
            "INSERT INTO equipment (item_name, quantity, assigned_room) VALUES (?, ?, ?)",
            equipment_list
        )

        conn.commit()
        conn.close()
        
        # 3. Add Default Users (using your db_manager function)
        add_user("admin", "admin123", "Admin")
        add_user("teacher1", "pass123", "Teacher")
        add_user("student1", "pass123", "Student")

        
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")
        print("Make sure you have run your db_setup.py script first to create the tables!")

if __name__ == "__main__":
    populate_database()