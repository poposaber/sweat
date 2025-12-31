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
                # Create games table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS games (
                        name TEXT PRIMARY KEY,
                        developer TEXT NOT NULL, 
                        version TEXT NOT NULL,
                        min_players INTEGER NOT NULL,
                        max_players INTEGER NOT NULL,
                        sha256 TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        FOREIGN KEY(developer) REFERENCES developers(username)
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
        
    def create_game(self, name: str, developer: str, version: str, min_players: int, max_players: int, sha256: str, file_path: str) -> bool:
        """Create a new game. Returns True if successful, False if game name exists."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO games (name, developer, version, min_players, max_players, sha256, file_path) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, developer, version, min_players, max_players, sha256, file_path))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            logger.error("Error creating game %s: %s", name, e)
            return False
        
    def get_game(self, name: str) -> Optional[tuple[str, str, str, int, int, str, str]]:
        """Retrieve a game by name. Returns (name, developer, version, min_players, max_players, sha256, file_path) or None."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, developer, version, min_players, max_players, sha256, file_path FROM games WHERE name = ?", (name,))
                row = cursor.fetchone()
                if row is None:
                    logger.info("Game %s not found", name)
                return row
        except Exception as e:
            logger.error("Error getting game %s: %s", name, e)
            return None
        
    def get_games_by_developer(self, developer: str) -> list[tuple[str, str, str, int, int, str, str]]:
        """Retrieve all games by a specific developer."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, developer, version, min_players, max_players, sha256, file_path FROM games WHERE developer = ?", (developer,))
                return cursor.fetchall()
        except Exception as e:
            logger.error("Error getting games for developer %s: %s", developer, e)
            return []
        
    def set_game(self, name: str, version: str, min_players: int, max_players: int, sha256: str, file_path: str) -> bool:
        """Update an existing game's details. Returns True if successful, False otherwise."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE games 
                    SET version = ?, min_players = ?, max_players = ?, sha256 = ?, file_path = ? 
                    WHERE name = ?
                """, (version, min_players, max_players, sha256, file_path, name))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error("Error updating game %s: %s", name, e)
            return False
