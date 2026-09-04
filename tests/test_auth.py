"""docs/trd/attend_a1_trd.md §6 테스트 시나리오 → AC-1~AC-11 대응"""

import re

from src.auth.session import SESSION_COOKIE_NAME

VALID_PASSWORD = "Passw0rd!"


def _extract_csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "csrf_token hidden field가 렌더링된 페이지에 없습니다"
    return match.group(1)


def test_ac1_login_success_sets_cookie_and_redirects_to_main(client, active_user):
    resp = client.post(
        "/login",
        data={"username": "teacher001", "password": VALID_PASSWORD},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["location"] == "/"
    assert SESSION_COOKIE_NAME in resp.cookies


def test_ac2_wrong_password_returns_generic_error(client, active_user):
    resp = client.post("/login", data={"username": "teacher001", "password": "wrong-password"})
    assert resp.status_code == 401
    assert "아이디 또는 비밀번호가 올바르지 않습니다" in resp.text


def test_ac3_nonexistent_username_returns_same_generic_error(client):
    resp = client.post("/login", data={"username": "ghost", "password": "whatever"})
    assert resp.status_code == 401
    assert "아이디 또는 비밀번호가 올바르지 않습니다" in resp.text


def test_ac4_inactive_account_rejected_with_same_message(client, inactive_user):
    resp = client.post("/login", data={"username": "retired001", "password": VALID_PASSWORD})
    assert resp.status_code == 401
    assert "아이디 또는 비밀번호가 올바르지 않습니다" in resp.text


def test_ac5_password_never_stored_in_plaintext(active_user):
    assert active_user.password_hash != VALID_PASSWORD
    assert active_user.password_hash.startswith(("$2a$", "$2b$", "$2y$"))


def test_ac6_session_expires_after_max_age(client, active_user, monkeypatch):
    from src import config as config_module

    login_resp = client.post(
        "/login",
        data={"username": "teacher001", "password": VALID_PASSWORD},
        follow_redirects=False,
    )
    cookie_value = login_resp.cookies.get(SESSION_COOKIE_NAME)

    # 30분 경과를 흉내내기 위해 세션 유효기간을 강제로 음수로 설정 → 즉시 만료 취급
    monkeypatch.setattr(config_module, "SESSION_MAX_AGE_SECONDS", -1)

    client.cookies.set(SESSION_COOKIE_NAME, cookie_value)
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/login"


def test_ac7_unauthenticated_access_redirects_to_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/login"


def test_ac8_no_lockout_after_repeated_failures(client, active_user):
    for _ in range(10):
        resp = client.post("/login", data={"username": "teacher001", "password": "wrong"})
        assert resp.status_code == 401

    ok_resp = client.post(
        "/login",
        data={"username": "teacher001", "password": VALID_PASSWORD},
        follow_redirects=False,
    )
    assert ok_resp.status_code == 302


def test_ac9_logout_invalidates_session(client, active_user):
    client.post("/login", data={"username": "teacher001", "password": VALID_PASSWORD})

    home_resp = client.get("/")
    assert home_resp.status_code == 200
    csrf_token = _extract_csrf(home_resp.text)

    logout_resp = client.post("/logout", data={"csrf_token": csrf_token}, follow_redirects=False)
    assert logout_resp.status_code == 302
    assert logout_resp.headers["location"] == "/login"

    after_resp = client.get("/", follow_redirects=False)
    assert after_resp.status_code == 302
    assert after_resp.headers["location"] == "/login"


def test_ac10_session_cookie_security_attributes(client, active_user):
    resp = client.post(
        "/login",
        data={"username": "teacher001", "password": VALID_PASSWORD},
        follow_redirects=False,
    )
    set_cookie_header = resp.headers.get("set-cookie", "")
    assert "httponly" in set_cookie_header.lower()
    assert "samesite=lax" in set_cookie_header.lower()
    # Secure는 SESSION_COOKIE_SECURE 환경변수에 따르며, 테스트 환경(HTTP)에서는
    # docs/attend_env_setup.md 안내대로 false로 완화되어 있어 여기서는 검증하지 않는다.
    # 운영 기본값(true)은 src/config.py의 기본값으로 보장된다.


def test_ac11_state_changing_request_without_csrf_token_is_rejected(client, active_user):
    client.post("/login", data={"username": "teacher001", "password": VALID_PASSWORD})

    resp = client.post("/logout", data={})
    assert resp.status_code == 403

    still_logged_in = client.get("/", follow_redirects=False)
    assert still_logged_in.status_code == 200
