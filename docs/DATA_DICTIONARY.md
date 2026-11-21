# Data Dictionary

## 1. 설계 원칙

데이터 사전은 관측값, 사건, 출처, AI 검토, 인간 판정을 구분한다. 원자료를 정규화하더라도 원래 표현과 단위를 잃지 않도록 한다.

- 결측값은 `NULL` 또는 명시적 상태로 기록한다.
- 0은 실제로 측정된 0일 때만 사용한다.
- 모든 시간은 UTC로 저장하고 원자료의 시간대 정보를 별도로 보존한다.
- 수치에는 단위, 기간, 지역, 모집단 및 정의가 따라야 한다.
- 수정은 기존 레코드 덮어쓰기보다 새 버전 또는 변경 이력으로 남긴다.

## 2. 핵심 엔터티

### 2.1 indicators

| 필드 | 유형 | 설명 |
|---|---|---|
| indicator_id | UUID | 지표 고유 ID |
| code | TEXT | 안정적인 지표 코드 |
| name | TEXT | 지표명 |
| research_question | TEXT | 관찰 질문 |
| definition | TEXT | 측정 정의 |
| default_unit | TEXT | 기본 단위 |
| preferred_frequency | TEXT | 권장 관측 주기 |
| baseline_method | TEXT | 기준선 정의 |
| status | TEXT | active / paused / retired |

초기 코드:
- `ENTRY_LEVEL_JOBS`
- `AI_POLICY_ANNOUNCEMENTS`
- `WAGES_EMPLOYMENT`
- `POWER_CARBON`
- `AI_VALIDATION_INCIDENTS`

### 2.2 sources

| 필드 | 유형 | 설명 |
|---|---|---|
| source_id | UUID | 출처 고유 ID |
| organization | TEXT | 발행 기관 |
| source_name | TEXT | API·페이지·데이터셋 이름 |
| source_type | TEXT | official_api / rss / research / news / report |
| base_url | TEXT | 출처 기본 URL |
| terms_url | TEXT | 이용 조건 URL |
| access_method | TEXT | API / RSS / download / public_page |
| reliability_basis | TEXT | 출처 신뢰도 평가 근거 |
| active | BOOLEAN | 수집 활성 여부 |

신뢰도는 기관 이름만으로 자동 부여하지 않는다. 원자료 여부, 방법론 공개, 독립 검증 가능성 등을 기록한다.

### 2.3 observations

| 필드 | 유형 | 설명 |
|---|---|---|
| observation_id | UUID | 관측값 ID |
| indicator_id | UUID | 연결 지표 |
| source_id | UUID | 원자료 출처 |
| observed_at | TIMESTAMPTZ | 관측 기준 시점 |
| period_start | DATE | 측정 기간 시작 |
| period_end | DATE | 측정 기간 종료 |
| geography | TEXT | 국가·주·지역 |
| industry_code | TEXT | 산업 분류(해당 시) |
| occupation_code | TEXT | 직종 분류(해당 시) |
| metric_name | TEXT | 원자료 지표명 |
| value_numeric | NUMERIC | 수치 |
| value_text | TEXT | 비수치 관측값 |
| unit | TEXT | 측정 단위 |
| status | TEXT | observed / unavailable / delayed / failed |
| raw_record_id | UUID | 원자료 참조 |

### 2.4 events

뉴스·발표·사고와 같은 사건형 자료를 저장한다.

| 필드 | 유형 | 설명 |
|---|---|---|
| event_id | UUID | 사건 고유 ID |
| event_type | TEXT | model / policy / regulation / incident / study |
| title | TEXT | 사건 제목 |
| summary | TEXT | 중립적 요약 |
| organization | TEXT | 관련 기관 |
| announced_at | TIMESTAMPTZ | 발표 시점 |
| effective_at | TIMESTAMPTZ | 시행 시점(해당 시) |
| geography | TEXT | 적용 지역 |
| canonical_event_key | TEXT | 중복 사건 연결 키 |
| verification_status | TEXT | unreviewed / corroborated / disputed / rejected |

### 2.5 source_documents

| 필드 | 유형 | 설명 |
|---|---|---|
| document_id | UUID | 문서 ID |
| source_id | UUID | 출처 |
| url | TEXT | 원문 URL |
| title | TEXT | 문서 제목 |
| published_at | TIMESTAMPTZ | 발표일 |
| collected_at | TIMESTAMPTZ | 수집일 |
| content_hash | TEXT | 내용 중복 식별용 해시 |
| storage_uri | TEXT | 저장된 원문 참조(있는 경우) |
| content_type | TEXT | HTML / PDF / JSON / CSV 등 |
| access_status | TEXT | accessible / restricted / removed / failed |

### 2.6 ai_reviews

| 필드 | 유형 | 설명 |
|---|---|---|
| review_id | UUID | 검토 ID |
| target_type | TEXT | observation / event / report |
| target_id | UUID | 검토 대상 |
| reviewer_model | TEXT | 모델 식별자 |
| reviewer_role | TEXT | 검토 역할 |
| review_stage | TEXT | independent / cross_review / synthesis |
| model_version | TEXT | 모델 버전 |
| prompt_version | TEXT | 프롬프트 버전 |
| facts_json | JSONB | 확인된 사실 |
| interpretations_json | JSONB | 해석 |
| counter_evidence_json | JSONB | 반대 근거 |
| uncertainties_json | JSONB | 불확실성 |
| source_references_json | JSONB | 인용 출처 |
| raw_response | TEXT | 원본 응답 |
| created_at | TIMESTAMPTZ | 생성 시각 |

### 2.7 research_reports

| 필드 | 유형 | 설명 |
|---|---|---|
| report_id | UUID | 보고서 ID |
| report_type | TEXT | weekly / biweekly / ad_hoc |
| period_start | DATE | 대상 기간 시작 |
| period_end | DATE | 대상 기간 종료 |
| summary | TEXT | 통합 요약 |
| agreements_json | JSONB | 합의 사항 |
| conflicts_json | JSONB | 충돌 사항 |
| open_questions_json | JSONB | 미결 사항 |
| source_review_ids | JSONB | 사용한 AI 검토 ID |
| created_at | TIMESTAMPTZ | 생성 시각 |

### 2.8 human_decisions

| 필드 | 유형 | 설명 |
|---|---|---|
| decision_id | UUID | 판정 ID |
| target_type | TEXT | observation / event / report |
| target_id | UUID | 판정 대상 |
| decision | TEXT | adopted / rejected / pending / investigate |
| rationale | TEXT | 판정 이유 |
| fact_issues_json | JSONB | 사실 쟁점 |
| interpretation_issues_json | JSONB | 해석 쟁점 |
| value_issues_json | JSONB | 가치 쟁점 |
| uncertainty_issues_json | JSONB | 불확실성 쟁점 |
| follow_up | TEXT | 후속 지시 |
| reviewer_user_id | UUID | 판정자 |
| decided_at | TIMESTAMPTZ | 판정 시각 |

### 2.9 collection_runs 및 audit_logs

`collection_runs`는 수집 작업의 시작·종료 시각, 출처, 성공·실패 건수, 오류 요약을 저장한다.

`audit_logs`는 사용자, 작업 유형, 대상 레코드, 변경 전후 값, 시각을 저장한다.

## 3. 공통 상태값

### 수집 상태

- `observed`: 관측 성공
- `unavailable`: 해당 시점에 공개자료 없음
- `delayed`: 출처 갱신 지연
- `failed`: 수집 오류
- `restricted`: 접근 제한

### 검증 상태

- `unreviewed`: 아직 검토되지 않음
- `corroborated`: 복수 근거로 확인됨
- `disputed`: 출처 간 충돌
- `rejected`: 근거 부족 또는 오류로 배제

### 인간 판정 상태

- `adopted`: 채택
- `rejected`: 기각
- `pending`: 보류
- `investigate`: 추가 조사

## 4. 자료 품질 메타데이터

각 관측값과 사건에는 가능하면 다음을 추가한다.

- 측정 방법 및 정의
- 원자료 수정 여부
- 계절 조정 여부
- 표본 범위
- 추정치인지 실제 측정치인지
- 독립 검증 여부
- 데이터 한계와 주의사항

## 5. 금지되는 데이터 처리

- 자료 없음 값을 0으로 치환하지 않는다.
- 뉴스 보도량을 실제 사건 수로 간주하지 않는다.
- 추정치를 실제 계량값처럼 표시하지 않는다.
- 서로 다른 단위·기간·모집단을 무표시로 비교하지 않는다.
- AI가 생성한 설명을 원자료 필드에 저장하지 않는다.
