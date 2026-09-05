# 인수인계 문서 (A0 Handoff) — A1 로그인/인증

> `harness/harness_03_handoff_template.md` 양식. 2026-09-05 하네스 감사 중
> 소급 작성 — 원본 세션 트랜스크립트는 보관돼 있지 않아, 실제 커밋 이력
> (`daef148` 외 `feature/a1-login`의 4개 커밋), TRD, ADR, 변경로그를 근거로
> 재구성했습니다 (하네스 원칙 6 — 원본 우선).

## 문서 정보
- 프로젝트: 학생 출결 등록 프로그램 (attendance-app)
- 최종 갱신일: 2026-09-05
- 갱신자: AI 소급 작성 (2026-09-05) — **사람 검증 필요**

## §1. 전체 진행 현황
| 단위 | 상태 | 비고 |
|---|---|---|
| A1 로그인/인증 | 구현 완료, 2026-09-05 PROD에 정식 병합 | AC-1~AC-11 전부 자동 테스트 존재, `pytest -q` 12 passed 확인(2026-09-05) |

## §2. 이번 세션에서 완료된 것 [AI 초안 → 사람 검증]
- 무엇을 만들었는가: FastAPI 기반 로그인/로그아웃, `itsdangerous` 서명 쿠키 세션(30분 슬라이딩 만료), bcrypt 비밀번호 해시, CSRF 토큰 검증 미들웨어, 인증 미들웨어(`require_login`).
- AC 대비 결과: AC-1~AC-11 전부 자동 테스트로 존재하며 전부 pass (`tests/test_auth.py`, 2026-09-05 재확인).
- 코드리뷰 반영 이력(`daef148` 커밋 메시지 원문 기준, 총 7건):
  1. (High) `require_login`이 세션 갱신 쿠키를 라우트 자체 Response에 못 심는 버그 → `SessionRenewalMiddleware`로 이동해 수정
  2. (그 수정이 유발한 2차 버그) 로그아웃 후에도 미들웨어가 세션 재발급 → `logout()`에서 `request.state.session = None` 명시 정리
  3. (Medium) `bcrypt.checkpw` 동기 호출이 이벤트 루프 블로킹 → `run_in_threadpool`로 오프로드
  4. (Medium) CSRF 토큰 비교가 `!=`(타이밍 공격 가능) → `hmac.compare_digest`로 교체
  5. (Medium) `BadSignature`만 캐치해 `BadPayload` 누출 → 공통 상위클래스 `BadData`로 교체
  6. `tests/conftest.py`의 엔진 설정 중복 → `src/db.py`에 `make_engine()` 팩토리 추가
  7. `conftest`의 `os.environ.setdefault`가 ambient 환경변수에 조용히 no-op 될 수 있음 → 강제 대입으로 교체

## §3. 발견된 편차 (TRD/가정과 실제가 다름) [필수 기록]
| 무엇을 가정했는가 | 실제로는 어땠는가 | 어떻게 처리했는가 |
|---|---|---|
| TRD/기술컨벤션이 명시한 "FastAPI SessionMiddleware" 사용 | 실제 구현은 `itsdangerous` 직접 사용 (Starlette `SessionMiddleware` 미사용) — CSRF/슬라이딩 만료 결합 목적의 의도적 선택 | TRD·기술컨벤션 문서 둘 다 정정 완료 (하네스 원칙 6) |
| §4의 로그인 성공 응답 코드 "200" | 구현은 302(리다이렉트) — §2의 "리다이렉트" 서술과 정합성 위해 302로 통일 | TRD §4 갱신, 편차로 기록 |
| "머지 완료"로 표시된 PR #6이 실제로 코드까지 병합했을 것 | PR #6은 TRD/작업지시서 문서만 병합, 소스코드는 `feature/a1-login`에 남아 있다가 해당 브랜치가 원격에서 삭제되어 dangling commit(`daef148`)으로만 존재 — git gc 시 소실 위험 상태였음 | 2026-09-05 감사에서 `git fsck`로 발견, `recovered/a1-login`으로 임시 복구 후 PROD에 정식 `git merge`로 병합. 상세는 `CLAUDE.md` "알려진 실패 패턴" #1, #8 참조 |

## §4. 남은 것 / 다음 세션에서 할 일
- [ ] 마이그레이션 정책 미확정 상태에서 `create_all()`로 스키마 생성 중 — 운영 마이그레이션 전략(Alembic 등) 확정 필요 (별도 ADR 대상, `daef148` 커밋 메시지에서 이미 보류 명시)
- [ ] 로그인 실패 시도 로깅(보안 모니터링용) — TRD §7 미결, 우선순위 낮음
- [ ] 비밀번호 최소 복잡도 규칙 — A2(사용자관리) 착수 시 재확인 예정 (TRD §7)

## §5. 다음 세션 착수 전 반드시 확인할 것
- A2~A6은 전부 이 단위의 세션/인증 미들웨어에 의존한다고 TRD에 명시돼 있음 — 실제로 `src/auth/dependencies.py`의 `require_login`을 import해서 쓰는지 착수 전 확인할 것.
- `.env.example`에 있는 `SESSION_SECRET` 등은 예시값이며, 실제 운영 시크릿은 별도 발급 필요 (`.env`는 `.gitignore`로 제외되어 있어 저장소엔 없음).

## §6. 리스크/미결 정책 (아직 사람의 최종 결정이 안 난 것)
| 항목 | 현재 임시 기본값 | 결정 필요 시점 |
|---|---|---|
| DB 마이그레이션 전략 | `create_all()`로 임시 생성 | A2 착수 전, 또는 운영 배포 전 반드시 확정 (ADR 대상) |
