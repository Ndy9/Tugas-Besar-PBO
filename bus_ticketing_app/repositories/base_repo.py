from db_manager import DBManager

# super class
class BaseRepository:
    def __init__(self, db: DBManager):
        self.db = db  # koneksi DB

    def _fetchone(self, query: str, params: tuple = ()):
        # ambil 1 baris data dari DB
        return self.db.execute(query, params, fetchone=True)

    def _fetchall(self, query: str, params: tuple = ()):
        # ambil banyak baris data dari DB
        return self.db.execute(query, params, fetchall=True)

    def _execute(self, query: str, params: tuple = (), commit: bool = False):
        # jalanin query (INSERT/UPDATE/DELETE)
        return self.db.execute(query, params, commit=commit)
