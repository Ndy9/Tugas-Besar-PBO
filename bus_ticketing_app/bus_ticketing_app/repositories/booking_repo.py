from typing import List, Optional
from models import Booking
from repositories.base_repo import BaseRepository

#sub class
class BookingRepository(BaseRepository):

    def create_booking(self, customer_name: str, customer_phone: str, schedule_id: int, seats: int, total_price: float) -> int:
        # simpan data booking baru ke DB
        query = """
            INSERT INTO booking(customer_name, customer_phone, schedule_id, seats_booked, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """
        booking_id = self._execute(
            query,
            (customer_name, customer_phone, schedule_id, seats, total_price),
            commit=True
        )
        
        return int(booking_id) # ambil id booking baru

    def list_all(self) -> List[Booking]:
        # ambil semua riwayat booking buat laporan/lihat transaksi
        rows = self._fetchall(
            "SELECT * FROM booking ORDER BY id_booking"
        )
        return [self._to_booking(r) for r in rows]
    
    # cari data berdasarkan id / verifikasi
    def find_by_id(self, booking_id: int) -> Optional[Booking]:
        row = self._fetchone("SELECT * FROM booking WHERE id_booking=%s", (booking_id,))
        return self._to_booking(row) if row else None

    def update_booking(self, booking_id: int, customer_name: str, customer_phone: str, schedule_id: int, seats_booked: int, total_price: float):
        query = """
            UPDATE booking
            SET customer_name=%s,
                customer_phone=%s,
                schedule_id=%s,
                seats_booked=%s,
                total_price=%s
            WHERE id_booking=%s
        """
        self._execute(
            query,
            (customer_name, customer_phone, schedule_id, seats_booked, total_price, booking_id),
            commit=True
        )

    def delete_booking(self, booking_id: int):
        self._execute("DELETE FROM booking WHERE id_booking=%s", (booking_id,), commit=True)

    # jumlah booking pada schedule (delete schedule)
    def count_by_schedule(self, schedule_id: int) -> int:
        row = self._fetchone(
            "SELECT COUNT(*) AS cnt FROM booking WHERE schedule_id=%s",
            (schedule_id,)
        )
        return int(row["cnt"])

    @staticmethod
    def _to_booking(row: dict) -> Booking:
        # ubah data dictionary dari DB jadi object Booking
        return Booking(
            id_booking=row["id_booking"],
            customer_name=row["customer_name"],
            customer_phone=row["customer_phone"],
            schedule_id=row["schedule_id"],
            seats_booked=row["seats_booked"],
            total_price=float(row["total_price"]),
            booked_at=row["booked_at"]
        )
