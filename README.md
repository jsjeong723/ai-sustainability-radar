# AI Sustainability Radar

AI 사회 지속성 레이더는 AI 도입에 따른 생산성 향상이 사회의 지속성과 회복력에 미치는 영향을 공개자료로 장기간 관찰하는 공동 연구 프로젝트입니다.

> **Observe continuously. Verify independently. Decide responsibly.**

## 프로젝트 원칙

- 공개자료를 자동 수집하되 출처와 수집 시점을 보존합니다.
- 관측된 사실과 AI의 해석을 분리합니다.
- 자료가 없거나 관측할 수 없는 값은 0이 아닌 `자료 없음`으로 기록합니다.
- 긍정적 효과와 부정적 효과를 대칭적으로 관찰합니다.
- AI는 관측·분석·검토를 지원하며 최종 판정은 인간이 수행합니다.
- AI별 독립 검토 의견과 인간 판정 이력을 덮어쓰지 않고 보존합니다.

## MVP 범위

미국 중심의 공개자료를 이용해 다음 5개 지표를 추적합니다.

1. 신입 채용 공고 수
2. 주요 AI 모델·정책·규제 발표
3. 임금·고용 통계
4. 전력·탄소 지표
5. 검증 자동화·중대 오류·재작업 관련 공개 사례

## 초기 구현 목표

첫 번째 마일스톤은 BLS와 EIA의 공식 통계를 자동 수집하고, 데이터베이스에 저장한 뒤 웹 대시보드에 표시하는 것입니다. 이후 뉴스·정책·채용·사고 사례 수집기를 순차적으로 추가합니다.

## 문서 안내

| 문서 | 설명 |
|---|---|
| [`docs/MVP_SPEC.md`](docs/MVP_SPEC.md) | MVP 기능 범위와 완료 기준 |
| [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md) | 시스템 구성과 데이터 흐름 |
| [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | 핵심 데이터 항목 정의 |
| [`docs/SOURCE_CATALOG.md`](docs/SOURCE_CATALOG.md) | 공개 데이터 출처와 수집 계획 |

## 권장 저장소 구조

```text
ai-sustainability-radar/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── docs/
│   ├── MVP_SPEC.md
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── SOURCE_CATALOG.md
│   └── DEVELOPMENT_ROADMAP.md
├── apps/
│   └── web/
├── backend/
│   ├── app/
│   └── tests/
├── config/
├── scripts/
└── .github/
    └── workflows/
```

## 개발 상태

현재 저장소 초기 문서 단계입니다. 아직 실제 수집기, 데이터베이스 마이그레이션, 대시보드 및 AI 어댑터는 구현되지 않았습니다.

## 기여 및 판정 원칙

연구 참여자는 자료의 출처, 정의, 측정 단위, 비교 기준을 확인해야 합니다. AI가 생성한 요약이나 경보만으로 사실을 확정하지 않습니다. 인간 판정은 `채택`, `기각`, `보류`, `추가 조사` 중 하나로 기록하고, 이유와 후속 지시를 함께 보존합니다.
