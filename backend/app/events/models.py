from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import relationship

from app.db.base import BaseDBModel


class Object(BaseDBModel):
    """Model of detected object"""
    
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False, index=True)
    object_type = Column(String(100), nullable=False, index=True)  # person, car, animal, etc.
    confidence = Column(Float, nullable=False)  # Уверенность алгоритма (0-1)
    
    # Object coordinates (bounding box)
    x_min = Column(Integer, nullable=False)
    y_min = Column(Integer, nullable=False)
    x_max = Column(Integer, nullable=False)
    y_max = Column(Integer, nullable=False)
    
    attributes = Column(JSON, nullable=True)
    
    event = relationship("Event", back_populates="objects")
    
    def __repr__(self):
        return f"<Object {self.object_type}>"


class Event(BaseDBModel):
    """Model of event (incident)"""
    
    event_type = Column(String(100), nullable=False, index=True)  # motion, person_detected, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    is_confirmed = Column(Boolean, default=False, nullable=False)  # Confirmed by user
    is_false_positive = Column(Boolean, default=False, nullable=False)  # False positive
    
    frame_number = Column(Integer, nullable=True)
    frame_timestamp = Column(DateTime, nullable=True)  # Frame timestamp
    frame_path = Column(String(512), nullable=True)  # Path to saved frame
    
    camera_id = Column(Integer, ForeignKey("camera.id"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("video.id"), nullable=True, index=True)
    
    camera = relationship("Camera", back_populates="events")
    video = relationship("Video", back_populates="events")
    objects = relationship("Object", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event {self.event_type}>" 