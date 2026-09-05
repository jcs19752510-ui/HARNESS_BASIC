from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


def make_engine(url: str, **engine_kwargs):
    """단일 지점에서 엔진 설정을 관리 — tests/conftest.py도 이 함수를 재사용한다
    (코드리뷰에서 중복 발견: 테스트가 connect_args를 따로 하드코딩하고 있었음)."""
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, **engine_kwargs)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
