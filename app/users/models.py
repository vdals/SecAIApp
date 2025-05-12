from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base import BaseDBModel, Base

# User-location relationship table
user_location = Table(
    "user_location",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("location_id", Integer, ForeignKey("location.id"), primary_key=True),
)


class User(BaseDBModel):
    """User model"""
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=True)
    
    # Отношения
    role = relationship("Role", back_populates="users")
    locations = relationship("Location", secondary=user_location, back_populates="users")
    cameras = relationship("Camera", back_populates="owner")
    
    def __repr__(self):
        return f"<User {self.email}>" 