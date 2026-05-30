/*=============================================================
  Snow편의점 ML Workshop - 데이터 적재
  Git Repository 스테이지에서 CSV 파일을 COPY INTO
=============================================================*/

USE DATABASE SNOW_ML_WORKSHOP;
USE SCHEMA CVS_DEMO;

-- Git 스테이지 경로 참조 (리포지토리 이름: snow_ml_workshop)
-- 사전 조건: 00_git_integration.sql로 Git Integration + Repository 생성 완료

-- 1. 매장 마스터
COPY INTO STORES
FROM @SNOW_ML_WORKSHOP.CVS_DEMO.snow_ml_workshop_repo/branches/main/data/stores.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 2. 상품 마스터
COPY INTO PRODUCTS
FROM @SNOW_ML_WORKSHOP.CVS_DEMO.snow_ml_workshop_repo/branches/main/data/products.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 3. 시간별 매출 (대용량 - gzip 압축 분할 파일)
COPY INTO HOURLY_SALES
FROM @SNOW_ML_WORKSHOP.CVS_DEMO.snow_ml_workshop_repo/branches/main/data/
PATTERN = 'hourly_sales.*[.]csv[.]gz'
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' COMPRESSION = 'GZIP');

-- 4. 날씨 데이터
COPY INTO WEATHER_DATA
FROM @SNOW_ML_WORKSHOP.CVS_DEMO.snow_ml_workshop_repo/branches/main/data/weather_data.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 5. 한국 이벤트/공휴일
COPY INTO KOREAN_EVENTS
FROM @SNOW_ML_WORKSHOP.CVS_DEMO.snow_ml_workshop_repo/branches/main/data/korean_events.csv
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 적재 결과 확인
SELECT 'STORES' AS TBL, COUNT(*) AS ROWS FROM STORES
UNION ALL SELECT 'PRODUCTS', COUNT(*) FROM PRODUCTS
UNION ALL SELECT 'HOURLY_SALES', COUNT(*) FROM HOURLY_SALES
UNION ALL SELECT 'WEATHER_DATA', COUNT(*) FROM WEATHER_DATA
UNION ALL SELECT 'KOREAN_EVENTS', COUNT(*) FROM KOREAN_EVENTS;
