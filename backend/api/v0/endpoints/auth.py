from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from models.user import User
from auth import hash_password, verify_password, create_access_token
from api.v0.schemas import user as user_schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=user_schemas.UserResponse)
def register(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Returns:
        - User information if registration successful

    Raises:
        - HTTPException 400 if email or username already exists
    """
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user with hashed password
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=user_schemas.Token)
def login(credentials: user_schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login with username and password.

    Returns:
        - JWT access token

    Raises:
        - HTTPException 401 if credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
