from sqlalchemy import Column, Integer, String, Float, ForeignKey

from db import Base


class RideBooking(Base):

    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    invoice_id = Column(String, unique=True)

    customer_name = Column(String)

    phone_number = Column(String)

    pickup_location = Column(String)

    drop_location = Column(String)

    car_type = Column(String)

    base_fare = Column(Float)

    tax = Column(Float)

    total_fare = Column(Float)

    payment_status = Column(
        String,
        default="Pending"
    )

    booking_status = Column(
        String,
        default="Confirmed"
    )

    booking_time = Column(String)

    arrival_time = Column(String)