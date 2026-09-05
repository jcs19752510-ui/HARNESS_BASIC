# 학생 출결 등록 프로그램 — 데이터 모델(ERD) 초안

> harness_01_trd_template.md §1(데이터 구조)의 입력이 되는 상위 설계 문서입니다.
> ⚠️ 이 문서는 초안입니다. §5 "확정 필요 항목"에 답하신 뒤 최종본으로 반영됩니다.
>
> **2026-09-05 갱신**: `contact_view_log` 테이블 추가 (`docs/attend_adr.md` ADR-008 —
> 학생/보호자 연락처 상세 열람 시 감사 로그 남기기로 결정된 데이터모델 후속 반영,
> 사람 승인 완료). A2(사용자/학생 관리 화면) 구현 시 이 테이블에 INSERT하는 로직 필수.

---

## 1. 테이블 목록 및 설계 근거

### `years` — 연도(기수)
학생/반 배정이 "1년 단위로 전체 바뀜"이라는 요구사항을 반영. 매년 반 편성이
통째로 새로 생기므로, 연도 자체를 하나의 기준 단위로 둡니다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| year | INT | 예: 2026 |
| use_yn | CHAR(1) | 소프트삭제 |

### `classes` — 반
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| year_id | FK → years | 어느 연도의 반인지 |
| name | VARCHAR | 반 이름 |
| use_yn | CHAR(1) | |

### `users` — 교사/관리자 계정
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| username | VARCHAR, UNIQUE | 로그인 아이디 |
| password_hash | VARCHAR | **평문 저장 금지, 해시만 저장** |
| name | VARCHAR | |
| role | ENUM | 관리자 / 담임교사 / 임원교사 / 교역자 |
| use_yn | CHAR(1) | |

### `class_teachers` — 반-교사 배정 (다대다)
"같은 반에 담임+보조교사 등 여러 명 가능"을 반영하기 위한 중간 테이블.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| class_id | FK → classes | |
| user_id | FK → users | |
| use_yn | CHAR(1) | |

### `students` — 학생 기본 정보
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | 시스템 내부 고유값 (동명이의 구분은 이 PK로 자동 해결) |
| student_no | VARCHAR, UNIQUE | 화면에 노출되는 학번(자동 생성, 순번 방식) |
| name | VARCHAR | |
| gender | ENUM | |
| grade | VARCHAR | 학년 |
| photo_path | VARCHAR | 업로드된 사진 파일 경로 (jpg/png, 서버/스토리지에 저장) |
| contact | VARCHAR | 학생 연락처 |
| guardian_contact | VARCHAR | 학부모 연락처 |
| note | TEXT | 특이사항 |
| use_yn | CHAR(1) | |

### `contact_view_log` — 학생/보호자 연락처 열람 이력 (감사 추적)
`docs/attend_adr.md` ADR-008(2026-09-05)에 따라, 목록 화면에서는 연락처를 마스킹하고
상세 화면에서 전체 번호를 열람할 때마다 아래 이력을 남깁니다. `attendance_history`와
같은 목적(감사 추적)의 별도 테이블입니다 — 물리 삭제 없음, 파기는 `harness_10`/
`docs/attend_data_lifecycle.md`의 3년 보존 정책을 따릅니다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| student_id | FK → students | 열람 대상 학생 |
| viewed_by | FK → users | 열람한 사용자(교사/관리자) |
| viewed_at | TIMESTAMP | 열람 시각 |

**저장 시점:** 학생 상세 화면(A2 등)에서 `contact`/`guardian_contact` 전체 값을 서버가
응답에 포함시키는 매 요청마다 INSERT (조회 자체가 열람이므로 화면 클릭과 무관하게 API
호출 시점 기준).

### `student_class_history` — 학생-반 소속 이력
"1년 단위로 전체 바뀌고, 필요시 반이동 존재"를 반영. 학생의 반 소속을
`students` 테이블에 직접 두지 않고 별도 이력 테이블로 분리합니다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| student_id | FK → students | |
| class_id | FK → classes | |
| start_date | DATE | 이 반 소속 시작일 |
| end_date | DATE, NULL 허용 | 반이동/졸업 시 종료일, 현재 소속이면 NULL |
| use_yn | CHAR(1) | |

**왜 이렇게 분리하는가:** 요구사항 §1에서 "학생 1명 = 반 1개만 소속"이라고
하셨지만, 이는 "동시점 기준"이지 "영구히 고정"이 아닙니다(반이동 있음).
`students` 테이블에 `class_id`를 직접 두면 반이동 이력이 사라지므로,
이력 테이블로 분리해 "현재 소속"과 "과거 소속"을 모두 조회 가능하게 합니다.

### `attendance` — 출결 기록
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| student_id | FK → students | |
| class_id | FK → classes | 등록 시점의 반 (student_class_history와 일관성 유지) |
| attend_date | DATE | 출결 대상 날짜 |
| status | ENUM | 출석 / 결석 / 지각 |
| recorded_by | FK → users | 마지막으로 저장한 사람 |
| use_yn | CHAR(1) | |
| UNIQUE(student_id, attend_date) | | 같은 학생, 같은 날짜 중복 방지 |

### `attendance_history` — 출결 변경 이력 (감사 추적)
"누가/언제/무엇을 바꿨는지 기록 필요"를 반영.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | PK | |
| attendance_id | FK → attendance | |
| old_status | ENUM, NULL 허용 | 최초 생성 시 NULL |
| new_status | ENUM | |
| changed_by | FK → users | |
| changed_at | TIMESTAMP | |

**저장 순서 원칙(동시성 정책 반영):** 저장 API는 `attendance`를 UPSERT하기
직전에, 바뀌기 전 값을 반드시 `attendance_history`에 먼저 기록합니다.
두 교사가 동시에 다르게 입력해도 최종값은 마지막 저장자 것으로 남고,
이전 시도들은 전부 이력에 남아 사후 확인이 가능합니다.

## 2. ERD 관계 요약

```
years 1─N classes 1─N class_teachers N─1 users
classes 1─N student_class_history N─1 students
students 1─N attendance N─1 classes
attendance 1─N attendance_history
users 1─N attendance_history (changed_by)
students 1─N contact_view_log N─1 users (viewed_by)
```

## 3. 요구사항 정의서와의 대응 확인

| 요구사항 | 반영 위치 |
|---|---|
| 교사 반별 일괄 등록 | `attendance`가 `class_id` 보유, 화면에서 반 단위 조회/저장 |
| 출석/결석/지각 3종 | `attendance.status` ENUM |
| 교사/관리자 언제든 수정 가능 | 별도 상태 제약 없음(모든 role이 수정 가능) |
| 학생 1명 = 반 1개(동시점) | `student_class_history`에서 `end_date IS NULL`인 레코드가 항상 1개 |
| 특정 요일만 등록 | 데이터모델엔 제약 없음 — TRD §3(워크플로우)에서 화면 단으로 제어 |
| 동시성(여러 교사) | `attendance_history`로 이력 보존, 저장은 UPSERT |
| 4단계 권한, 전체 반 개방 | `users.role`만으로 판단, class 단위 필터 없음 |
| 감사 추적 | `attendance_history` |
| 연락처 열람 감사(ADR-008) | `contact_view_log` |
| 소프트삭제만 | 전 테이블에 `use_yn`, 물리 DELETE 없음 |

## 4. 아직 다루지 않은 것 (다음 TRD에서 결정)
- 반이동 처리 화면/절차 (student_class_history를 누가 어떻게 갱신하는지)
- 학생 사진 업로드/저장 방식 (스토리지 종류는 기술스택 확정 단계에서)
- 통계/현황 화면 (요구사항 정의서에서 미결로 남김)

## 5. 확정 필요 항목 — 답변 완료, 확정됨

| 항목 | 확정 내용 |
|---|---|
| 학생 사진 | 파일 업로드(jpg/png), 서버/스토리지에 경로 저장 (`students.photo_path`) |
| 학생 고유식별자 | `student_no` 자동 생성(순번 방식) 컬럼 추가 |
| 동명이의 | PK(`id`)로 시스템 내부적으로 항상 구분됨 — 화면 표시는 `student_no` + 이름 병기 권장 |

> 이 섹션이 채워지면서 이 문서는 초안(Draft)에서 확정본으로 전환됩니다.
> 파일명에서 `_draft`를 제거하고 `attend_a0_datamodel_trd.md`로 저장 후
> `docs/trd/`로 이동해 커밋하세요.
