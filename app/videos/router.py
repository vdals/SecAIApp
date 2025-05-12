import os
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, CurrentVideoManager, CurrentSuperuser
from app.common.schemas import PaginatedResult, PaginationParams
from app.common.utils import NotFoundException
from app.db.session import get_db
from app.users.models import User
from app.videos.schemas import (
    Video, VideoCreate, VideoUpdate, VideoWithCamera, VideoWithEvents, VideoFull,
    VideoProcessStatus, VideoUpload
)
from app.videos.service import VideoService

router = APIRouter(prefix="/videos", tags=["videos"])

video_service = VideoService()


@router.get("/", response_model=PaginatedResult[Video], summary="Get list of videos")
async def get_videos(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Video]:
    """
    Get list of all videos with pagination
    """
    return await video_service.get_all(
        db, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/camera/{camera_id}", response_model=PaginatedResult[Video], summary="Get list of videos by camera")
async def get_videos_by_camera(
    camera_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> PaginatedResult[Video]:
    """
    Get list of all videos for a specific camera with pagination
    """
    try:
        return await video_service.get_all_by_camera(
            db, camera_id=camera_id, skip=pagination.skip, limit=pagination.limit
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/date-range", response_model=PaginatedResult[Video], summary="Get list of videos by date")
async def get_videos_by_date_range(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)],
    pagination: Annotated[PaginationParams, Depends()],
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    camera_id: Optional[int] = Query(None)
) -> PaginatedResult[Video]:
    """
    Get list of all videos for a specific date range with pagination
    """
    try:
        return await video_service.get_by_date_range(
            db, 
            start_date=start_date, 
            end_date=end_date, 
            camera_id=camera_id,
            skip=pagination.skip, 
            limit=pagination.limit
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/latest/camera/{camera_id}", response_model=List[Video], summary="Get latest videos by camera")
async def get_latest_videos_by_camera(
    camera_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)],
    limit: int = Query(5, ge=1, le=20)
) -> List[Video]:
    """
    Get latest videos for a specific camera
    """
    try:
        return await video_service.get_latest_by_camera(
            db, camera_id=camera_id, limit=limit
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{video_id}", response_model=Video, summary="Get video by ID")
async def get_video(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> Video:
    """
    Get video by ID
    """
    video = await video_service.get_by_id(db, id=video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return video


@router.get("/{video_id}/with-camera", response_model=VideoWithCamera, summary="Get video with camera information")
async def get_video_with_camera(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> VideoWithCamera:
    """
    Get video with camera information by ID
    """
    video = await video_service.get_with_camera(db, id=video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return video


@router.get("/{video_id}/with-events", response_model=VideoWithEvents, summary="Get video with events information")
async def get_video_with_events(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> VideoWithEvents:
    """
    Get video with events information by ID
    """
    video = await video_service.get_with_events(db, id=video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return video


@router.get("/{video_id}/full", response_model=VideoFull, summary="Get video with full information")
async def get_video_full(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentUser)]
) -> VideoFull:
    """
    Get video with full information by ID
    """
    video = await video_service.get_full(db, id=video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return video


@router.get("/{video_id}/download", summary="Download video file")
async def download_video(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(CurrentUser)]
) -> FileResponse:
    """
    Download video file by ID
    """
    video = await video_service.get_by_id(db, id=video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if not os.path.exists(video.filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found"
        )
    
    return FileResponse(
        path=video.filepath,
        filename=video.filename,
        media_type="video/mp4"  # or other corresponding type
    )


@router.post("/", response_model=VideoFull, status_code=status.HTTP_201_CREATED, summary="Create new video record")
async def create_video(
    video_in: VideoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentVideoManager)]
) -> VideoFull:
    """
    Create new video record
    (requires videos.manage permission)
    """
    try:
        return await video_service.create(db, video_in=video_in)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/upload", response_model=Video, status_code=status.HTTP_201_CREATED, summary="Upload video file")
async def upload_video(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentVideoManager)],
    file: UploadFile = File(...),
    camera_id: int = Form(...),
    recording_start: Optional[datetime] = Form(None),
    recording_end: Optional[datetime] = Form(None)
) -> Video:
    """
    Upload video file
    (requires videos.manage permission)
    """
    # Create folder for storing videos if it doesn't exist
    upload_dir = os.path.join("uploads", "videos")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create path to file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Create video record
        upload_info = VideoUpload(
            camera_id=camera_id,
            recording_start=recording_start,
            recording_end=recording_end
        )
        
        return await video_service.handle_upload(
            db, file_path=file_path, file_size=file_size, upload_info=upload_info
        )
    except NotFoundException as e:
        # Delete file if an error occurred
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Delete file if an error occurred
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.put("/{video_id}/status", response_model=Video, summary="Update video processing status")
async def update_video_status(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentVideoManager)],
    status: str = Form(...)
) -> Video:
    """
    Update video processing status
    (requires videos.manage permission)
    """
    video = await video_service.update_processing_status(db, id=video_id, status=status)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return video


@router.put("/{video_id}/analysis", response_model=Video, summary="Update video analysis status")
async def update_video_analysis_status(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentVideoManager)],
    is_analyzed: bool = Form(...)
) -> Video:
    """
    Update video analysis status
    (requires videos.manage permission)
    """
    video = await video_service.update_analysis_status(db, id=video_id, is_analyzed=is_analyzed)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return video


@router.put("/{video_id}", response_model=VideoFull, summary="Update video")
async def update_video(
    video_id: int,
    video_in: VideoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentVideoManager)]
) -> VideoFull:
    """
    Update video by ID
    (requires videos.manage permission)
    """
    try:
        video = await video_service.update(db, id=video_id, video_in=video_in)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        return video
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete video")
async def delete_video(
    video_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(CurrentVideoManager)],
    delete_file: bool = Query(False)
) -> None:
    """
    Delete video by ID
    (requires videos.manage permission)
    """
    deleted = await video_service.delete(db, id=video_id, delete_file=delete_file)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        ) 