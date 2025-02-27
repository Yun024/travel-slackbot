CREATE OR REPLACE TABLE dev.yeojun.get_city_info (
    name_eng VARCHAR NOT NULL,
    name_ko VARCHAR,
    lat double,
    lon double,
    country VARCHAR,
    get_date TIMESTAMP default GETDATE()
);

GRANT OWNERSHIP ON table dev.yeojun.slackbot_weather_info TO ROLE accountadmin REVOKE CURRENT GRANTS;
delete from dev.raw_data.slackbot_weather_info;
drop table dev.raw_data.slackbot_weather_info;

COPY INTO dev.raw_data.slackbot_currency_info
FROM @dev.raw_data.my_s3_stage/slackbot/currency/20250203/currency_info.parquet
FILE_FORMAT = (TYPE ="PARQUET")
MATCH_BY_COLUMN_NAME = 'CASE_INSENSITIVE'
Force=True;

------ stage 및 file format 생성
CREATE OR REPLACE STAGE dev.raw_data.my_s3_stage
URL = 's3://yeojun-test-bucket/'
CREDENTIALS = (AWS_KEY_ID=AWS_ACCESS_KEY AWS_SECRET_KEY=AWS_SECRET_KEY);

LIST @dev.raw_data.my_s3_stage/slackbot/weather/20250203/;

GRANT ALL ON STAGE dev.raw_data.my_s3_stage TO ROLE analytics_users;
GRANT USAGE ON STAGE dev.raw_data.my_s3_stage TO USER yeojun;
GRANT INSERT ON TABLE dev.raw_data.slackbot_weather_info TO USER yeojun;

GRANT ALL ON FILE FORMAT dev.raw_data.json_format TO ROLE analytics_users;

------------------------------------------ 
-- 삿포로시, 도쿄도, 오키나와섬 와같은 도시명 수동변경경
update dev.raw_data.get_city_info
set name_ko =replace(name_ko,'도쿄도','도쿄')
where name_ko like '%도쿄도%';
commit;

--------------------------------- 테이블 확인
select * from dev.raw_data.get_city_info;
select * from dev.raw_data.slackbot_weather_info;
select * from dev.raw_data.slackbot_currency_info;
select * from dev.raw_data.slackbot_airline_info;

-----------------------------최종 ELT
CREATE OR REPLACE TABLE dev.analytics.slackbot_backend AS(
WITH
airline_summary AS (
    SELECT cityname, CEIL(AVG(price)/100) * 100 AS avg_price
    FROM dev.raw_data.slackbot_airline_info
    WHERE datetime = (SELECT MIN(datetime) FROM dev.raw_data.slackbot_airline_info)
    GROUP BY cityname)
,
weather_summary AS (
    SELECT row_num, ROUND(MIN(temp)-273.15) min_temp, ROUND(MAX(temp)-273.15) max_temp , MAX(weather) weather, MAX(pop) pop  
    FROM dev.raw_data.slackbot_weather_info
    WHERE LEFT(datetime,10) = TO_CHAR(CONVERT_TIMEZONE('UTC', 'Asia/Seoul', CURRENT_TIMESTAMP), 'YYYY-MM-DD')
    GROUP BY row_num)

SELECT 
    country, name_ko, name_eng, min_temp, max_temp, weather, pop, kftc_deal_bas_r, avg_price
FROM dev.raw_data.country_currency_info A
INNER JOIN dev.raw_data.get_city_info B ON A.iso3166 = B.country
INNER JOIN dev.raw_data.slackbot_currency_info C ON A.iso4217 = LEFT(C.cur_unit,3)
INNER JOIN weather_summary D ON B.row_num = D.row_num
INNER JOIN airline_summary E ON B.name_ko = E.cityname)
;

SELECT * FROM dev.analytics.slackbot_backend;
