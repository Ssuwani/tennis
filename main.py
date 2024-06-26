from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from slack_bolt import App as SlackApp

from dotenv import load_dotenv

load_dotenv() # for local

app = SlackApp()

loader = WebBaseLoader("https://www.ksponco.or.kr/spm/tennis/tennis_wait_status.do")
web_data = loader.load()

prompt = f"""
base_data: {web_data}

Check if there are "available waiting slots" based on the following criteria:
- Weekdays after 19:00
- Anytime on weekends

Respond with only True if there are available slots, otherwise respond with False.
"""

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
chain = llm
result = chain.invoke(prompt)
if result.content == "False":
    print("No available slots")
    app.client.chat_postMessage(
        channel='C074SLJRGTS',
        text=f"응 돌아가",
    )
else:
    print("Available slots")
    app.client.chat_postMessage(
        channel='C074SLJRGTS',
        text=f"<@U0743SMPX3L> 올림픽 공원 달려가",
    )
