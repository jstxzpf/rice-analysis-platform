from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud import crud_analysis_result, crud_field, crud_user, crud_photogroup
from app.db.base import get_db
from app.db.models import User, PhotoGroup, AnalysisResult, Field
from app.schemas import analysis_result as ar_schema
from app.schemas import field as field_schema
from app.schemas import user as user_schema
from app.schemas import photogroup as pg_schema
from app.schemas.token import Token
from app.worker.tasks import run_analysis

from .dependencies import get_current_user, get_current_admin_user

router = APIRouter()
analysis_router = APIRouter()


# region Authentication
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud_user.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }


# endregion


# region User
@router.post("/users/", response_model=user_schema.User, tags=["Users"])
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return crud_user.create_user(db=db, user=user)


@router.get("/users/me", response_model=user_schema.User, tags=["Users"])
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users/", response_model=List[user_schema.User], tags=["Users"])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Retrieve all users. Admin only.
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/password-recovery/{username}", response_model=dict, tags=["Users"])
def recover_password(username: str, db: Session = Depends(get_db)):
    """
    Password Recovery. In a real system, this would send an email.
    For this demo, it generates a token and prints it to the console.
    """
    user = crud_user.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist.",
        )
    user_with_token = crud_user.create_password_reset_token(db, user=user)
    # In a real app, you would send an email with the token.
    print(f"Password reset token for user {username}: {user_with_token.reset_password_token}")
    return {"message": "Password recovery email sent (check console for token)."}


@router.post("/reset-password/", response_model=dict, tags=["Users"])
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
):
    """
    Reset password.
    """
    user = crud_user.get_user_by_password_reset_token(db, token=token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    crud_user.reset_password(db, user=user, new_password=new_password)
    return {"message": "Password updated successfully"}


# endregion


# region Field
@router.post("/fields/", response_model=field_schema.Field, tags=["Fields"])
def create_field(
    field: field_schema.FieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud_field.create_field_for_user(db=db, field=field, owner_id=current_user.id)


@router.get("/fields/", response_model=List[field_schema.Field], tags=["Fields"])
def read_fields(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fields = crud_field.get_fields_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return fields


@router.get("/fields/{field_id}", response_model=field_schema.Field, tags=["Fields"])
def read_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_field = crud_field.get_field(db, field_id=field_id)
    if db_field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    if db_field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_field

@router.get("/fields/{field_id}/results", response_model=List[pg_schema.PhotoGroup], tags=["Fields"])
def read_field_results(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all analysis photo groups for a specific field."""
    results = crud_field.get_field_results(db, field_id=field_id, owner_id=current_user.id)
    return results


@router.put("/fields/{field_id}", response_model=field_schema.Field, tags=["Fields"])
def update_field(
    field_id: int,
    field_update: field_schema.FieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_field = crud_field.get_field(db, field_id=field_id)
    if db_field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    if db_field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_field.update_field(db, field_id=field_id, field_update=field_update)


@router.delete("/fields/{field_id}", response_model=field_schema.Field, tags=["Fields"])
def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_field = crud_field.get_field(db, field_id=field_id)
    if db_field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    if db_field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_field.delete_field(db, field_id=field_id)


# endregion


# region Photo Upload
@router.post("/photogroups/upload", response_model=pg_schema.PhotoGroup, tags=["Photo Groups"])
def upload_photo_group(
    drone_photo: UploadFile = File(...),
    side_photo_05m: UploadFile = File(...),
    side_photo_3m_horizontal: UploadFile = File(...),
    side_photo_3m_vertical: UploadFile = File(...),
    field_id: int = Body(...),
    capture_date: date = Body(...),
    rice_variety: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a set of four photos for analysis:
    - drone_photo: Drone overhead view
    - side_photo_05m: Side view at 0.5m height
    - side_photo_3m_horizontal: Side view at 3m height (horizontal orientation)
    - side_photo_3m_vertical: Side view at 3m height (vertical orientation)
    """
    # Verify that the field belongs to the current user
    db_field = crud_field.get_field(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    if db_field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Save uploaded files
    import os
    from datetime import datetime
    from uuid import uuid4
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filenames to prevent conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid4())[:8]
    
    # Save drone photo
    drone_filename = f"drone_{timestamp}_{unique_id}_{drone_photo.filename}"
    drone_path = os.path.join(upload_dir, drone_filename)
    with open(drone_path, "wb") as buffer:
        buffer.write(drone_photo.file.read())
    
    # Save 0.5m side photo
    side_05m_filename = f"side_05m_{timestamp}_{unique_id}_{side_photo_05m.filename}"
    side_05m_path = os.path.join(upload_dir, side_05m_filename)
    with open(side_05m_path, "wb") as buffer:
        buffer.write(side_photo_05m.file.read())
    
    # Save 3m horizontal side photo
    side_3m_horizontal_filename = f"side_3m_horizontal_{timestamp}_{unique_id}_{side_photo_3m_horizontal.filename}"
    side_3m_horizontal_path = os.path.join(upload_dir, side_3m_horizontal_filename)
    with open(side_3m_horizontal_path, "wb") as buffer:
        buffer.write(side_photo_3m_horizontal.file.read())
    
    # Save 3m vertical side photo
    side_3m_vertical_filename = f"side_3m_vertical_{timestamp}_{unique_id}_{side_photo_3m_vertical.filename}"
    side_3m_vertical_path = os.path.join(upload_dir, side_3m_vertical_filename)
    with open(side_3m_vertical_path, "wb") as buffer:
        buffer.write(side_photo_3m_vertical.file.read())
    
    # Create PhotoGroup record
    photo_group_data = pg_schema.PhotoGroupCreate(
        field_id=field_id,
        capture_date=capture_date,
        rice_variety=rice_variety
    )
    
    db_photo_group = crud_photo_group.create_photo_group(
        db=db,
        photo_group=photo_group_data,
        drone_photo_path=drone_path,
        side_photo_05m_path=side_05m_path,
        side_photo_3m_horizontal_path=side_3m_horizontal_path,
        side_photo_3m_vertical_path=side_3m_vertical_path
    )
    
    # Trigger async analysis task
    task = run_analysis.delay(db_photo_group.id)
    db_photo_group.celery_task_id = task.id
    db.commit()
    
    return db_photo_group


@router.get("/photogroups/status/{task_id}", response_model=dict, tags=["Photo Groups"])
def get_analysis_status(task_id: str):
    """
    Get the status of an analysis task.
    """
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id)
    
    # Return status and any additional result info
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
# endregion


# region Analysis
@analysis_router.get(
    "/results/{result_id}",
    response_model=ar_schema.AnalysisResult,
    tags=["Analysis"],
)
def get_analysis_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a single analysis result by its ID.
    """
    result = crud_analysis_result.get_analysis_result(
        db=db, result_id=result_id, owner_id=current_user.id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    return result


@analysis_router.get(
    "/inter-field-comparison/",
    response_model=List[ar_schema.AnalysisResult],
    tags=["Analysis"],
)
def get_inter_field_comparison(
    period_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve analysis results for all fields for a given period (10 days).
    """
    start_date = period_date - timedelta(days=5)
    end_date = period_date + timedelta(days=4)
    results = crud_analysis_result.get_analysis_results_for_period(
        db=db, owner_id=current_user.id, start_date=start_date, end_date=end_date
    )
    return results


@analysis_router.get(
    "/growth-heatmap/{field_id}",
    response_model=dict,
    tags=["Analysis"],
)
def get_growth_heatmap(
    field_id: int,
    indicator: str = "avg_plant_height",  # 默认指标为株高
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate growth heatmap data for a specific field with spatial coordinates.
    This endpoint simulates spatial data for the heatmap based on analysis results.
    """
    # Verify field ownership
    db_field = crud_field.get_field(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    if db_field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Fetch analysis results for the field
    results = crud_analysis_result.get_analysis_results_for_field(
        db=db, field_id=field_id, start_date=start_date, end_date=end_date
    )
    
    # Generate heatmap data
    heatmap_data = []
    for result in results:
        # Get photo group to access capture date and location info
        photo_group = db.query(PhotoGroup).filter(PhotoGroup.id == result.photo_group_id).first()
        if photo_group:
            # Simulate spatial coordinates (in a real implementation, these would come from GPS data)
            # For demonstration purposes, we'll generate random coordinates with some clustering
            import random
            # Create multiple data points per analysis result to simulate spatial distribution
            for i in range(20):  # Generate 20 points per time point
                x = random.uniform(0, 100)  # Simulated X coordinate (0-100 meters)
                y = random.uniform(0, 100)  # Simulated Y coordinate (0-100 meters)
                
                # Get the value for the selected indicator
                value = getattr(result, indicator, 0) or 0  # Default to 0 if the attribute is None
                
                # Add slight random variation to the value for realistic distribution
                if value:
                    value = max(0, value + random.uniform(-value*0.1, value*0.1))
                
                heatmap_data.append([
                    x,  # x-coordinate
                    y,  # y-coordinate
                    value if value is not None else 0,  # indicator value
                    photo_group.capture_date.isoformat()  # date for time dimension
                ])
    
    return {
        "field_id": field_id,
        "indicator": indicator,
        "heatmap_data": heatmap_data,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None
    }


@analysis_router.get(
    "/regional-differences/{field_id}",
    response_model=dict,
    tags=["Analysis"],
)
def get_regional_differences(
    field_id: int,
    indicator: str = "avg_plant_height",  # 默认指标为株高
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze regional differences within a specific field based on spatial coordinates.
    This endpoint calculates statistics for different regions of the field.
    """
    # Verify field ownership
    db_field = crud_field.get_field(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    if db_field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Fetch analysis results for the field
    results = crud_analysis_result.get_analysis_results_for_field(
        db=db, field_id=field_id, start_date=start_date, end_date=end_date
    )
    
    # Simulate regional analysis by virtually dividing the field into 4 quadrants
    regions = {
        "northeast": {"values": [], "count": 0},
        "northwest": {"values": [], "count": 0},
        "southeast": {"values": [], "count": 0},
        "southwest": {"values": [], "count": 0}
    }
    
    for result in results:
        # Get the value for the selected indicator
        value = getattr(result, indicator, 0) or 0  # Default to 0 if the attribute is None
        
        if value:  # Only process if there's a valid value
            # Randomly assign data points to regions for demonstration
            import random
            region_keys = list(regions.keys())
            selected_region = random.choice(region_keys)
            
            regions[selected_region]["values"].append(value)
            regions[selected_region]["count"] += 1
    
    # Calculate statistics for each region
    regional_stats = {}
    for region_name, data in regions.items():
        if data["count"] > 0:
            values = data["values"]
            regional_stats[region_name] = {
                "average": round(sum(values) / len(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "std_dev": round((sum((x - sum(values) / len(values)) ** 2 for x in values) / len(values)) ** 0.5, 2) if len(values) > 1 else 0,
                "count": data["count"]
            }
        else:
            regional_stats[region_name] = {
                "average": 0,
                "min": 0,
                "max": 0,
                "std_dev": 0,
                "count": 0
            }
    
    # Calculate overall field statistics
    all_values = []
    for data in regions.values():
        all_values.extend(data["values"])
    
    overall_stats = {}
    if all_values:
        overall_stats = {
            "average": round(sum(all_values) / len(all_values), 2),
            "min": round(min(all_values), 2),
            "max": round(max(all_values), 2),
            "std_dev": round((sum((x - sum(all_values) / len(all_values)) ** 2 for x in all_values) / len(all_values)) ** 0.5, 2) if len(all_values) > 1 else 0,
            "count": len(all_values)
        }
    else:
        overall_stats = {
            "average": 0,
            "min": 0,
            "max": 0,
            "std_dev": 0,
            "count": 0
        }
    
    return {
        "field_id": field_id,
        "indicator": indicator,
        "regional_stats": regional_stats,
        "overall_stats": overall_stats,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None
    }


# endregion
