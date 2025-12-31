from typing import Optional
from models import Staff
from repositories.base_repo import BaseRepository

# sub class
class StaffRepository(BaseRepository):

    # verifikasi
    def find_by_username(self, username: str) -> Optional[Staff]:
        row = self._fetchone(
            "SELECT * FROM staff WHERE username = %s",
            (username,)
        )
        return Staff(**row) if row else None  # return object Staff
