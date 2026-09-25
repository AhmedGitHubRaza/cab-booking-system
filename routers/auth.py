from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Form,
    Response
)

from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from db import SessionLocal
from models.user import User
from utils.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

templates = Jinja2Templates(directory="templates")

# Database Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
        
        
@router.get("/signup")
def signup_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="signup.html"
    )


@router.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@router.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )
    
        
@router.post("/signup-form")
def signup_form(
    full_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.username == username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
        
    existing_email = db.query(User).filter(
        User.email == email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
    )
        
    existing_phone = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Phone Number already exists"
    )

    user = User(
        full_name=full_name,
        username=username,
        email=email,
        phone_number=phone_number,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return RedirectResponse(
        url="/auth/login",
        status_code=303
    )
    
@router.post("/login-form")
def login_form(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username"
        )

    if not verify_password(
        password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token(
        {
            "sub": user.username
        }
    )

    response = RedirectResponse(
        url="/auth/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True
    )

    return response
    
    
# Signup Schema
class SignupRequest(BaseModel):

    full_name: str
    username: str
    email: EmailStr
    phone_number: str
    password: str


# Login Schema
class LoginRequest(BaseModel):

    username: str
    password: str


# Signup Route
@router.post("/signup")
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):

    existing_username = db.query(
        User
    ).filter(
        User.username == data.username
    ).first()

    if existing_username:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = db.query(
        User
    ).filter(
        User.email == data.email
    ).first()

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user = User(

        full_name=data.full_name,
        username=data.username,
        email=data.email,        
        phone_number=data.phone_number,
        password=hash_password(
            data.password
        )
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "message": "Account Created Successfully"
    }


# Login Route
@router.post("/login")
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username"
        )

    if not verify_password(
        data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token(
        {
            "sub": user.username
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True
    )

    return {

        "message": "Login Successful",

        "access_token": token,

        "token_type": "bearer"
    }