import os
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form, Body
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, CurrentEventManager, CurrentSuperuser
from app.common.schemas import PaginatedResult, PaginationParams
from app.common.utils import NotFoundException
from app.db.session import get_db
from app.users.models import User
from app.events.schemas import (
    Event, EventCreate, EventUpdate, EventWithObjects, EventWithCamera, EventWithVideo, EventFull,
    Object, ObjectCreate, ObjectUpdate, EventStats, AIDetectionResult
)
from app.events.service import EventService, ObjectService

router = APIRouter(prefix="/events", tags=["events"])

event_service = EventService()
object_service = ObjectService()


@router.get("/", response_model=PaginatedResult[Event], summary="Get list of events")
async def get_events(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Event]:
    """
    Get list of all events with pagination
    """
    return await event_service.get_all(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/camera/{camera_id}", response_model=PaginatedResult[Event], summary="Get list of events by camera")
async def get_events_by_camera(
    camera_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Event]:
    """
    Get list of all events for a specific camera with pagination
    """
    try:
        return await event_service.get_all_by_camera(
            db, camera_id=camera_id, skip=pagination.skip, limit=pagination.limit
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/video/{video_id}", response_model=PaginatedResult[Event], summary="Get list of events by video")
async def get_events_by_video(
    video_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Event]:
    """
    Get list of all events for a specific video with pagination
    """
    try:
        return await event_service.get_all_by_video(
            db, video_id=video_id, skip=pagination.skip, limit=pagination.limit
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/type/{event_type}", response_model=PaginatedResult[Event], summary="Get list of events by type")
async def get_events_by_type(
    event_type: str,
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Event]:
    """
    Get list of all events of a specific type with pagination
    """
    return await event_service.get_all_by_type(
        db, event_type=event_type, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/date-range", response_model=PaginatedResult[Event], summary="Get list of events by date range")
async def get_events_by_date_range(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)],
    pagination: Annotated[PaginationParams, Depends()],
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    camera_id: Optional[int] = Query(None),
    event_type: Optional[str] = Query(None)
) -> PaginatedResult[Event]:
    """
    Get list of all events for a specific period with pagination
    """
    try:
        return await event_service.get_all_by_date_range(
            db, 
            start_date=start_date, 
            end_date=end_date, 
            camera_id=camera_id,
            event_type=event_type,
            skip=pagination.skip, 
            limit=pagination.limit
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/stats", response_model=EventStats, summary="Get statistics for events")
async def get_event_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> EventStats:
    """
    Get statistics for events
    """
    return await event_service.get_stats(db)


@router.get("/{event_id}", response_model=Event, summary="Get event by ID")
async def get_event(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> Event:
    """
    Get event by ID
    """
    event = await event_service.get_by_id(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.get("/{event_id}/with-objects", response_model=EventWithObjects, summary="Get event with objects")
async def get_event_with_objects(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> EventWithObjects:
    """
    Get event with objects by ID
    """
    event = await event_service.get_with_objects(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.get("/{event_id}/with-camera", response_model=EventWithCamera, summary="Get event with camera")
async def get_event_with_camera(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> EventWithCamera:
    """
    Get event with camera by ID
    """
    event = await event_service.get_with_camera(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.get("/{event_id}/with-video", response_model=EventWithVideo, summary="Get event with video")
async def get_event_with_video(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> EventWithVideo:
    """
    Get event with video by ID
    """
    event = await event_service.get_with_video(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.get("/{event_id}/full", response_model=EventFull, summary="Get event with full information")
async def get_event_full(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> EventFull:
    """
    Get event with full information by ID
    """
    event = await event_service.get_full(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.get("/{event_id}/objects", response_model=PaginatedResult[Object], summary="Get event objects")
async def get_event_objects(
    event_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Object]:
    """
    Get objects for a specific event with pagination
    """
    event = await event_service.get_by_id(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return await object_service.get_all_by_event(
        db, event_id=event_id, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/{event_id}/frame", summary="Get event frame")
async def get_event_frame(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> FileResponse:
    """
    Get event frame by ID
    """
    event = await event_service.get_by_id(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if not event.frame_path or not os.path.exists(event.frame_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frame not found"
        )
    
    return FileResponse(
        path=event.frame_path,
        media_type="image/jpeg"
    )


@router.post("/", response_model=EventWithObjects, status_code=status.HTTP_201_CREATED, summary="Create new event")
async def create_event(
    event_in: EventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentEventManager)]
) -> EventWithObjects:
    """
    Create new event
    (requires events.manage permission)
    """
    try:
        return await event_service.create(db, event_in=event_in)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/ai-detection", response_model=EventWithObjects, status_code=status.HTTP_201_CREATED, summary="Process AI detection result")
async def process_ai_detection(
    detection: AIDetectionResult,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentEventManager)]
) -> EventWithObjects:
    """
    Process AI detection result
    (requires events.manage permission)
    """
    try:
        return await event_service.process_ai_detection(db, detection=detection)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/upload-frame", response_model=str, status_code=status.HTTP_201_CREATED, summary="Upload event frame")
async def upload_event_frame(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentEventManager)],
    file: UploadFile = File(...),
    event_id: int = Form(...)
) -> str:
    """
    Upload event frame
    (requires events.manage permission)
    """
    event = await event_service.get_by_id(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Create folder for storing frames if it doesn't exist
    upload_dir = os.path.join("uploads", "frames")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create path to file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"event_{event_id}_{timestamp}.jpg"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        contents = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        event_update = EventUpdate(frame_path=file_path)
        await event_service.update(db, id=event_id, event_in=event_update)
        
        return file_path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.put("/{event_id}/confirm", response_model=Event, summary="Confirm event")
async def confirm_event(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentEventManager)],
    is_confirmed: bool = Form(...)
) -> Event:
    """
    Confirm event (is_confirmed = true) or cancel confirmation (is_confirmed = false)
    (requires events.manage permission)
    """
    event = await event_service.update_confirmed_status(db, id=event_id, is_confirmed=is_confirmed)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.put("/{event_id}/false-positive", response_model=Event, summary="Mark event as false positive")
async def mark_event_as_false_positive(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentEventManager)],
    is_false_positive: bool = Form(...)
) -> Event:
    """
    Mark event as false positive (is_false_positive = true) or cancel mark (is_false_positive = false)
    (requires events.manage permission)
    """
    event = await event_service.update_false_positive_status(
        db, id=event_id, is_false_positive=is_false_positive
    )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.put("/{event_id}", response_model=Event, summary="Update event")
async def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentEventManager)]
) -> Event:
    """
    Update event by ID
    (requires events.manage permission)
    """
    try:
        event = await event_service.update(db, id=event_id, event_in=event_in)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        return event
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete event")
async def delete_event(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentEventManager)]
) -> None:
    """
    Delete event by ID
    (requires events.manage permission)
    """
    deleted = await event_service.delete(db, id=event_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        ) 