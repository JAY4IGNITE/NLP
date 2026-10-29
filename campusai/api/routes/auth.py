"""
Authentication endpoints: login, token issuance, user profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from campusai.api.dependencies import (
    create_access_token, get_current_user, get_db, verify_password
)
from campusai.api.schemas import LoginRequest, TokenResponse, UserOut
from campusai.database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == creds.username).first()
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username, "role": user.role, "uid": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role
    )


@router.post("/logout")
def logout():
    return {"message": "Successfully logged out."}
