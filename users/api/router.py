from dataclasses import field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db.database import get_session
from pydantic import BaseModel, validator

from core.utils import phone_utils
from users.db.models import OtpRequest, User

router = APIRouter()


class CreateOtpRequest(BaseModel):
    phone_number: str

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, value):
        return phone_utils.format(value)


class CreateOtpResponse(BaseModel):
    pass


@router.post("/request_otp", response_model=CreateOtpResponse)
def create_otp(
    request: CreateOtpRequest,
    db: Session = Depends(get_session),
):
    # Get or create user with db
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if user is None:
        user = User(phone_number=request.phone_number, status=User.Status.PENDING)
        db.add(user)
        db.commit()
        db.refresh(user)

    return CreateOtpResponse()


@router.post("/verify_otp")
def verify_otp():
    pass
