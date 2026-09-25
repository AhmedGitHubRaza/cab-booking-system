from sqlalchemy import Column, Integer, String, Boolean
from db import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(String)

    username = Column(
        String,
        unique=True
    )

    email = Column(
        String,
        unique=True
    )
    
    phone_number = Column(
        String,
        unique=True
    )

    password = Column(String)

    role = Column(
        String,
        default="user"
    )

    is_verified = Column(
        Boolean,
        default=False
    )