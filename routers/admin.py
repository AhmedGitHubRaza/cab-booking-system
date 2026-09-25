from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import SessionLocal
from models.ride import RideBooking
from pydantic import BaseModel

from fastapi import Request
from fastapi.templating import Jinja2Templates

from fastapi.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")
class StatusUpdate(BaseModel):
    booking_status: str
    payment_status: str
    
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/rides")
def get_all_rides(
    db: Session = Depends(get_db)
):
    return db.query(RideBooking).all()

@router.put("/update-status/{ride_id}")
def update_status(
    ride_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db)
):

    ride = db.query(
        RideBooking
    ).filter(
        RideBooking.id == ride_id
    ).first()

    if not ride:
        raise HTTPException(
            status_code=404,
            detail="Ride Not Found"
        )

    ride.booking_status = data.booking_status
    ride.payment_status = data.payment_status

    db.commit()

    return {
        "message": "Status Updated Successfully"
    }
    
@router.delete("/delete/{ride_id}")
def delete_ride(
    ride_id: int,
    db: Session = Depends(get_db)
):

    ride = db.query(
        RideBooking
    ).filter(
        RideBooking.id == ride_id
    ).first()

    if not ride:
        raise HTTPException(
            status_code=404,
            detail="Ride Not Found"
        )

    db.delete(ride)

    db.commit()

    return {
        "message": "Ride Deleted Successfully"
    }
   
    
@router.get("/dashboard")
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    rides = db.query(
        RideBooking
    ).all()

    total_rides = len(rides)

    total_revenue = sum(
        ride.total_fare
        for ride in rides
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "rides": rides,
            "total_rides": total_rides,
            "total_revenue": total_revenue
        }
    )
   
    
@router.get("/mark-paid/{ride_id}")
def mark_paid(
    ride_id: int,
    db: Session = Depends(get_db)
):

    ride = db.query(
        RideBooking
    ).filter(
        RideBooking.id == ride_id
    ).first()

    if not ride:
        raise HTTPException(
            status_code=404,
            detail="Ride Not Found"
        )

    ride.payment_status = "Paid"

    db.commit()

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=303
    )
    
@router.get("/mark-completed/{ride_id}")
def mark_completed(
    ride_id: int,
    db: Session = Depends(get_db)
):

    ride = db.query(
        RideBooking
    ).filter(
        RideBooking.id == ride_id
    ).first()

    if not ride:
        raise HTTPException(
            status_code=404,
            detail="Ride Not Found"
        )

    ride.booking_status = "Completed"

    db.commit()

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=303
    )