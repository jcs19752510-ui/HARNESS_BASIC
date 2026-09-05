import enum

from sqlalchemy import CHAR, Enum as SAEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class UserRole(str, enum.Enum):
    """docs/trd/attend_a0_datamodel_trd.md users.role 4단계"""

    ADMIN = "관리자"
    HOMEROOM_TEACHER = "담임교사"
    LEAD_TEACHER = "임원교사"
    MINISTER = "교역자"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False,
    )
    # 'N'이면 로그인 차단 (docs/trd/attend_a1_trd.md §1) — 물리삭제 금지, 소프트삭제만 (ADR-001)
    use_yn: Mapped[str] = mapped_column(CHAR(1), nullable=False, default="Y")
