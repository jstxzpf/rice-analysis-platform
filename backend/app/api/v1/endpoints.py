from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud import crud_analysis_result, crud_field, crud_user
from app.db.base import get_db
from app.db.models import User
from app.schemas import analysis_result as ar_schema
from app.schemas import field as field_schema
from app.schemas import user as user_schema
from app.schemas import photogroup as pg_schema
from app.schemas.token import Token

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


# endregion
