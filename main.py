from langchain_community.document_loaders import WebBaseLoader
from slack_bolt import App as SlackApp
import re
from dotenv import load_dotenv

load_dotenv() # for local

app = SlackApp()

loader = WebBaseLoader("https://www.ksponco.or.kr/spm/tennis/tennis_wait_status.do")
web_data = loader.load()
content = web_data[0].page_content.strip().replace("\n", "").replace("\t", "")


# 정규식을 이용하여 시간대별 예약현황을 추출
pattern = re.compile(r'대기현황요일시간/코트(.*?)● 1인 1강좌만', re.DOTALL)
match = pattern.search(content)

if match:
    timetable_data = match.group(1).strip()
    sections = re.split(r'(주중실외|주중실내|주말실외|주말실내|수요일실내)', timetable_data)[1:]
    
    reservation_status = {}
    for i in range(0, len(sections), 2):
        label = sections[i]
        timeslots = re.findall(r'(마감|X|\d+)', sections[i+1])
        timeslots = [(i+6, t) for i, t in enumerate(timeslots)]
        reservation_status[label] = timeslots

    # 출력
    for label, timeslots in reservation_status.items():
        print(f"{label}: {timeslots}")

else:
    print("예약 현황을 찾을 수 없습니다.")


def is_available(timeslots):
    return [ts for ts in timeslots if ts[1].isdigit()]

message = ""
for weekend in ["주말실외", "주말실내"]:
    possible = is_available(reservation_status[weekend][1:]) # 7시부터 가능
    if possible:
        for p in possible:
            message += f"{weekend}에 가능한 시간: {p[0]}\n"
for week in ["주중실외", "주중실내", "수요일실내"]:
    possible = is_available(reservation_status[week][1:3] + reservation_status[week][-3:])
    if possible:
        for p in possible:
            message += f"{week}에 가능한 시간: {p[0]}\n"

if not message:
    app.client.chat_postMessage(
        channel='C074SLJRGTS',
        text=f"응 돌아가",
    )
else:
    app.client.chat_postMessage(
        channel='C074SLJRGTS',
        text=f"<@U0743SMPX3L> 올림픽 공원 달려가\n{message}",
    )

