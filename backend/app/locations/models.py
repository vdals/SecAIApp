from sqlalchemy import Column, String, Text, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import BaseDBModel
from app.users.models import user_location


class Location(BaseDBModel):
    """Model of location (house)"""
    
    name = Column(String(255), index=True, nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Отношения
    users = relationship("User", secondary=user_location, back_populates="locations")
    cameras = relationship("Camera", back_populates="location", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Location {self.name}>" 