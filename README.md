# ❄️ Snow편의점 ML Workshop

Snowflake의 End-to-End ML 파이프라인을 편의점 매출 예측 시나리오로 실습합니다.

## 아키텍처

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Raw Data   │───▶│  Feature Store   │───▶│  ML Forecast     │
│  (5 Tables) │    │  (Dynamic Table) │    │  (서버리스 학습)    │
└─────────────┘    └──────────────────┘    └──────────────────┘
                                                      │
                   ┌───────────────────┐              │
                   │  ML Observability │◀─────────────┘
                   │  (모니터링/알림)     │
                   └───────────────────┘
```

## 실습 내용 (5단계)

| 단계 | 주제 | 산출물 |
|------|------|--------|
| 1️⃣ | Feature Store | `DAILY_SALES_FEATURES` Dynamic Table |
| 2️⃣ | Training | `TOTAL_SALES_FORECAST`, `CATEGORY_SALES_FORECAST` 모델 |
| 3️⃣ | Forecast | `SALES_FORECAST` 테이블 (30일 예측) |
| 4️⃣ | Model Registry | `ML_MODEL_REGISTRY` 메타데이터 |
| 5️⃣ | ML Observability | `ML_MONITORING_LOG` 성능 이력 |

## 사전 준비

- Snowflake 계정 (Trial 가능)
- ACCOUNTADMIN 역할
- GitHub 계정 + Personal Access Token (PAT)

## 실습 순서

### Step 0. Git Integration 연결
```sql
-- setup/00_git_integration.sql
-- GitHub PAT와 리포지토리 URL을 수정 후 실행
```

### Step 1. 테이블 생성
```sql
-- setup/01_ddl.sql 실행
-- Database: SNOW_ML_WORKSHOP, Schema: CVS_DEMO
```

### Step 2. 데이터 적재
```sql
-- setup/02_load_data.sql 실행
-- Git 스테이지에서 CSV 파일을 COPY INTO
```

### Step 3. 노트북 실행
1. Snowsight > Notebooks에서 `notebooks/sales_forecast.ipynb` 열기
2. Compute: Warehouse 선택 (XSMALL 이상)
3. 셀 순서대로 실행

### Step 4. (선택) Task 스케줄링
```sql
-- setup/03_schedule.sql 실행
-- 매주 월요일 02:00 KST 자동 재학습
```

## 데이터 구성

| 테이블 | 건수 | 설명 |
|--------|------|------|
| `HOURLY_SALES` | 921,491 | 시간별 매출 트랜잭션 (2024.07~2025.12) |
| `PRODUCTS` | 390 | 상품 마스터 (9개 카테고리) |
| `STORES` | 103 | 매장 마스터 (7개 지역) |
| `WEATHER_DATA` | 3,843 | 지역별 일간 날씨 |
| `KOREAN_EVENTS` | 31 | 한국 공휴일/이벤트 |

## 프로젝트 구조

```
snow-ml-workshop/
├── README.md
├── setup/
│   ├── 00_git_integration.sql   # Git 연결 설정
│   ├── 01_ddl.sql               # DB/스키마/테이블 생성
│   ├── 02_load_data.sql         # 데이터 적재
│   └── 03_schedule.sql          # Task 스케줄링
├── data/
│   ├── stores.csv
│   ├── products.csv
│   ├── weather_data.csv
│   ├── korean_events.csv
│   ├── hourly_sales_01.csv.gz   # 매출 분할 파일 1 (gzip)
│   ├── hourly_sales_02.csv.gz   # 매출 분할 파일 2 (gzip)
│   ├── hourly_sales_03.csv.gz   # 매출 분할 파일 3 (gzip)
│   └── hourly_sales_04.csv.gz   # 매출 분할 파일 4 (gzip)
└── notebooks/
    └── sales_forecast.ipynb     # ML 파이프라인 노트북
```

## 주요 Snowflake 기능

- **ML Feature Store**: 피처 중앙 관리, Dynamic Table 자동 갱신
- **Snowflake ML Forecast**: SQL 한 줄로 시계열 예측 모델 학습
- **Model Registry**: 모델 버전/메타데이터 관리
- **Cortex AI**: 자동 인사이트 생성 (LLM 활용)
- **Tasks**: 주기적 재학습 자동화
