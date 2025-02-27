import os
import pandas as pd
import snowflake.connector
from tabulate import tabulate

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from dotenv import load_dotenv
load_dotenv()

## 앱 연결
app = App(
    token= os.environ.get("SLACK_BOT_TOKEN"))

## DB 연결
def connect_to_snowflake():
    try:
        conn = snowflake.connector.connect(
            user=os.environ.get("SNOWFLAKE_USER"),
            password=os.environ.get("SNOWFLAKE_PASS"),
            account=os.environ.get("SNOWFLAKE_ACCOUNT"),
            warehouse="COMPUTE_WH",
            database="dev",
            schema="analytics",
            role="Analytics_users"
        )
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM analytics.slackbot_backend;")
        backend = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

        cur.execute("SELECT * FROM raw_data.exchange_location_info;")
        exchange = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

        cur.close()
        conn.close()
        return backend,exchange,"Snowflake에 성공적으로 연결되었습니다"

    except Exception as e:
        return False, False, "Error : Snowflake연결에 실패하였습니다."

backend,exchange,result = connect_to_snowflake()       

## 사용자의 상태
user_state = {}

def user_state_exchange(user_id,text,say):
    result = exchange[exchange['ADDRESS_NAME'].str.contains(text,na=False)]
    if result.shape[0]:
        texted_dateframe = tabulate(
            result[['ADDRESS_NAME','PLACE_NAME','PLACE_URL']],
            headers='keys',
            tablefmt='grid',
            showindex=False
        )
        code_block= f"```\n{texted_dateframe}\n```"
        user_state.pop(user_id)

        say(f"{text}의 환전소 위치 정보")
        say(f"{code_block}")
        say(f"이용해주셔서 감사합니다!😊")

    else:
        say(f"😢{text}에는 환전소 위치 정보 데이터가 존재하지 않습니다.")
        user_state.pop(user_id)
        say(f"이용해주셔서 감사합니다!😊")
        
def user_state_city(text,say):
    result = backend[backend["NAME_KO"]==text].iloc[0]

    if text in backend["NAME_KO"].values:
        result = backend[backend["NAME_KO"]==text].iloc[0]
        if result['WEATHER'] == "Clouds":
            weather = "☁️ 날씨: 흐림 (Cloudy)"
        elif result['WEATHER'] == "Rain":
            weather = "🌧️ 날씨: 비 (Rainy)"
        elif result['WEATHER'] == "Snow":
            weather = "❄️ 날씨: 눈 (Snowy)"
        else:
            weather = "☀️ 날씨: 맑음(Cleary)"
        say(f"""[{text}] \n
💰 환율 정보: 1 {result['ISO4217']} = {result['KFTC_DEAL_BAS_R']}원
🌤️ 기상 정보: 최저 {result['MIN_TEMP']}°c / 최고 {result['MAX_TEMP']}°c
{weather}
🌧️ 강수확률: {int(result['POP']*100)}%""")
        say(
            blocks=[
                {
                    "type":"section",
                    "text": {"type": "mrkdwn", "text": "원하는 환전소 위치 정보를 알려드릴까요?"},
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "네"},
                            "value": "네",
                            "action_id":"select_yes",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "아니오"},
                            "value": "아니오",
                            "action_id":"select_no",
                        },
                    ],
                },
            ]
        )

@app.event("app_mention")
def handle_app_mention_events(event,say):
    user_id = event["user"]
    
    if result[:5] =="Error":
        say(result)
        raise
    
    if user_id not in user_state:
        user_state[user_id] = {"step":"도시"}
        say(result)
        say(f"<@{user_id}>님 안녕하세요! 여행을 가고 싶은 도시를 입력해주세요. 👉[입력예시: 런던]")
    else:
        say(f"<@{user_id}>님 멘션(@)을 제거하고 {user_state[user_id]['step']}를 말해주세요!")
    

@app.message()
def message_handler(message,say):
    text = message["text"].strip()
    bot_id = app.client.auth_test()["user_id"]
    user_id = message["user"]
    
    if user_id not in user_state and f"<@{bot_id}>" in text:
        return
    if not user_state.get(user_id,0):
        say(f"<@{user_id}>님 저를 멘션(@)으로 호출해주세요.")
    elif user_state[user_id]['step'] == "환전소":
        user_state_exchange(user_id,text,say)
    elif user_state[user_id]['step'] == "도시":
        user_state_city(text,say)


@app.action("select_yes")
def handle_yes_click(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    user_state[user_id] = {"step":"환전소"}
    say(f"환전을 원하는 국내 위치를 입력해주세요. 👉[입력예시: 서울 강남구, 충북 청주시, 전남 화순군]")

@app.action("select_no")
def handle_yes_click(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    user_state.pop(user_id)
    say(f"""환전소 정보가 필요하다면 저를 다시 멘션(@)으로 호출해주세요! \n
이용해주셔서 감사합니다!😊""")
    

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
