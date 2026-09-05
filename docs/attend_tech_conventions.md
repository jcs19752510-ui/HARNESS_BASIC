# 학생 출결 등록 프로그램 — 전역 기술 컨벤션

> `harness/harness_13_tech_conventions.md` 템플릿의 프로젝트 적용본입니다. `harness/`
> 아래 템플릿 자체는 도메인 중립을 유지하고, 실제 확정값은 이 문서(`docs/attend_tech_conventions.md`)에
> 기록합니다. A1에서 이미 내려진 기술 결정을 소급 반영했고, 하네스 리뷰(2026-09-04)에서
> 발견된 CSRF/쿠키 보안 정책 공백을 함께 채웠습니다. A2부터 모든 단위 TRD §1/§2/§4는
> 이 문서를 참조합니다.

---

## §1. 기술 스택
- 언어/프레임워크: Python, FastAPI
- 템플릿 렌더링: Jinja2 (서버사이드 렌더링, SPA 아님)
- ORM: SQLAlchemy
- 데이터베이스: PostgreSQL (NeonDB 관리형)
- 비밀번호 해시: bcrypt
- 세션: 서명된 쿠키(itsdangerous `URLSafeTimedSerializer` 직접 사용) — 별도 세션 테이블 없음.
  Starlette의 `SessionMiddleware` 클래스는 사용하지 않는다 — CSRF 토큰 발급/검증과
  "활동 시 자동 연장"(슬라이딩 만료)을 자체 미들웨어(`SessionRenewalMiddleware`)로
  결합해야 해서 커스텀 구현으로 확정 (A1 실제 구현 시 결정, 하네스 원칙 6에 따라
  이전 표기와의 편차를 기록함)
- 테스트: pytest
- 관련 ADR: `docs/attend_adr.md`의 ADR-003(인증방식), ADR-004(비밀번호저장)

## §2. API 설계 표준
- URL 네이밍: 리소스 중심 경로(`/login`, `/students`, `/classes` 등). 서버사이드 폼
  제출 구조이므로 브라우저가 지원하는 GET/POST만 사용하고, PUT/PATCH/DELETE에
  대응하는 동작은 `/students/{id}/delete`처럼 액션 경로 + POST로 구현한다.
- HTTP 메서드: GET(조회/폼 렌더링), POST(생성·수정·상태변경 전부)
- 요청/응답 공통 포맷: 기본은 HTML(Jinja2 렌더링). JSON 응답이 필요한 엔드포인트는
  `{"data": ..., "error": null}` / 실패 시 `{"data": null, "error": {"code": "...", "message": "..."}}`
  형식을 따른다.
- 에러 응답 공통 포맷: 위 JSON 포맷을 그대로 따름. 모든 단위 TRD §4(상태/에러 코드)는
  이 포맷을 전제로 작성한다.
- 버저닝 정책: 현재 단일 버전, 별도 버전 접두사 없음. 외부 API 클라이언트가 생기면
  `harness_12` 변경관리 절차로 재검토.

## §3. 인증/인가 공통 방식
- 인증 방식: 서명된 쿠키 기반 세션 (ADR-003). JWT 미사용.
- **세션 쿠키 보안 속성 (ADR-007):** `HttpOnly=true`, `Secure=true`(운영 기본값,
  로컬 개발만 환경변수로 끌 수 있음), `SameSite=Lax`. 모든 단위 TRD의 로그인/세션
  관련 AC는 이 속성 검증을 포함해야 한다.
- **CSRF 방어 (ADR-006):** 로그인 이후 모든 상태변경 요청(POST)에 세션 바인딩
  CSRF 토큰을 hidden form field로 발급/검증한다(Synchronizer Token 방식). 로그인
  폼 자체(미인증 상태)는 대상에서 제외한다.
- 권한/역할 구조: `users.role` 4단계(관리자/담임교사/임원교사/교역자). 반(class)
  단위 접근 제한 없음 — 역할은 "어떤 화면/기능에 접근 가능한가"만 가른다
  (`docs/attend_requirements_summary.md` §2). 모든 단위 TRD §0-1 "권한" 항목은
  이 구조를 참조한다.

## §4. 코딩 컨벤션
- 네이밍: 변수/함수 `snake_case`, 클래스 `PascalCase`, 파일명 `snake_case`
- 디렉토리 구조(권장): `src/models`(SQLAlchemy 모델), `src/routes`(엔드포인트),
  `src/auth`(세션/CSRF/인증 미들웨어 — 단위 간 재사용), `src/templates`(Jinja2),
  `src/static`, `tests/`(pytest)
  > 저장소 루트에 이미 `test`라는 이름의 파일이 존재해 `test/` 디렉토리와 이름이
  > 충돌한다(하네스 리뷰 중 발견 — 내용은 이 프로젝트와 무관한 스크래치로 보임,
  > 삭제 여부는 사람 확인 필요이므로 손대지 않음). 충돌을 피하기 위해 테스트
  > 디렉토리명은 `tests/`로 확정한다.
- 주석/문서화 규칙: 프로젝트 루트 `CLAUDE.md`의 전역 규칙(WHY만 기록, 자명한 내용
  주석 금지)을 그대로 따른다.

## §5. 로깅/에러 처리 표준
- 로그 포맷/레벨 세부 규칙: A2 이후 실제 구현 과정에서 확정(현재 미결).
- **개인정보 로그 금지 규칙 (필수):** 비밀번호(해시 포함), 세션 토큰 원문, 학생/보호자
  연락처는 어떤 로그 레벨·어떤 예외 스택트레이스에서도 남기지 않는다. 에러 로깅
  유틸은 이 값들을 자동 마스킹하거나 애초에 로그 대상에서 제외하도록 구현한다.

## §6. 커밋/PR 컨벤션
- `harness_05 §1`의 브랜치/커밋 규칙을 그대로 따른다 (여기서 중복 정의하지 않음).

## §7. 확정 이력
| 항목 | 확정 시점 | 근거 |
|---|---|---|
| §1 기술스택 | 2026-09-03 (A1) | `docs/trd/attend_a1_trd.md` |
| §3 CSRF/쿠키 보안 속성 | 2026-09-04 (하네스 리뷰) | `docs/attend_adr.md` ADR-006, ADR-007 — A1 구현 착수 전 재확인 권장 |
