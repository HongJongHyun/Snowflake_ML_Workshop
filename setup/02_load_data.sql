/*=============================================================
  Snow편의점 ML Workshop - 데이터 적재
  Git Repository → 내부 스테이지 복사 → COPY INTO 테이블
=============================================================*/

USE DATABASE SNOW_ML_WORKSHOP;
USE SCHEMA CVS_DEMO;

-- 사전 조건: 00_git_integration.sql 실행 완료 (Git Repository 연결됨)
-- 최신 커밋 동기화
ALTER GIT REPOSITORY snow_ml_workshop_repo FETCH;

-- 내부 스테이지 생성
CREATE OR REPLACE STAGE load_stage;

/*-------------------------------------------------------------
  Step 1: Git Repository → 내부 스테이지로 파일 복사
-------------------------------------------------------------*/

COPY FILES
  INTO @load_stage
  FROM @snow_ml_workshop_repo/branches/main/data/
  FILES = ('stores.csv', 'products.csv', 'weather_data.csv', 'korean_events.csv',
           'hourly_sales_01.csv.gz', 'hourly_sales_02.csv.gz',
           'hourly_sales_03.csv.gz', 'hourly_sales_04.csv.gz');

-- 복사 확인
LS @load_stage;

/*-------------------------------------------------------------
  Step 2: 내부 스테이지 → 테이블 적재
-------------------------------------------------------------*/

-- 1. 매장 마스터
COPY INTO STORES
FROM @load_stage/stores.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 2. 상품 마스터
COPY INTO PRODUCTS
FROM @load_stage/products.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 3. 시간별 매출 (gzip 압축 분할 파일)
COPY INTO HOURLY_SALES
FROM @load_stage/
PATTERN = 'hourly_sales.*[.]csv[.]gz'
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' COMPRESSION = 'GZIP');

-- 4. 날씨 데이터
COPY INTO WEATHER_DATA
FROM @load_stage/weather_data.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 5. 한국 이벤트/공휴일
COPY INTO KOREAN_EVENTS
FROM @load_stage/korean_events.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

/*-------------------------------------------------------------
  Step 3: 적재 결과 확인 및 정리
-------------------------------------------------------------*/

SELECT 'STORES' AS TBL, COUNT(*) AS ROW_CNT FROM STORES
UNION ALL SELECT 'PRODUCTS', COUNT(*) FROM PRODUCTS
UNION ALL SELECT 'HOURLY_SALES', COUNT(*) FROM HOURLY_SALES
UNION ALL SELECT 'WEATHER_DATA', COUNT(*) FROM WEATHER_DATA
UNION ALL SELECT 'KOREAN_EVENTS', COUNT(*) FROM KOREAN_EVENTS;

-- 내부 스테이지 정리 (선택)
-- DROP STAGE IF EXISTS load_stage;
