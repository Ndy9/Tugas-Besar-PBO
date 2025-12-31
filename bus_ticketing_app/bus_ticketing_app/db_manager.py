import mysql.connector  # koneksi MySQL

# config DB
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bus_ticketing"
}

class DBManager:
    def __init__(self, config: dict = DB_CONFIG):
        self._config = config  # config database

    def _connect(self):
        # buka koneksi ke database
        return mysql.connector.connect(**self._config)

    def execute(self, query: str, params: tuple = (), fetchone: bool = False, fetchall: bool = False, commit: bool = False):
        conn = self._connect()  # mulai koneksi
        try:
            cursor = conn.cursor(dictionary=True)  # hasil query jadi dict
            cursor.execute(query, params)          # jalanin query

            result = None
            if fetchone:
                result = cursor.fetchone()  # ambil 1 data
            if fetchall:
                result = cursor.fetchall()  # ambil semua data

            last_id = None
            if commit:
                conn.commit()  # simpen perubahan ke DB
                last_id = cursor.lastrowid # ambil id insert

            cursor.close()  # tutup cursor

            return last_id if last_id else result   # kalau commit dan ini insert, balikin last_id
        finally:
            conn.close()  # tutup koneksi
