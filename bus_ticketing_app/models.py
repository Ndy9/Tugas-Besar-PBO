from dataclasses import dataclass
from datetime import datetime

@dataclass
class Staff:
    id_staff: int
    username: str
    password: str

@dataclass
class BusSchedule:
    id_schedule: int
    origin: str
    destination: str
    depart_time: datetime
    arrive_time: datetime
    price: float
    seats_total: int
    seats_available: int

@dataclass
class Booking:
    id_booking: int
    customer_name: str
    customer_phone: str
    schedule_id: int
    seats_booked: int
    total_price: float
    booked_at: datetime
