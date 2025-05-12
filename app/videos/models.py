from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean, BigInteger
from sqlalchemy.orm import relationship

from app.db.base import BaseDBModel


class Video(BaseDBModel):
    """Video file model"""
    
    filename = Column(String(255), index=True, nullable=False)
    filepath = Column(String(512), nullable=False)
    file_size = Column(BigInteger, default=0, nullable=False)  # File size in bytes
    duration = Column(Integer, default=0)  # Duration in seconds
    
    # Metadata
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    fps = Column(Integer, nullable=True)
    codec = Column(String(50), nullable=True)
    format = Column(String(50), nullable=True)
    
    # Recording start and end time
    recording_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    recording_end = Column(DateTime, nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False)
    is_analyzed = Column(Boolean, default=False, nullable=False)  # Analyzed by AI
    processing_status = Column(String(50), default="pending", nullable=False)
    
    # Relationships
    camera_id = Column(Integer, ForeignKey("camera.id"), nullable=False, index=True)
    camera = relationship("Camera", back_populates="videos")
    events = relationship("Event", back_populates="video", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Video {self.filename}>" 