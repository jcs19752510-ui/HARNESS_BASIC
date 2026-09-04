import os

# src.config가 임포트되기 전에 테스트용 환경변수를 먼저 확정한다.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SESSION_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("SESSION_COOKIE_SECURE", "false")  # 테스트는 HTTPS가 아니므로 완화

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.auth.security import hash_password
from src.db import Base, get_db
from src.main import app
from src.models.user import User, UserRole


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def active_user(db_session):
    user = User(
        username="teacher001",
        password_hash=hash_password("Passw0rd!"),
        name="테스트교사",
        role=UserRole.HOMEROOM_TEACHER,
        use_yn="Y",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def inactive_user(db_session):
    user = User(
        username="retired001",
        password_hash=hash_password("Passw0rd!"),
        name="비활성교사",
        role=UserRole.HOMEROOM_TEACHER,
        use_yn="N",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
