from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import SessionLocal
from models.ride import RideBooking

from pydantic import BaseModel

from datetime import datetime, timedelta
import uuid
from fastapi import Request
from fastapi.templating import Jinja2Templates

from fastapi import Cookie
from jose import JWTError
from utils.security import verify_token
from models.user import User

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/ride",
    tags=["Ride Booking"]
)

# Database Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
  
        
def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not access_token:

        raise HTTPException(
            status_code=401,
            detail="Login Required"
        )

    payload = verify_token(access_token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    username = payload.get("sub")

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User Not Found"
        )

    return user

@router.get("/my-rides")
def my_rides(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    rides = db.query(RideBooking).filter(
        RideBooking.user_id == current_user.id
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="rides.html",
        context={
            "rides": rides
        }
    )
    
# Request Schema
class RideRequest(BaseModel):

    pickup_location: str

    drop_location: str

    choice: int


# Helper Function
def get_car_info(choice: int):

    cars = {
        1: ("Mini", 800),
        2: ("Sedan", 1500),
        3: ("SUV", 2500)
    }

    return cars.get(choice)


# Book Ride
@router.post("/book")
def book_ride(
    data: RideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    info = get_car_info(data.choice)

    if not info:
        raise HTTPException(
            status_code=400,
            detail="Invalid Car Choice"
        )

    car_type, base_fare = info

    tax = base_fare * 0.08
    total = base_fare + tax

    invoice = "CAB-" + str(
        uuid.uuid4()
    )[:8].upper()

    now = datetime.now()

    arrival = now + timedelta(
        minutes=15
    )

    ride = RideBooking(

        user_id=current_user.id,
        
        invoice_id=invoice,
        
        customer_name=current_user.full_name,
        
        phone_number=current_user.phone_number,
        
        pickup_location=data.pickup_location,
        
        drop_location=data.drop_location,

        car_type=car_type,

        base_fare=base_fare,
        
        tax=tax,
        
        total_fare=total,

        payment_status="Pending",
        
        booking_status="Confirmed",

        booking_time=now.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        arrival_time=arrival.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    db.add(ride)

    db.commit()

    db.refresh(ride)

    return {
        "message": "Ride Booked Successfully",
        "data": ride
    }


# Get All Rides
@router.get("/all")
def get_rides(
    db: Session = Depends(get_db)
):

    return db.query(
        RideBooking
    ).all()