from datetime import datetime
from typing import Optional

from models import Staff
from services.auth_service import AuthService
from services.booking_service import BookingService
from services.schedule_service import ScheduleService

class ConsoleView:
    def __init__(self, auth_service: AuthService, booking_service: BookingService, schedule_service: ScheduleService):
        self.auth_service = auth_service
        self.booking_service = booking_service
        self.schedule_service = schedule_service
        self.current_staff: Optional[Staff] = None

    def run(self):
        while True:
            try:
                if self.current_staff is None:
                    self._menu_login()
                else:
                    self._menu_loket()
            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

    def _menu_login(self):
        print("\n=== LOGIN PETUGAS LOKET ===")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        self.current_staff = self.auth_service.login(username, password)
        print(f"\nLogin berhasil. Halo, {self.current_staff.username}!\n")

    def _menu_loket(self):
        print("=== MENU LOKET BUS ===")
        print("1. Lihat Jadwal")
        print("2. Pesan Tiket")
        print("3. Lihat Semua Transaksi")
        print("4. Kelola Jadwal Bus")
        print("5. Kelola Tiket")
        print("\n9. Logout")
        print("0. Keluar")

        choice = input("\nPilih: ").strip()
        if choice == "1":
            self._show_schedules(active_only=False)
        elif choice == "2":
            self._make_booking()
        elif choice == "3":
            self._show_all_bookings()
        elif choice == "4":
            self._manage_schedules()
        elif choice == "5":
            self._manage_tickets()
        elif choice == "9":
            self.current_staff = None
            print("Logout berhasil.\n")
        elif choice == "0":
            raise SystemExit
        else:
            print("Pilihan tidak valid.\n")

    # Menu 1
    def _show_schedules(self, active_only: bool = True):
        schedules = self.schedule_service.list_schedules(active_only=active_only)
        print("\n--- JADWAL BUS ---")
        if not schedules:
            print("Belum ada jadwal.\n")
            return

        header = (
            f"{'ID':^4} | {'Asal':^15} | {'Tujuan':^15} | "
            f"{'Berangkat':^16} | {'Tiba':^16} | {'Harga':^12} | {'Kursi':^9}"
        )
        print(header)
        print("-" * len(header))

        for s in schedules:
            depart = f"{s.depart_time:%Y-%m-%d %H:%M}"
            arrive = f"{s.arrive_time:%Y-%m-%d %H:%M}"
            harga = f"{s.price:>10,.0f}"
            kursi = f"{s.seats_available}/{s.seats_total}"

            print(
                f"{s.id_schedule:^4} | {s.origin:<15} | {s.destination:<15} | "
                f"{depart:<16} | {arrive:<16} | Rp{harga} | {kursi:^9}"
            )
        print()


    # Menu 2
    def _make_booking(self):
        self._show_schedules()
        name = input("Nama pembeli: ").strip()
        phone = input("No HP pembeli: ").strip()
        schedule_id = int(input("ID jadwal: "))
        seats = int(input("Jumlah kursi: "))

        booking = self.booking_service.create_booking(
            name, phone, schedule_id, seats
        )

        print("\n=== STRUK PEMESANAN ===")
        print(f"Booking ID  : {booking.id_booking}")
        print(f"Nama        : {booking.customer_name}")
        print(f"No HP       : {booking.customer_phone}")
        print(f"Jadwal ID   : {booking.schedule_id}")
        print(f"Jumlah kursi: {booking.seats_booked}")
        print(f"Total bayar : Rp{booking.total_price:,.0f}")
        print(f"Waktu pesan : {booking.booked_at:%Y-%m-%d %H:%M}\n")
    
    # Menu 3
    def _show_all_bookings(self):
        bookings = self.booking_service.list_bookings()
        print("\n--- SEMUA TRANSAKSI ---")
        if not bookings:
            print("Belum ada transaksi.\n")
            return

        header = (
            f"{'ID':^4} | {'Nama':^18} | {'No HP':^12} | {'Rute':^20} | "
            f"{'Berangkat':^16} | {'Tiba':^16} | {'Harga/Seat':^12} | {'Kursi':^5} | {'Total':^12} | {'Tgl Pesan':^16}"
        )
        print(header)
        print("-" * len(header))

        for b in bookings:
            schedule = self.schedule_service.get_schedule(b.schedule_id)

            if schedule:
                rute = f"{schedule.origin} -> {schedule.destination}"
                depart = f"{schedule.depart_time:%Y-%m-%d %H:%M}"
                arrive = f"{schedule.arrive_time:%Y-%m-%d %H:%M}"
            else:
                rute = "Jadwal tidak ada"
                depart = "-"
                arrive = "-"
            
            price_per_seat = b.total_price/b.seats_booked
            price_per_seat = f"{price_per_seat:>10,.0f}"

            created_at = f"{b.booked_at:%Y-%m-%d %H:%M}"

            print(
                f"{b.id_booking:^4} | {b.customer_name:<18} | {b.customer_phone:<12} | {rute:<20} | "
                f"{depart:<16} | {arrive:<16} | Rp{price_per_seat} | {b.seats_booked:^5} | "
                f"Rp{b.total_price:>10,.0f} | {created_at:<16}"
            )

        print()


    ### KELOLA SCHEDULES ###  Menu 4
    def _manage_schedules(self):
        while True:
            print("\n=== KELOLA JADWAL BUS ===")
            print("1. Tambah Jadwal Bus")
            print("2. Ubah Jadwal Bus")
            print("3. Hapus Jadwal Bus")
            print("\n9. Kembali")

            sub = input("\nPilih: ").strip()
            if sub == "1":
                self._add_schedule()
            elif sub == "2":
                self._update_schedule()
            elif sub == "3":
                self._delete_schedule()
            elif sub == "9":
                print()
                return
            else:
                print("Pilihan tidak valid.\n")

    def _add_schedule(self):
        origin = input("Asal: ").strip()
        destination = input("Tujuan: ").strip()
        depart_str = input("Berangkat (YYYY-MM-DD HH:MM): ").strip()
        arrive_str = input("Tiba (YYYY-MM-DD HH:MM): ").strip()
        price = float(input("Harga tiket: ").strip())
        seats_total = int(input("Total kursi: ").strip())

        depart_time = datetime.strptime(depart_str, "%Y-%m-%d %H:%M")
        arrive_time = datetime.strptime(arrive_str, "%Y-%m-%d %H:%M")

        created = self.schedule_service.create_schedule(
            origin, destination, depart_time, arrive_time, price, seats_total
        )

        print(f"Jadwal berhasil ditambahkan. ID={created.id_schedule}\n")

    def _update_schedule(self):
        self._show_schedules()
        schedule_id = int(input("Masukkan ID jadwal yang mau diubah: "))

        print("Kosongkan jika tidak ingin diubah.")

        origin = input("Asal baru: ").strip()
        destination = input("Tujuan baru: ").strip()

        depart_in = input("Waktu berangkat baru (YYYY-MM-DD HH:MM): ").strip()
        arrive_in = input("Waktu tiba baru (YYYY-MM-DD HH:MM): ").strip()

        price_in = input("Harga baru: ").strip()
        seats_in = input("Total kursi baru: ").strip()

        new_depart = datetime.strptime(depart_in, "%Y-%m-%d %H:%M") if depart_in != "" else None
        new_arrive = datetime.strptime(arrive_in, "%Y-%m-%d %H:%M") if arrive_in != "" else None
        new_price = float(price_in) if price_in != "" else None
        new_seats_total = int(seats_in) if seats_in != "" else None

        updated = self.schedule_service.update_schedule(
            schedule_id,
            origin if origin != "" else None,
            destination if destination != "" else None,
            new_depart,
            new_arrive,
            new_price,
            new_seats_total
        )

        print(f"\nJadwal berhasil diupdate. ID={updated.id_schedule}\n")

    def _delete_schedule(self):
        self._show_schedules()
        schedule_id = int(input("Masukkan ID jadwal yang mau dihapus: "))

        self.schedule_service.delete_schedule(schedule_id)
        print("Jadwal berhasil dihapus.\n")



    ### KELOLA TIKET ###  Menu 5
    def _manage_tickets(self):
        while True:
            print("\n=== KELOLA TIKET ===")
            print("1 Update Tiket")
            print("2 Cancel Tiket")
            print("\n9. Kembali")

            sub = input("\nPilih: ").strip()
            if sub == "1":
                self._update_ticket()
            elif sub == "2":
                self._cancel_ticket()
            elif sub == "9":
                print()
                return
            else:
                print("Pilihan tidak valid.\n")

    def _update_ticket(self):
        self._show_schedules()
        self._show_all_bookings()
        booking_id = int(input("Masukkan Booking ID yang mau diupdate: "))

        print("Kosongkan jika tidak ingin di ubah.")

        new_name = input("Nama baru: ").strip()
        new_phone = input("No HP baru: ").strip()

        sched_in = input("ID Jadwal baru: ").strip()
        new_schedule_id = int(sched_in) if sched_in != "" else None

        seats_in = input("Jumlah kursi baru: ").strip()
        new_seats = int(seats_in) if seats_in != "" else None

        updated = self.booking_service.update_booking(
            booking_id,
            new_name if new_name != "" else None,
            new_phone if new_phone != "" else None,
            new_schedule_id,
            new_seats
        )

        print("\n=== BOOKING BERHASIL DIUPDATE ===")
        print(f"Booking ID  : {updated.id_booking}")
        print(f"Nama        : {updated.customer_name}")
        print(f"No HP       : {updated.customer_phone}")
        print(f"Jadwal ID   : {updated.schedule_id}")
        print(f"Jumlah kursi: {updated.seats_booked}")
        print(f"Total bayar : Rp{updated.total_price:,.0f}")
        print(f"Waktu pesan : {updated.booked_at:%Y-%m-%d %H:%M}\n")

    def _cancel_ticket(self):
        self._show_all_bookings()
        booking_id = int(input("Masukkan Booking ID yang mau dicancel: "))

        self.booking_service.cancel_booking(booking_id)
        print("Booking berhasil dicancel. Kursi dikembalikan.\n")


    