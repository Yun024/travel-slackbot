-- 스테이지 생성 및 권한 부여
CREATE OR REPLACE STAGE dev.raw_data.my_s3_stage
URL = 's3://yeojun-test-bucket/'
CREDENTIALS = (AWS_KEY_ID='AWS_ACCESS_KEY' AWS_SECRET_KEY='AWS_SECRET_KEY');

GRANT ALL ON STAGE dev.raw_data.my_s3_stage TO ROLE analytics_users;

-- 스테이지 연결 확인용 쿼리
LIST @dev.raw_data.my_s3_stage/slackbot/weather/20250203/;

-- (도쿄도, 오키나와섬)과 같은 데이터 데이터 이름 변경
update dev.raw_data.get_city_info
set name_ko =replace(name_ko,'삿포로시','삿포로')
where name_ko like '%삿포로시%';

commit;

-- Slackbot 관련 테이블 조회
select * from dev.raw_data.get_city_info;
select * from dev.raw_data.slackbot_weather_info;
select * from dev.raw_data.slackbot_currency_info;
select * from dev.raw_data.slackbot_airline_info;
select * from dev.raw_data.country_currency_info;
select * from dev.raw_data.exchange_location_info;
select * from dev.analytics.slackbot_backend;