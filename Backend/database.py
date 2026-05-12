import sqlite3

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to database: {db_file}")
    except sqlite3.Error as e:
        print(e)

    return conn

def create_table(conn):
    try:
        sql_create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_users_table)
        print("Users table created successfully.")
    except sqlite3.Error as e:
        print("Failed to create users table.")
        print(e)
    
def insert_user(conn, username, email, password):
    try:
        sql = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)"
        cursor = conn.cursor()
        cursor.execute(sql, (username, email, password))
        conn.commit()
        print("User inserted successfully.")
    except sqlite3.Error as e:
        print("Failed to insert user.")
        print(e)

def user_exists(conn, username, password):
    try:
        sql = "SELECT id FROM users WHERE username = ? AND password = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (username, password))
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        print("Failed to check if user exists.")
        print(e)
        return False

if __name__ == "__main__":
    database = "Enteka.db"
    conn = create_connection(database)
    create_table(conn)

    if conn is not None:
        create_table(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")
    