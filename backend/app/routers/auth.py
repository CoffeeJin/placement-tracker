from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, security
from app.deps import get_current_user
from app.mailer import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if user.is_active == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been disabled, or its email has not been verified yet")

    token, expire = security.create_access_token(user.id, user.role.value)
    return schemas.TokenResponse(access_token=token, expires_at=expire)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username is already taken")
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = models.User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=security.hash_password(payload.password),
        role=models.UserRole.student,
        is_active=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = security.create_email_verification_token(user.id)
    try:
        send_verification_email(user.email, user.full_name, token)
    except Exception:
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=502, detail="Failed to send verification email, please try again later")

    return schemas.MessageResponse(message="Verification email sent, please check your inbox")


@router.post("/verify-email", response_model=schemas.MessageResponse)
def verify_email(payload: schemas.VerifyEmailRequest, db: Session = Depends(get_db)):
    try:
        token_payload = security.decode_email_verification_token(payload.token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user = db.query(models.User).filter(models.User.id == token_payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user.is_active = 1
    db.commit()
    return schemas.MessageResponse(message="Email verified successfully, you can now log in")
