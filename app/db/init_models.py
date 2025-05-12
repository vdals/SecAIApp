"""
Модуль для инициализации forward references в Pydantic моделях.
"""

import importlib
import inspect
import sys

from app.users.schemas import UserWithLocations
from app.locations.schemas import LocationWithUsers, LocationWithCameras, LocationFull
from app.cameras.schemas import CameraWithLocation, CameraWithOwner, CameraFull
from app.videos.schemas import VideoWithEvents, VideoFull
from app.events.schemas import EventWithVideo, EventFull

# Импортируем все модули схем для инициализации всех типов
import app.users.schemas
import app.locations.schemas
import app.cameras.schemas
import app.videos.schemas
import app.events.schemas


def update_forward_refs() -> None:
    """
    Updates all string references in Pydantic models.
    In Pydantic v2 the update_forward_refs method does not accept arguments.
    """
    
    # Initialize user schemas
    UserWithLocations.model_rebuild()
    
    # Initialize location schemas
    LocationWithUsers.model_rebuild()
    LocationWithCameras.model_rebuild()
    LocationFull.model_rebuild()
    
    # Initialize camera schemas
    CameraWithLocation.model_rebuild()
    CameraWithOwner.model_rebuild()
    CameraFull.model_rebuild()
    
    # Initialize video schemas
    VideoWithEvents.model_rebuild()
    VideoFull.model_rebuild()
    
    # Initialize event schemas
    EventWithVideo.model_rebuild()
    EventFull.model_rebuild()

init_models = update_forward_refs 