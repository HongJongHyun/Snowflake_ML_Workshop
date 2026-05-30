/*=============================================================
  Snow편의점 ML Workshop - Git Integration 설정
  Public GitHub 리포지토리를 Snowflake에 연결합니다.
  
  GitHub: https://github.com/HongJongHyun/Snowflake_ML_Workshop
=============================================================*/

USE ROLE ACCOUNTADMIN;

CREATE DATABASE IF NOT EXISTS SNOW_ML_WORKSHOP;
CREATE SCHEMA IF NOT EXISTS SNOW_ML_WORKSHOP.CVS_DEMO;

USE DATABASE SNOW_ML_WORKSHOP;
USE SCHEMA CVS_DEMO;

-- 1. API Integration (Public repo - 인증 불필요)
CREATE OR REPLACE API INTEGRATION snow_ml_workshop_git_api
    API_PROVIDER = git_https_api
    API_ALLOWED_PREFIXES = ('https://github.com/HongJongHyun/')
    ENABLED = TRUE;

-- 2. Git Repository 연결 (Secret 없이)
CREATE OR REPLACE GIT REPOSITORY snow_ml_workshop_repo
    API_INTEGRATION = snow_ml_workshop_git_api
    ORIGIN = 'https://github.com/HongJongHyun/Snowflake_ML_Workshop.git';

-- 3. 연결 확인
ALTER GIT REPOSITORY snow_ml_workshop_repo FETCH;
SHOW GIT BRANCHES IN snow_ml_workshop_repo;

-- 4. 파일 목록 확인
LS @snow_ml_workshop_repo/branches/main/;

SELECT '✅ Git Integration 설정 완료' AS STATUS;
