from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    # The first 12 chars of the raw key (after the "sk_live_" prefix) are stored
    # in plaintext and used as the DB primary key. The remainder is hashed.
    # This lets us look up by prefix in O(1) and then verify the secret with argon2.
    # Same pattern Stripe uses.
    id: Mapped[str] = mapped_column(String(12), primary_key=True)

    hashed_secret: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None
