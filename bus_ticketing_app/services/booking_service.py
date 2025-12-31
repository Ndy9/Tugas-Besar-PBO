from typing import List, Optional
from models import Booking
from repositories.schedule_repo import ScheduleRepository
from repositories.booking_repo import BookingRepository


class BookingService:
    def __init__(self, schedule_repo: ScheduleRepository, booking_repo: BookingRepository):
        self.schedule_repo = schedule_repo
        self.booking_repo = booking_repo

    def create_booking(self, customer_name: str, customer_phone: str, schedule_id: int, seats: int) -> Booking:
        if seats <= 0:
            raise ValueError("Jumlah kursi harus > 0.")
        
        # cek data jadwal bus
        schedule = self.schedule_repo.find_by_id(schedule_id)
        if not schedule:
            raise ValueError("Jadwal tidak ditemukan.")
        if schedule.seats_available < seats:
            raise ValueError("Kursi tidak cukup.")

        new_available = schedule.seats_available - seats
        self.schedule_repo.update_seats(schedule_id, new_available)

        total_price = seats * schedule.price
        booking_id = self.booking_repo.create_booking(
            customer_name, customer_phone, schedule_id, seats, total_price
        )

        created = self.booking_repo.find_by_id(booking_id)
        if not created:
            raise ValueError("Booking gagal dibuat.")
        return created

    def list_bookings(self) -> List[Booking]:
        return self.booking_repo.list_all()
    
    def cancel_booking(self, booking_id: int):
        booking = self.booking_repo.find_by_id(booking_id)
        if not booking:
            raise ValueError("Booking tidak ditemukan.")

        schedule = self.schedule_repo.find_by_id(booking.schedule_id)
        if not schedule:
            raise ValueError("Jadwal booking tidak valid.")

        # balikin stok kursi
        new_available = schedule.seats_available + booking.seats_booked
        if new_available > schedule.seats_total:
            new_available = schedule.seats_total

        self.schedule_repo.update_seats(schedule.id_schedule, new_available)
        self.booking_repo.delete_booking(booking_id)

    def update_booking(self,
                       booking_id: int,
                       new_name: Optional[str] = None,
                       new_phone: Optional[str] = None,
                       new_schedule_id: Optional[int] = None,
                       new_seats: Optional[int] = None) -> Booking:

        booking = self.booking_repo.find_by_id(booking_id)
        if not booking:
            raise ValueError("Booking tidak ditemukan.")

        # pakai value lama kalau kosong / None
        final_name = new_name if (new_name is not None and new_name.strip() != "") else booking.customer_name
        final_phone = new_phone if (new_phone is not None and new_phone.strip() != "") else booking.customer_phone
        final_schedule_id = new_schedule_id if (new_schedule_id is not None) else booking.schedule_id
        final_seats = new_seats if (new_seats is not None) else booking.seats_booked

        if final_seats <= 0:
            raise ValueError("Jumlah kursi harus > 0.")

        old_schedule = self.schedule_repo.find_by_id(booking.schedule_id)
        if not old_schedule:
            raise ValueError("Jadwal lama tidak valid.")

        new_schedule = self.schedule_repo.find_by_id(final_schedule_id)
        if not new_schedule:
            raise ValueError("Jadwal baru tidak ditemukan.")

        # ---- CASE 1: jadwal ganti ----
        if final_schedule_id != booking.schedule_id:
            # refresh dulu stok jadwal lama
            fresh_old = self.schedule_repo.find_by_id(old_schedule.id_schedule)
            if not fresh_old:
                raise ValueError("Jadwal lama tidak valid.")
            
            # balikin kursi ke jadwal lama
            self.schedule_repo.update_seats(
                fresh_old.id_schedule,
                fresh_old.seats_available + booking.seats_booked
            )

            # refresh jadwal baru juga
            fresh_new = self.schedule_repo.find_by_id(new_schedule.id_schedule)
            if not fresh_new:
                raise ValueError("Jadwal baru tidak valid.")    

            # cek kursi di jadwal baru
            if fresh_new.seats_available < final_seats:
                raise ValueError("Kursi di jadwal baru tidak cukup.")

            # kurangin kursi di jadwal baru
            self.schedule_repo.update_seats(
                fresh_new.id_schedule,
                fresh_new.seats_available - final_seats
            )

        # ---- CASE 2: jadwal sama, cuma kursi berubah ----
        else:
            delta = final_seats - booking.seats_booked

            # ambil ulang stok terbaru biar gak stale
            current_schedule = self.schedule_repo.find_by_id(old_schedule.id_schedule)
            if not current_schedule:
                raise ValueError("Jadwal tidak valid.")

            if delta > 0 and current_schedule.seats_available < delta:
                raise ValueError("Kursi tidak cukup untuk update.")

            self.schedule_repo.update_seats(
                current_schedule.id_schedule,
                current_schedule.seats_available - delta
            )

        final_total = final_seats * new_schedule.price

        self.booking_repo.update_booking(
            booking_id,
            final_name,
            final_phone,
            final_schedule_id,
            final_seats,
            final_total
        )

        return self.booking_repo.find_by_id(booking_id)

