# End-to-end 데이터 파이프라인 구성하기
### 주제: 해외여행지 정보 제공 슬랙봇 
**Team: 보람 3조** | 2025.01.24 ~ 2025.02.06
  + `윤여준`: OpenWeather API를 활용한 도시의 좌표정보 및 날씨정보에 대한 DAG 작성, ELT테이블 생성, 슬랙봇 개발
  + `신예린`: 네이버 항공권을 이용한 Airline에 대한 DAG 작성, ELT테이블 생성, 디스코드봇 개발
  + `백재우`: 한국수출입은행 API를 활용한 나라별 환율정보에 대한 DAG 작성, ELT테이블 생성, 슬랙봇 개발
  + `이은지`: 카카오 API를 활용한 환전소 데이터 크롤링

# 목차
1. 프로젝트 개요<br>
2. 서비스 구조 및 데이터 설계<br>
3. 기술 스택 & 데이터 소스<br>
4. 프로젝트 세부 결과<br>
5. 결론<br>

# 프로젝트 개요
이 프로젝트는 해외여행을 준비하는 여행객들에게 필수적인 정보를 제공하는 슬랙봇을 개발하는 것입니다. 사용자는 슬랙을 통해 실시간으로 여행지의 날씨, 환율, 항공권 가격, 주변 환전소 정보 등을 간편하게 조회할 수 있습니다.

단순한 정보 제공을 넘어, ETL 및 ELT 파이프라인을 활용하여 최신 데이터를 수집 및 처리하고, 이를 데이터 레이크 및 데이터 웨어하우스에 적재함으로써 신뢰할 수 있는 정보를 제공합니다. 이를 통해 여행객들은 여러 웹사이트를 직접 검색하는 번거로움 없이, 손쉽게 필요한 정보를 받아보고 보다 효율적으로 여행을 계획할 수 있습니다.

이 슬랙봇은 실시간 데이터 제공을 기반으로 여행 준비 과정에서 발생하는 정보 탐색의 번거로움을 줄이고, 사용자 경험을 극대화하는 것을 목표로 합니다. 🚀

# 서비스 구조 및 데이터 설계
## 사용자 시나리오
<details>
  <summary>🔹 1. 여행 도시 선택</summary>

  - 슬랙봇이 메시지를 전송:  
    **"어디로 여행을 가고 싶으신가요? 도시를 선택해주세요!"**  
  - 사용자가 입력: **런던 / LA / 오사카** 등 원하는 도시 선택  
</details>

<details>
  <summary>🔹 2. 기본 정보 조회</summary>

  - 사용자가 선택한 도시를 기준으로 **다음 정보를 조회**  
    - 🌦 **날씨 정보** (Weather API)  
    - 💱 **환율 정보** (Exchange Rate API)  
    - ✈️ **항공권 평균 가격** (크롤링)  
  - 슬랙봇이 응답:  
    ```
    현재 런던의 날씨는 맑음 ☀️, 기온은 18°C입니다.
    1 USD = 1,300 KRW 입니다.
    인천에서 런던까지의 평균 항공권 가격은 1,200,000원 입니다.
    ```
</details>

<details>
  <summary>🔹 3. 환전소 정보 제공 (선택 사항)</summary>

  - 슬랙봇이 질문:  
    **"원하는 지역의 환전소 위치 정보를 알려드릴까요? (네 / 아니오)"**  
  - **사용자 응답에 따라 분기**  
    - "네" 선택 → **환전소 위치 입력 요청**  
    - "아니오" 선택 → **대화 종료 ("다른 도움이 필요하시면 말씀해주세요!")**  
</details>

<details>
  <summary>🔹 4. 환전소 정보 조회 및 제공</summary>

  - 사용자가 **환전을 원하는 지역** 입력 (예: "서울시 강남구")  
  - 슬랙봇이 **카카오 맵 API를 활용하여 환전소 정보 조회**  
  - 슬랙봇 응답:  
    ```
    서울시 강남구에는 다음과 같은 환전소가 있습니다:
    
    | 환전소 이름 | 주소 | 운영시간 |
    |------------|--------------------|--------|
    | AAA 환전소 | 강남대로 123 | 09:00 - 20:00 |
    | BBB 환전소 | 테헤란로 456 | 10:00 - 22:00 |
    ```
  - **대화 종료**
</details>
<br>

## 아키텍처
<img width="701" alt="image" src="https://github.com/user-attachments/assets/7543f908-ec80-4525-a2de-6855a0a88432" />

## ERD
<img width="701" alt="image" src="https://github.com/user-attachments/assets/c0289a2c-3bcd-4918-94f4-e87c0bf51d6c" />

# 기술스택 & 데이터 소스
### Backend 
`Python` `Slack Bolt(Socket Mode)` `Snowflake`

### ETL
`Python` `Airflow` `AWS S3` `Snowflake` `Docker`

### Collab
`Github` `Slack` `Zep` `Notion`
  
### 데이터 소스
`한국수출입은행 API` `KakaoMap API` `OpenWeatherMap API` `네이버 항공권 WebPage`

# 프로젝트 세부결과
## DAG
### plugins
<details>
  <summary>parquet_to_s3</summary>

    주요기능
    - DataFrame을 Parquet 포맷으로변환
    - Airflow의 S3Hook을 활용하여 특정 Topic(도시,환율,항공권)에 따라 적절한 경로에 자동생성
    - Amazon S3 버킷에 데이터 저장
    - 업로드 경로를 오늘 날짜 기준으로 자동 설정
    - S3에 동일한 파일이 존재하면 덮어쓰기 여부(replace)를 선택 가능
</details>

<details>
  <summary>s3_to_snowflake</summary>

    주요기능
    - Parquet 데이터가 저장된 S3에 Snowflake로 데이터 적재
    - Airflow의 SnowflakeHook을 활용하여 특정 Topic에 따라 적절한 데이터 삽입
    - 테이블이 존재하지 않으면 자동 생성
    - 기존 데이터 삭제 후 새로운 데이터 삽입(Full Refressh)
    - 파일 형식(PARQUET)을 지정하여 COPY INTO 실행
    - 예외 발생 시 ROLLBACK 실행으로 데이터 무결성 유지
</details>

### 도시 및 날씨정보
<details>
  <summary>get_city_lat_lon</summary>

    주요 기능
    - 사용자가 입력한 도시명 기반으로 OpenWeather API에서 위치 정보를 조회
    - 조회된 데이터를 Snowflake 테이블(raw_data.get_city_info)에 저장
    - 중복 데이터가 있을 경우 기존 데이터를 삭제하고, 최신 데이터를 반영

    DAG 정보
    - schedule: None (수동 실행 전용)
    - catchUp : False
    - 기존에 있는 데이터가 들어올 경우만 ROW_NUMBER를 Refresh
    - 특정 Airflow container에 접속하여 아래 커맨드 작성해서 DAG 실행
    - airflow dags test get_city_lat_lon —conf ‘{”city_name”: “New York”}’
</details>

<details>
  <summary>get_Weather_Information</summary>

    주요 기능
    - Snowflake의 도시정보 테이블(raw_data.get_city_info)에서 위치 정보를 조회
    - OpenWeatherMap API에 도시의 날씨 정보를 반복으로 요청하여 날씨 예측 정보 수집
    - Json데이터를 Parquet파일로 변환하여 S3에 업로드
    - S3의 데이터를 snowflake_stage를 사용해 COPY INTO로 최종 적재

    DAG 정보
    - start_date: 2025-01-01
    - schedule: (30 15 * * *) UTC, 한국 시간 12시30분 기준 스케줄링
    - catchUp : False, Full Refresh(과거 데이터는 S3에 저장)
    - 실패 시 최대 1회 재시도(간격은 3분)
</details>

### 네이버 항공권 
<details>
  <summary>airline_ticket_crawling</summary>

    주요기능
    - 항공권 크롤링 → 네이버 항공권 사이트에서 해외 도시(도쿄, 뉴욕 등) 항공권 데이터 수집
    - 출발일 자동 변경 → 현재 날짜 기준 3일간의 항공권 정보 크롤링
    - Selenium 활용 → Chrome WebDriver로 자동화, Headless 모드 지원
    - 데이터 정리 → Pandas DataFrame으로 저장, 중복 제거 후 반환
    - 예외 처리 & 로깅 → 광고·특가 항공권 예외 처리, 오류 로깅 적용
</details>

<details>
  <summary>get_airline_information</summary>

    주요 기능
    - 네이버 항공권 데이터를 3일 간격으로 자동 수집하는 Airflow DAG
    - 수집한 데이터를 S3에 저장 후 Snowflake로 적재

    DAG 정보
    - 스케줄: 0 15 */3 * * (3일마다 실행)
    - 태스크 실행 흐름: 크롤링 → S3 업로드 → Snowflake 적재

    태스크
    - get_airline_crawling_data() → 네이버 항공권 크롤링 실행
    - parquet_to_s3() → 크롤링 데이터를 Parquet 변환 후 S3 업로드
    - s3_to_snowflake() → S3 데이터를 Snowflake 테이블에 적재
</details>

### 환율 정보
<details>
  <summary>get_currency_information</summary>

    주요 기능
    - 한국수출입은행 API 호출 → 실시간 환율 정보(cur_unit, cur_nm, kftc_deal_bas_r) 수집
    - Parquet 변환 및 S3 업로드 → 수집된 데이터를 Parquet 형식으로 변환 후 S3 저장
    - Snowflake 적재 → COPY INTO를 사용해 S3 데이터를 Snowflake 테이블(raw_data.slackbot_currency_info)에 적재

    DAG 정보
    - start_date: 2025-01-27
    - schedule: 0 3 * * * (매일 한국 시간 12:00 PM 실행)
    - catchup: False (과거 데이터는 저장하지 않음)
    - 환경 변수 사용: Airflow Variable에서 currency_api_key를 가져와 API 호출
    - 태스크 실행 흐름: 환율 데이터 수집 → Parquet 변환 & S3 업로드 → Snowflake 적재
</details>

### 환전소 위치 정보
<details>
  <summary>exchange_location_crawler</summary>

    주요 기능
    - 카카오 지도 API 활용 → 전국 주요 도시(서울, 부산, 제주 등)의 환전소 정보 수집
    - 검색 키워드 지정 → "환전소", "외환", "환전", "외화 환전", "환전 가능한 은행" 등의 키워드 검색
    - 반복 요청 → 각 도시별로 반경 20km 내 환전소 검색 (최대 3페이지 반복 요청)
    - 중복 데이터 제거
    - 불필요한 장소(ATM, 충전소, 주차장 등) 필터링
    - "특별자치도", "특별자치시" 등 불필요한 행정 구역명 제거
    
    실행 과정
    - 카카오 API 요청 → 위치 기반 환전소 검색 후 JSON 데이터 반환
    - 데이터 가공 → pandas를 활용하여 DataFrame 변환 및 중복 제거
    - CSV 저장 → exchange_location.csv 파일로 저장 (utf-8-sig 인코딩 적용)
</details>

### 슬랙봇 백엔드 ELT
<details>
  <summary>get_slackbot_backend</summary>

    ETL 실행 (ELT 방식 적용)
    - 환율, 항공권, 날씨 데이터를 Snowflake에서 가공하여 Slackbot이 활용할 데이터 테이블(analytics.slackbot_backend) 생성
    
    데이터 변환 과정
    - 항공권 정보 요약: 도시별 평균 항공권 가격 계산
    - 날씨 정보 요약: 최저/최고 기온, 날씨 상태, 강수 확률 집계
    - 최종 데이터 결합: 국가/도시 정보 + 환율 + 항공권 가격 + 날씨 정보를 하나의 테이블로 병합

    DAG 정보
    - start_date: 2025-01-01
    - schedule: 0 16 * * * (매일 한국 시간 01:00 AM 실행)
    - catchup: False (과거 데이터는 저장하지 않음)
    - 테이블 생성 방식: CREATE OR REPLACE TABLE (기존 데이터 갱신)
    - 예외 처리: 쿼리 실행 중 오류 발생 시 ROLLBACK 처리하여 데이터 정합성 유지
</details>

## Slackbot
### ✅ 사용자 입력 처리
- Slack에서 @Slackbot을 멘션하면 대화가 시작됩니다.
- 사용자의 현재 상태를 단계별로 관리하여 필요한 정보를 순차적으로 제공합니다.
### ✅ Snowflake 데이터 연동
- 환율 및 기상 정보와 환전소 위치 정보를 Snowflake에서 조회하여 제공합니다.
### ✅ 환율 및 기상 정보 조회
- 사용자가 입력한 도시명을 검색하여 환율, 기온, 날씨 상태, 강수 확률 등을 안내합니다.
- 추가로 환전소 정보가 필요한 경우, 버튼을 통해 선택할 수 있습니다.
### ✅ 환전소 위치 정보 제공
- 지역명을 입력하면 해당 지역의 환전소 목록(이름, 주소, URL) 을 표 형태로 제공해 줍니다.
### ✅ Slack 인터랙션 기능
- 버튼을 활용하여 직관적인 사용자 경험 제공
  + 네 버튼 클릭 시 → 환전소 정보 조회 단계로 이동
  + 아니오 버튼 클릭 시 → 대화 종료
### ✅ 시연 영상
![소셜(채널) - slack_alert_practice - Slack 2025-02-06 16-13-04](https://github.com/user-attachments/assets/3cc56b15-3171-4390-bdca-0b242c517b83)

# 결론
## 📌 기대효과

✅ 여행자들에게 편의 제공
- 사용자가 **Slack 채팅 환경**에서 원하는 여행 목적지에 대한 다양한 정보를 **실시간으로 제공**받아, 의사결정 및 여행 준비에 큰 도움을 줄 수 있음

✅ 자동화된 데이터 파이프라인 구축
- **Airflow를 통한 정기적인 데이터 수집 및 가공** 및 **Snowflake를 활용한 중앙 집중형 저장 시스템**을 구축하여, 향후 **데이터 분석 및 머신러닝 모델 적용** 등 추가 활용 가능성 확보

✅ 확장성과 유연성
- 각 **데이터 소스를 독립적인 DAG**로 구성하여, 새로운 API나 데이터 소스가 추가되더라도 **기존 파이프라인에 유연하게 통합 가능**

## ⚠️ 한계
- 많은 도시 정보를 제공하지 못하는 점
  + 개발 기간과 리소스의 한계로 인해 **전 세계 모든 도시 정보를 제공하지 못함**
  + 현재 일부 **주요 도시(런던, LA, 오사카 등)로 제한**
  + 환전소 정보는 **국내 지역으로 한정**
- 이로 인해 **다양한 지역의 여행 수요를 완벽하게 반영하지 못하는 한계 존재**

## 🔄 개선점

#### 1. 프로덕션 데이터베이스 활용
  + 현재 **DW(Snowflake)** 를 슬랙봇의 DB로 사용했으나, **실제 서비스처럼 구현하기 위해 MySQL 또는 PostgreSQL로 마이그레이션 진행**

#### 2. 도시 정보 확장
  + 추가적인 **데이터 소스 및 API 연계**를 통해 **전 세계 주요 도시뿐 아니라 더 많은 지역의 정보를 실시간으로 수집**

#### 3. 슬랙봇 대화 시나리오 고도화
  + 사용자 인터랙션을 더욱 풍부하게 하기 위해 **다양한 시나리오를 도입**

#### 4. 데이터 파이프라인 안정성 및 모니터링 강화
  + 데이터 수집 및 처리 단계에서 **오류를 실시간 감지하고 자동 재시도하는 로직 추가**
  + **데이터 품질을 모니터링할 수 있는 시스템 구축**하여 안정성 확보

