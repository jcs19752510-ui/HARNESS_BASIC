# 인수인계 문서 (A0 Handoff) — 데이터 모델(ERD)

> `harness/harness_03_handoff_template.md` 양식. 2026-09-05 하네스 감사 중
> 소급 작성 — 원본 세션 트랜스크립트가 보관되지 않아, 실제 커밋된
> `docs/trd/attend_a0_datamodel_trd.md`·`docs/attend_adr.md`·`docs/attend_change_log.md`를
> 근거로 재구성했습니다 (하네스 원칙 6 — 원본 우선).

## 문서 정보
- 프로젝트: 학생 출결 등록 프로그램 (attendance-app)
- 최종 갱신일: 2026-09-05
- 갱신자: AI 소급 작성 (2026-09-05) — **사람 검증 필요**

## §1. 전체 진행 현황
| 단위 | 상태 | 비고 |
|---|---|---|
| A0 데이터 모델(ERD) | 확정 | `docs/trd/attend_a0_datamodel_trd.md` §5 확정 완료 |
| A1 로그인/인증 | 구현 완료(코드리뷰 반영 포함), 2026-09-05에 base 브랜치(PROD)로 정식 병합 | 별도 `attend_a1_handoff.md` 참조 |
| A2~A6 | 미착수 | 마스터 TRD상 화면 목록만 존재 |

## §2. 이번 세션에서 완료된 것 [AI 초안 → 사람 검증]
- 무엇을 만들었는가: `years / classes / users / class_teachers / students / student_class_history / attendance / attendance_history` 8개 테이블 ERD 확정. 반이동 이력 분리(`student_class_history`), 출결 변경 감사 이력(`attendance_history`), 전 테이블 소프트삭제(`use_yn`) 원칙 확정.
- AC 대비 결과: A0는 TRD 템플릿상 별도 AC 섹션이 없는 설계 문서 — §3(요구사항 대응표)의 9개 항목 전부 반영 확인됨.

## §3. 발견된 편차 (TRD/가정과 실제가 다름) [필수 기록]
| 무엇을 가정했는가 | 실제로는 어땠는가 | 어떻게 처리했는가 |
|---|---|---|
| 개인정보 보유/마스킹 정책이 데이터 모델 확정 전에 먼저 결정될 것 | `students.contact`/`guardian_contact`를 평문 VARCHAR 컬럼으로 먼저 "확정"한 뒤에도, `docs/attend_requirements_summary.md` §3의 마스킹 정책은 여전히 "미결" 상태로 남음 (2026-09-05 감사에서 발견) | CLAUDE.md에 실패 패턴으로 기록. §6에 미결 정책으로 등재 — **아직 해소 안 됨, 사람 결정 필요** |

## §4. 남은 것 / 다음 세션에서 할 일
- [x] `students.contact`/`guardian_contact`의 보유기간·마스킹·열람권한 정책 확정 — 2026-09-05, ADR-008 (`docs/attend_adr.md`, `docs/attend_data_lifecycle.md`)
- [ ] **후속**: ADR-008 반영을 위해 `attend_a0_datamodel_trd.md`에 열람 이력 테이블(`contact_view_log`: id, student_id, viewed_by, viewed_at) 추가 — A2 착수 전 필수
- [ ] 반이동 처리 화면/절차 확정 (TRD §4에 미결로 명시됨)
- [ ] 학생 사진(`photo_path`) 저장소 종류(로컬/S3 등) — 기술스택 확정 문서(`harness_13`)와 연동 필요

## §5. 다음 세션 착수 전 반드시 확인할 것
- `docs/trd/attend_a0_datamodel_trd.md`가 "확정" 상태이지만, PII 컬럼 관련 정책은 별개로 미결이라는 점을 다음 세션(특히 A2 사용자관리, 학생정보 화면 구현 시)이 다시 확인해야 함. TRD의 "확정" 표시만 보고 안심하지 말 것.

## §6. 리스크/미결 정책 (아직 사람의 최종 결정이 안 난 것)
| 항목 | 현재 임시 기본값 | 결정 필요 시점 |
|---|---|---|
| `students.contact`/`guardian_contact` 노출·보존 방식 | ✅ 확정됨 (ADR-008, 2026-09-05) — 남은 건 TRD/코드 반영뿐 | 해소됨 |
| 정확한 법적 보존기간(3년은 잠정치) | 3년(교육기관 관례 기준) | 법무 검토 시 조정 가능 |
