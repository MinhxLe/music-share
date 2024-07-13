import random
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.orm import Session

from core.db.database import get_session
from users.db.models import OtpRequest, User


class Service:
    def __init__(self, db: Session = Depends(get_session)):
        self.db = db

    def create_otp_request(self, user: User, now: datetime) -> OtpRequest:
        with self.db.begin():
            self.db.execute(
                update(OtpRequest)
                .where(OtpRequest.user_id == user.id)
                .values(status=OtpRequest.Status.EXPIRED)
            )
            new_request = OtpRequest(
                user_id=user.id,
                expires_at=now + timedelta(minutes=10),
                status=OtpRequest.Status.PENDING,
                code="".join([str(random.randint(0, 9)) for _ in range(6)]),
            )
        return new_request
