from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import sqlite3
from sqlite3 import Connection
from typing import Any, Callable, Dict, List, Optional
import threading
import time

logger = get_logger("soma.storage.sqlite")

class SQLiteStorage:
    def __init__(self):
        self.db_url = getattr(config.database, 'url', 'data/seaa.db')
        self.pool_size = getattr(config.database, 'pool_size', 5)
        self.connection_pool: List[Connection] = []
        self._initialize_database()
        bus.subscribe('*', self.on_event)

    def _initialize_database(self):
        conn = sqlite3.connect(self.db_url)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organs (
                name TEXT PRIMARY KEY,
                description TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organ_name TEXT NOT NULL,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (organ_name) REFERENCES organs(name)
            )
        ''')
        conn.commit()
        self.connection_pool.append(conn)

    def _get_connection(self) -> Connection:
        if not self.connection_pool:
            return sqlite3.connect(self.db_url)
        return self.connection_pool.pop()

    def _release_connection(self, conn: Connection):
        if len(self.connection_pool) < self.pool_size:
            self.connection_pool.append(conn)
        else:
            conn.close()

    def on_event(self, event: Event):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (event_type, data)
            VALUES (?, ?)
        ''', (event.event_type, str(event.data)))
        conn.commit()
        self._release_connection(conn)

    def query_events(self, event_type: Optional[str] = None,
                     start_time: Optional[str] = None,
                     end_time: Optional[str] = None,
                     organ_name: Optional[str] = None) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM events WHERE 1=1'
        params = []
        if event_type:
            query += ' AND event_type=?'
            params.append(event_type)
        if start_time:
            query += ' AND timestamp>=?'
            params.append(start_time)
        if end_time:
            query += ' AND timestamp<=?'
            params.append(end_time)
        cursor.execute(query, params)
        results = cursor.fetchall()
        self._release_connection(conn)
        return [{'id': row[0], 'event_type': row[1], 'data': row[2], 'timestamp': row[3]} for row in results]

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = SQLiteStorage()