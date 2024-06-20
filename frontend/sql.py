import sqlite3

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("./db.sqlite3", isolation_level=None)
    except sqlite3.Error as e:
        print(e)
    
    return conn

def create_table():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Recordings (recording_id INTEGER PRIMARY KEY, recording_path TEXT)")
        conn.close()
    except sqlite3.Error as e:
        print(e)
        
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Events (event_id INTEGER PRIMARY KEY, face_path TEXT, entered_at TEXT, exited_at TEXT)")
        conn.close()
    except sqlite3.Error as e:
        print(e)
        
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Event_recordings (recording_id INTEGER PRIMARY KEY, event_id INTEGER, recording_path TEXT)")
        conn.close()
    except sqlite3.Error as e:
        print(e)
        
        
def truncate_table():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Recordings")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)
        
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Events")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)
        
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Event_recordings")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)
        
def view_table():      
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Events;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        conn.close()
    except sqlite3.Error as e:
        print(e)
        
def add_url(url):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO URL (url, date) VALUES (?, datetime('now'))", (url,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


# truncate_table()
# view_table()