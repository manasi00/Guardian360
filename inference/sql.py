import sqlite3
import datetime as dt

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
        
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS URL (url_id INTEGER PRIMARY KEY, url TEXT, date TEXT)")
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
        
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM URL")
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
        
def face_in(imag_filename):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Events (face_path, entered_at, exited_at) VALUES (?,?,?)", (imag_filename, dt.datetime.now(), None))
        try:
            conn.commit()
            print('Data added to database')
        except sqlite3.Error as e:
            print(e)
        conn.close()
        
    except sqlite3.Error as e:
        print(e)

def face_out(imag_filename):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Events SET exited_at = ? WHERE face_path = ? AND exited_at IS NULL", (dt.datetime.now(), imag_filename))
        try:
            conn.commit()
            print('Data added to database')
        except sqlite3.Error as e:
            print(e)
        conn.close()
        
    except sqlite3.Error as e:
        print(e)

def get_url():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM url ORDER BY url_id DESC;")
        rows = cursor.fetchall()
        conn.close()
        if rows:
            return rows[0][1]
        else:
            return None
    except sqlite3.Error as e:
        print(e)

create_table()
# truncate_table()