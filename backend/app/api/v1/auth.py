from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.config import settings
from app.models.database import User, Base
from app.models.schemas import UserRegister, UserLogin, UserResponse, Token, TokenData, DeviceOnboardingRequest
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets
import logging
import os
import shutil
from pathlib import Path
from PIL import Image
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create verification token
    verification_token = secrets.token_urlsafe(32)
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    trial_end = datetime.utcnow() + timedelta(days=14)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires=verification_expires,
        plan='trial',
        trial_start_date=datetime.utcnow(),
        trial_end_date=trial_end
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Send verification email (don't fail registration if email fails)
    try:
        from app.services.email_service import email_service
        email_service.send_verification_email(
            new_user.email,
            new_user.username,
            verification_token
        )
        logger.info(f"Verification email sent to {new_user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {new_user.email}: {e}")
        # Don't fail registration if email fails
    
    logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        is_verified=new_user.is_verified,
        plan=new_user.plan,
        profile_picture=new_user.profile_picture,
        trial_start_date=new_user.trial_start_date.isoformat() if new_user.trial_start_date else None,
        trial_end_date=new_user.trial_end_date.isoformat() if new_user.trial_end_date else None,
        solar_provider=new_user.solar_provider,
        battery_type=new_user.battery_type
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    # OAuth2PasswordRequestForm uses 'username' field for both email and username
    # Try email first, then username
    user = get_user_by_email(db, form_data.username) or get_user_by_username(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_verified=current_user.is_verified,
        plan=current_user.plan,
        profile_picture=current_user.profile_picture,
        trial_start_date=current_user.trial_start_date.isoformat() if current_user.trial_start_date else None,
        trial_end_date=current_user.trial_end_date.isoformat() if current_user.trial_end_date else None,
        solar_provider=current_user.solar_provider,
        battery_type=current_user.battery_type
    )

@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload or update user profile picture"""
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.PROFILE_PICTURE_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix or '.jpg'
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = upload_dir / filename
    
    try:
        # Save original file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Process and resize image
        img = Image.open(file_path)
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to max 400x400 while maintaining aspect ratio
        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Save processed image
        img.save(file_path, "JPEG", quality=85, optimize=True)
        
        # Delete old profile picture if exists
        if current_user.profile_picture:
            # Extract filename from path (e.g., "/api/v1/auth/profile-picture/filename.jpg")
            old_filename = Path(current_user.profile_picture).name
            old_path = upload_dir / old_filename
            if old_path.exists() and old_path.is_file():
                try:
                    old_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete old profile picture: {e}")
        
        # Update user record
        relative_path = f"/api/v1/auth/profile-picture/{filename}"
        current_user.profile_picture = relative_path
        db.commit()
        
        logger.info(f"Profile picture uploaded for user {current_user.id}: {filename}")
        
        return {
            "message": "Profile picture uploaded successfully",
            "profile_picture": relative_path
        }
    
    except Exception as e:
        # Clean up file if something went wrong
        if file_path.exists():
            file_path.unlink()
        logger.error(f"Error uploading profile picture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture"
        )

@router.get("/profile-picture/{filename}")
async def get_profile_picture(filename: str):
    """Get profile picture by filename"""
    file_path = Path(settings.PROFILE_PICTURE_DIR) / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture not found"
        )
    
    return FileResponse(
        file_path,
        media_type="image/jpeg",
        filename=filename
    )

@router.delete("/profile-picture")
async def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user's profile picture"""
    if not current_user.profile_picture:
        return {"message": "No profile picture to delete"}
    
    # Extract filename from path
    filename = Path(current_user.profile_picture).name
    file_path = Path(settings.PROFILE_PICTURE_DIR) / filename
    
    # Delete file
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete profile picture file: {e}")
    
    # Update user record
    current_user.profile_picture = None
    db.commit()
    
    return {"message": "Profile picture deleted successfully"}

@router.post("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    
    logger.info(f"User email verified: {user.email}")
    
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(email: str, db: Session = Depends(get_db)):
    """Resend verification email"""
    user = get_user_by_email(db, email)
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a verification link has been sent"}
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Generate new token
    verification_token = secrets.token_urlsafe(32)
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    user.verification_token = verification_token
    user.verification_token_expires = verification_expires
    db.commit()
    
    # Send email
    from app.services.email_service import email_service
    email_service.send_verification_email(user.email, user.username, verification_token)
    
    return {"message": "Verification email sent"}

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Request password reset"""
    user = get_user_by_email(db, email)
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    user.reset_token = reset_token
    user.reset_token_expires = reset_expires
    db.commit()
    
    # Send email
    from app.services.email_service import email_service
    email_service.send_password_reset_email(user.email, user.username, reset_token)
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password with token"""
    user = db.query(User).filter(User.reset_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    logger.info(f"Password reset for user: {user.email}")
    
    return {"message": "Password reset successfully"}

@router.post("/onboard-device/{user_id}", response_model=UserResponse)
async def onboard_device(
    user_id: int,
    device_data: DeviceOnboardingRequest,
    db: Session = Depends(get_db)
):
    """Update user device preferences (solar provider and battery type)"""
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate solar provider
    valid_solar_providers = ['Tata Power Solar', 'Adani Solar', 'Loom Solar']
    if device_data.solar_provider not in valid_solar_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid solar provider. Must be one of: {', '.join(valid_solar_providers)}"
        )
    
    # Validate battery type
    valid_battery_types = ['Exide', 'Luminous', 'Amaron']
    if device_data.battery_type not in valid_battery_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid battery type. Must be one of: {', '.join(valid_battery_types)}"
        )
    
    # Update user device preferences
    user.solar_provider = device_data.solar_provider
    user.battery_type = device_data.battery_type
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(user)
        logger.info(f"Device onboarded for user {user_id}: {device_data.solar_provider} + {device_data.battery_type}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating device preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device preferences"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_verified=user.is_verified,
        plan=user.plan,
        profile_picture=user.profile_picture,
        trial_start_date=user.trial_start_date.isoformat() if user.trial_start_date else None,
        trial_end_date=user.trial_end_date.isoformat() if user.trial_end_date else None,
        solar_provider=user.solar_provider,
        battery_type=user.battery_type
    )

