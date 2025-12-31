from typing import List, Optional
from datetime import datetime
from models import BusSchedule
from repositories.schedule_repo import ScheduleRepository
from repositories.booking_repo import BookingRepository

class ScheduleService:
    def __init__(self, schedule_repo: ScheduleRepository, booking_repo: BookingRepository):
        self.schedule_repo = schedule_repo
        self.booking_repo = booking_repo

    def get_schedule(self, schedule_id:int):
        return self.schedule_repo.find_by_id(schedule_id)

    # tampilkan data bus semua / aktif saja
    def list_schedules(self, active_only: bool = True) -> List[BusSchedule]:
        return self.schedule_repo.list_all(active_only=active_only)

    def create_schedule(self, origin: str, destination: str, depart_time: datetime, arrive_time: datetime, price: float, seats_total: int) -> BusSchedule:
        if seats_total <= 0:
            raise ValueError("Total kursi harus > 0.")
        if price <= 0:
            raise ValueError("Harga harus > 0.")
        if arrive_time <= depart_time:
            raise ValueError("Waktu tiba harus setelah waktu berangkat.")

        schedule_id = self.schedule_repo.create_schedule(
            origin, destination, depart_time, arrive_time, price, seats_total
        )
        created = self.schedule_repo.find_by_id(schedule_id)
        if not created:
            raise ValueError("Jadwal gagal dibuat.")
        return created

    def update_schedule(self,
                        schedule_id: int,
                        new_origin: Optional[str] = None,
                        new_destination: Optional[str] = None,
                        new_depart_time: Optional[datetime] = None,
                        new_arrive_time: Optional[datetime] = None,
                        new_price: Optional[float] = None,
                        new_seats_total: Optional[int] = None) -> BusSchedule:

        old = self.schedule_repo.find_by_id(schedule_id)
        if not old:
            raise ValueError("Jadwal tidak ditemukan.")

        # pakai data lama kalau None / kosong
        final_origin = new_origin.strip() if new_origin and new_origin.strip() != "" else old.origin
        final_destination = new_destination.strip() if new_destination and new_destination.strip() != "" else old.destination
        final_depart = new_depart_time if new_depart_time else old.depart_time
        final_arrive = new_arrive_time if new_arrive_time else old.arrive_time
        final_price = new_price if new_price is not None else old.price
        final_seats_total = new_seats_total if new_seats_total is not None else old.seats_total

        if final_seats_total <= 0:
            raise ValueError("Total kursi harus > 0.")
        if final_price <= 0:
            raise ValueError("Harga harus > 0.")
        if final_arrive <= final_depart:
            raise ValueError("Waktu tiba harus setelah waktu berangkat.")
        
        # kursi yg sudah di pesan/booking
        booked = old.seats_total - old.seats_available
        if final_seats_total < booked:
            raise ValueError(
                f"Total kursi baru ({final_seats_total}) tidak boleh "
                f"lebih kecil dari kursi yang sudah dibooking ({booked})."
            )
        final_seats_available = final_seats_total - booked

        self.schedule_repo.update_schedule(
            schedule_id,
            final_origin,
            final_destination,
            final_depart,
            final_arrive,
            final_price,
            final_seats_total,
            final_seats_available
        )

        return self.schedule_repo.find_by_id(schedule_id)

    # hanya bisa delete jika tidak ada booking
    def delete_schedule(self, schedule_id: int):
        old = self.schedule_repo.find_by_id(schedule_id)
        if not old:
            raise ValueError("Jadwal tidak ditemukan.")

        # cek booking dulu
        if self.booking_repo.count_by_schedule(schedule_id) > 0:
            raise ValueError("Jadwal tidak bisa dihapus karena sudah ada booking.")

        self.schedule_repo.delete_schedule(schedule_id)
