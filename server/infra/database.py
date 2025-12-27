import sqlite3
import logging
from typing import Optional
from protocol.enums import Role

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "sweat.db"):
        self._db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                # Create players table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL
                    )
                """)
                # Create developers table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS developers (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL
                    )
                """)
                # Create games table (placeholder for now)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS games (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        developer TEXT NOT NULL,
                        FOREIGN KEY(developer) REFERENCES users(username)
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.exception("Failed to initialize database: %s", e)
            raise

    def get_player(self, username: str) -> Optional[tuple[str, str]]:
        """Retrieve a player by username. Returns (username, password) or None."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, password FROM players WHERE username = ?", (username,))
                return cursor.fetchone()
        except Exception as e:
            logger.error("Error getting player %s: %s", username, e)
            return None
        
    def create_player(self, username: str, password: str) -> bool:
        """Create a new player. Returns True if successful, False if username exists."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO players (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            logger.error("Error creating player %s: %s", username, e)
            return False
        
    def get_developer(self, username: str) -> Optional[tuple[str, str]]:
        """Retrieve a developer by username. Returns (username, password) or None."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, password FROM developers WHERE username = ?", (username,))
                return cursor.fetchone()
        except Exception as e:
            logger.error("Error getting developer %s: %s", username, e)
            return None
        
    def create_developer(self, username: str, password: str) -> bool:
        """Create a new developer. Returns True if successful, False if username exists."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO developers (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            logger.error("Error creating developer %s: %s", username, e)
            return False

    # def get_user(self, username: str) -> Optional[tuple[str, str, str]]:
    #     """Retrieve a user by username. Returns (username, password, role) or None."""
    #     try:
    #         with sqlite3.connect(self._db_path) as conn:
    #             cursor = conn.cursor()
    #             cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    #             return cursor.fetchone()
    #     except Exception as e:
    #         logger.error("Error getting user %s: %s", username, e)
    #         return None

    # def create_user(self, username: str, password: str, role: str) -> bool:
    #     """Create a new user. Returns True if successful, False if username exists."""
    #     try:
    #         with sqlite3.connect(self._db_path) as conn:
    #             cursor = conn.cursor()
    #             cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    #             conn.commit()
    #             return True
    #     except sqlite3.IntegrityError:
    #         return False
    #     except Exception as e:
    #         logger.error("Error creating user %s: %s", username, e)
    #         return False
