from typing import Optional, List
from datetime import datetime
from models import BusSchedule
from repositories.base_repo import BaseRepository

# sub class
class ScheduleRepository(BaseRepository): 
    
    def list_all(self, active_only: bool = True) -> List[BusSchedule]:
        # tampilkan jadwal bus yang masih aktif
        if active_only:
            rows = self._fetchall(
                "SELECT * FROM schedules WHERE depart_time > %s ORDER BY depart_time",
                (datetime.now(),)
            )
        # tampilkan semua jadwal bus
        else:
            rows = self._fetchall(
                "SELECT * FROM schedules ORDER BY depart_time"
            )
        return [self._to_schedule(r) for r in rows]

    def find_by_id(self, schedule_id: int) -> Optional[BusSchedule]:
        # cari jadwal berdasarkan id / verifikasi
        row = self._fetchone(
            "SELECT * FROM schedules WHERE id_schedule = %s",
            (schedule_id,)
        )
        return self._to_schedule(row) if row else None

    def update_seats(self, schedule_id: int, new_available: int) -> None:
        # update sisa kursi setelah booking
        self._execute(
            "UPDATE schedules SET seats_available = %s WHERE id_schedule = %s",
            (new_available, schedule_id),
            commit=True
        )

    def create_schedule(self, origin: str, destination: str, depart_time: datetime, arrive_time: datetime, price: float, seats_total: int) -> int:
        # nambah jadwal baru
        query = """
            INSERT INTO schedules(origin, destination, depart_time, arrive_time, price, seats_total, seats_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        schedule_id = self._execute(
            query,
            (origin, destination, depart_time, arrive_time, price, seats_total, seats_total),
            commit=True
        )

        return int(schedule_id)
    
    def update_schedule(self, schedule_id: int, origin: str, destination: str, depart_time: datetime, arrive_time: datetime, price: float, seats_total: int, seats_available: int) -> None:
        query = """
            UPDATE schedules
            SET origin=%s,
                destination=%s,
                depart_time=%s,
                arrive_time=%s,
                price=%s,
                seats_total=%s,
                seats_available=%s
            WHERE id_schedule=%s
        """
        self._execute(
            query,
            (origin, destination, depart_time, arrive_time,price, seats_total, seats_available, schedule_id),
            commit=True
        )

    def delete_schedule(self, schedule_id: int) -> None:
        self._execute(
            "DELETE FROM schedules WHERE id_schedule=%s",
            (schedule_id,),
            commit=True
        )

    @staticmethod
    def _to_schedule(row: dict) -> BusSchedule:
        # ubah data dict dari DB jadi object BusSchedule
        return BusSchedule(
            id_schedule=row["id_schedule"],
            origin=row["origin"],
            destination=row["destination"],
            depart_time=row["depart_time"],
            arrive_time=row["arrive_time"],
            price=float(row["price"]),
            seats_total=row["seats_total"],
            seats_available=row["seats_available"]
        )
