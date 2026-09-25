from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from db import Base, engine
from models.user import User
from models.ride import RideBooking
from routers.ride import router as ride_router
from routers.auth import router as auth_router
from routers.admin import router as admin_router

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cab Booking System")


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(ride_router)
app.include_router(admin_router)

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )