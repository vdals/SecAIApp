from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from app.db.base import BaseDBModel


class Camera(BaseDBModel):
    """Camera model"""
    
    name = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(255), nullable=True)
    rtsp_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    fps = Column(Integer, nullable=True)
    rotation = Column(Integer, default=0, nullable=True)  # Поворот камеры в градусах
    timezone = Column(String(50), nullable=True)
    
    location = relationship("Location", back_populates="cameras")
    owner = relationship("User", back_populates="cameras")
    videos = relationship("Video", back_populates="camera", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="camera", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Camera {self.name}>" 