from db_manager import DBManager, DB_CONFIG

from repositories.staff_repo import StaffRepository
from repositories.schedule_repo import ScheduleRepository
from repositories.booking_repo import BookingRepository

from services.auth_service import AuthService
from services.booking_service import BookingService
from services.schedule_service import ScheduleService

from console_view import ConsoleView

# entry point
def main():
    db = DBManager(DB_CONFIG)

    staff_repo = StaffRepository(db)
    schedule_repo = ScheduleRepository(db)
    booking_repo = BookingRepository(db)

    auth_service = AuthService(staff_repo)
    booking_service = BookingService(schedule_repo, booking_repo)
    schedule_service = ScheduleService(schedule_repo, booking_repo)

    app = ConsoleView(auth_service, booking_service, schedule_service)
    app.run()

if __name__ == "__main__":
    main()
