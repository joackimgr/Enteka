import sqlite3
import uuid
import hashlib
import logging
from security.encryption import encrypt, decrypt

logger = logging.getLogger("enteka.database")

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        logger.info("Connected to database: %s", db_file)
    except sqlite3.Error as e:
        logger.error(e)

    return conn

def create_table(conn):
    try:
        sql_create_tables = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            profile_picture TEXT
        );

        CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL,
        user2_id INTEGER NOT NULL,
        passkey_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user1_id) REFERENCES users(id),
        FOREIGN KEY (user2_id) REFERENCES users(id),
        UNIQUE(user1_id, user2_id)
        );
        
        CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        image TEXT,
        timestamp TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (chat_id) REFERENCES chats(id),
        FOREIGN KEY (sender_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_id INTEGER NOT NULL,
        to_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (from_id) REFERENCES users(id),
        FOREIGN KEY (to_id) REFERENCES users(id),
        UNIQUE(from_id, to_id)
        );
        """
        cursor = conn.cursor()
        cursor.executescript(sql_create_tables)
        columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
        if "profile_picture" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
            conn.commit()
            logger.info("Added 'profile_picture' column to users table.")
        logger.info("Tables created successfully.")
    except sqlite3.Error as e:
        logger.error("Failed to create tables.")
        logger.error(e)
    
def insert_user(conn, username, email, password):
    try:
        sql = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)"
        cursor = conn.cursor()
        cursor.execute(sql, (username, email, password))
        conn.commit()
        logger.info("User '%s' inserted successfully.", username)
        return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error("Failed to insert user.")
        logger.error(e)
        return None

def get_user_hash(conn, username):
    try:
        sql = "SELECT password FROM users WHERE username = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    
    except sqlite3.Error as e:
        logger.error("Failed to get user hash.")
        logger.error(e)
        return None

def get_user_hash_by_id(conn, user_id):
    try:
        sql = "SELECT password FROM users WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except sqlite3.Error as e:
        logger.error("Failed to get user hash by id.")
        logger.error(e)
        return None
    
def search_users(conn, query):
        try:
            sql = "SELECT id, username FROM users WHERE username LIKE ?"
            cursor = conn.cursor()
            cursor.execute(sql, (f"{query}%",))
            result = cursor.fetchall()
            return [{"id": row[0], "username": row[1]} for row in result]
        except sqlite3.Error as e:
            logger.error("Failed to search user.")
            logger.error(e)
            return None

def create_chat(conn, user1_id, user2_id):
    if user2_id < user1_id:
        user1_id, user2_id = user2_id, user1_id
    try:
        raw = str(uuid.uuid4())
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        sql = """INSERT INTO chats (user1_id, user2_id, passkey_hash) VALUES (?, ?, ?)"""
        cursor = conn.cursor()
        cursor.execute(sql, (user1_id, user2_id, hashed))
        conn.commit()
        return { "chat_id": cursor.lastrowid, "passkey_hash": hashed }
        
    except sqlite3.IntegrityError:
        cursor = conn.cursor()
        cursor.execute("SELECT id, passkey_hash FROM chats WHERE user1_id = ? AND user2_id = ?", (user1_id, user2_id))
        result = cursor.fetchone()
        if result:
            return { "chat_id": result[0], "passkey_hash": result[1] }
        return None
    except sqlite3.Error as e:
        logger.error("Failed to create chat.")
        logger.error(e)
        return None

def get_chat_passkey_hash(conn, chat_id):
    try:
        sql = "SELECT passkey_hash FROM chats WHERE id = ?" 
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, ))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    
    except sqlite3.Error as e:
        logger.error("Failed to get passkey hash.")
        logger.error(e)
        return None

def get_user_by_username(conn, username):
    try:
        sql = "SELECT id FROM users WHERE username = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (username, ))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    
    except sqlite3.Error as e:
        logger.error("Failed to find user by username.")
        logger.error(e)
        return None
    
def get_user_by_id(conn, id):
    try:
        sql = "SELECT username FROM users WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (id, ))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except sqlite3.Error as e:
        logger.error("Failed to find user by id.")
        logger.error(e)
        return None
    
def insert_message(conn, chat_id, sender_id, message, image=None):
    try:
        sql = "INSERT INTO messages (chat_id, sender_id, content, image) VALUES (?, ?, ?, ?)"
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, sender_id, encrypt(message), image))
        result = cursor.lastrowid
        conn.commit()
        if result:
            return result
        return None
    
    except sqlite3.Error as e:
        logger.error("Failed to send message.")
        logger.error(e)
        return None
    
def get_messages_by_chat_id(conn, chat_id):
    try:
        sql = """SELECT id, sender_id, content, image, timestamp
        FROM messages 
        WHERE chat_id = ? 
        ORDER BY timestamp ASC
        """
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, ))
        result = cursor.fetchall()
        if result:
            return [(row[0], row[1], decrypt(row[2]), row[3], row[4]) for row in result]
        return None
    
    except sqlite3.Error as e:
        logger.error("Failed to get messages.")
        logger.error(e)
        return None
    
def get_last_message_by_chat_id(conn, chat_id):
    try:
        sql = "SELECT content, image, timestamp FROM messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 1"    
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, ))
        result = cursor.fetchone()
        if result:
            return (decrypt(result[0]), result[1], result[2])
        return None
    except sqlite3.Error as e:
        logger.error("Failed to get last message.")
        logger.error(e)
        return None
    
def get_chats_by_user_id(conn, user_id):
    try:
        sql = """SELECT id, user1_id, user2_id, passkey_hash, created_at 
        FROM chats 
        WHERE user1_id = ? 
        OR user2_id = ? 
        ORDER BY created_at DESC
        """
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, user_id))
        result = cursor.fetchall()
        if result:
            return result
        return None
    
    except sqlite3.Error as e:
        logger.error("Failed to get chats.")
        logger.error(e)
        return None

def get_user_suggestions(conn, caller_id, limit = 10):
    try:
        sql = """SELECT id, username 
        FROM users 
        WHERE id != ? 
        ORDER BY RANDOM() 
        LIMIT ?
        """
        cursor =  conn.cursor()
        cursor.execute(sql, (caller_id, limit))
        result = cursor.fetchall()
        return [{"id": row[0], "username": row[1]} for row in result]
    except sqlite3.Error as e:
        logger.error("Failed to get user suggestions.")
        logger.error(e)
        return None
    
def send_friend_request(conn, from_id, to_id):
    if from_id == to_id:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM friends WHERE (from_id = ? AND to_id = ?) OR (from_id = ? AND to_id = ?)",
            (from_id, to_id, to_id, from_id)
        )
        if cursor.fetchone():
            return None
        sql = "INSERT INTO friends (from_id, to_id, status) VALUES (?, ?, 'pending')"
        cursor.execute(sql, (from_id, to_id))
        conn.commit()
        return {"id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return None
    except sqlite3.Error as e:
        logger.error(e)
        return None

def accept_friend_request(conn, request_id, user_id):
    try:
        sql = "UPDATE friends SET status = 'accepted' WHERE id = ? AND status = 'pending' AND to_id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (request_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(e)
        return None

def reject_friend_request(conn, request_id, user_id):
    try:
        sql = "UPDATE friends SET status = 'rejected' WHERE id = ? AND status = 'pending' AND to_id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (request_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(e)
        return None

def get_pending_requests(conn, user_id):
    try:
        sql = """SELECT f.id, f.from_id, u.username, f.created_at
        FROM friends f
        JOIN users u ON f.from_id = u.id
        WHERE f.to_id = ? AND f.status = 'pending'
        ORDER BY f.created_at DESC
        """
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        if result:
            return [{"id": row[0], "from_id": row[1], "username": row[2], "created_at": row[3]} for row in result]
        return []
    except sqlite3.Error as e:
        logger.error(e)
        return None

def get_friends(conn, user_id):
    try:
        sql = """SELECT f.id,
        CASE WHEN f.from_id = ? THEN f.to_id ELSE f.from_id END AS friend_id,
        CASE WHEN f.from_id = ? THEN u2.username ELSE u1.username END AS username
        FROM friends f
        JOIN users u1 ON f.from_id = u1.id
        JOIN users u2 ON f.to_id = u2.id
        WHERE (f.from_id = ? OR f.to_id = ?) AND f.status = 'accepted'
        ORDER BY f.created_at DESC
        """
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, user_id, user_id, user_id))
        result = cursor.fetchall()
        if result:
            return [{"id": row[0], "friend_id": row[1], "username": row[2]} for row in result]
        return []
    except sqlite3.Error as e:
        logger.error(e)
        return None

def remove_friend(conn, user_id, friend_id):
    try:
        sql = """DELETE FROM friends
        WHERE ((from_id = ? AND to_id = ?) OR (from_id = ? AND to_id = ?))
        AND status = 'accepted'
        """
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, friend_id, friend_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(e)
        return None
    
def search_friends(conn, user_id, query):
    try:
        sql = """SELECT DISTINCT u.id, u.username
        FROM users u
        JOIN friends f ON (u.id = f.from_id OR u.id = f.to_id)
        WHERE (f.from_id = ? OR f.to_id = ?)
        AND f.status = 'accepted'
        AND u.id != ?
        AND u.username LIKE ?
        """
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, user_id, user_id, f"{query}%"))
        result = cursor.fetchall()
        return [{"id": row[0], "username": row[1]} for row in result]
    except sqlite3.Error as e:
        logger.error(e)
        return None

def chat_belongs_to_user(conn, chat_id, user_id):
    try:
        sql = "SELECT id FROM chats WHERE id = ? AND (user1_id = ? OR user2_id = ?)"
        cursor = conn.cursor()
        cursor.execute(sql, (chat_id, user_id, user_id))
        result = cursor.fetchall()
        return bool(result)
    except sqlite3.Error as e:
        logger.error(e)
        return None

def get_user_profile(conn, user_id):
    try:
        sql = "SELECT id, username, email, profile_picture FROM users WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result:
            return {"id": result[0], "username": result[1], "email": result[2], "profile_picture": result[3]}
        return None
    except sqlite3.Error as e:
        logger.error(e)
        return None

def update_username(conn, user_id, new_username):
    try:
        sql = "UPDATE users SET username = ? WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (new_username, user_id))
        conn.commit()
        return new_username
    except sqlite3.IntegrityError:
        logger.error("Username '%s' is already taken.", new_username)
        return None
    except sqlite3.Error as e:
        logger.error(e)
        return None

def update_email(conn, user_id, new_email):
    try:
        sql = "UPDATE users SET email = ? WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (new_email, user_id))
        conn.commit()
        return new_email
    except sqlite3.IntegrityError:
        logger.error("Email '%s' is already taken.", new_email)
        return None
    except sqlite3.Error as e:
        logger.error(e)
        return None

def update_password(conn, user_id, new_hash):
    try:
        sql = "UPDATE users SET password = ? WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (new_hash, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(e)
        return None

def update_profile_picture(conn, user_id, image_url):
    try:
        sql = "UPDATE users SET profile_picture = ? WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (image_url, user_id))
        conn.commit()
        return image_url
    except sqlite3.Error as e:
        logger.error(e)
        return None
    
if __name__ == "__main__":
    database = "Enteka.db"
    conn = create_connection(database)
    create_table(conn)

    if conn is not None:
        conn.close()
    else:
        print("Error! Cannot create the database connection.")