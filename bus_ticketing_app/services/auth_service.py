from models import Staff
from repositories.staff_repo import StaffRepository


class AuthService:
    def __init__(self, staff_repo: StaffRepository):
        self.staff_repo = staff_repo

    def login(self, username: str, password: str) -> Staff:
        staff = self.staff_repo.find_by_username(username)
        if not staff:
            raise ValueError("Username petugas tidak ditemukan.")

        if staff.password != password:
            raise ValueError("Password salah.")

        return staff