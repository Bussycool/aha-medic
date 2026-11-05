from enum import Enum

class Appointment_Status(str, Enum):
  BOOKED = 'booked'
  CANCELLED = 'cancelled'
