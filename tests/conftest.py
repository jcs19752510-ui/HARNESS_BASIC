import os

# src.config가 임포트되기 전에 테스트용 환경변수를 확정한다. setdefault가 아니라
# 강제 대입이다 — ambient 환경(예: 쉘 프로필/CI 시크릿에 SESSION_COOKIE_SECURE=true가
# 이미 있는 경우)에 따라 테스트가 조용히 달라지는 것을 막기 위함 (코드리뷰에서 발견).
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SESSION_SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["SESSION_COOKIE_SECURE"] = "false"  # 테스트는 HTTPS가 아니므로 완화

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.auth.security import hash_password
from src.db import Base, get_db, make_engine
from src.main import app
from src.models.user import User, UserRole


@pytest.fixture()
def db_session():
    # src/db.py의 make_engine()을 재사용 — connect_args 설정이 중복/불일치되지 않게
    engine = make_engine("sqlite:///:memory:", poolclass=StaticPool)
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
