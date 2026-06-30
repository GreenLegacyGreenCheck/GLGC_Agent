import os
from dotenv import load_dotenv

# 로컬 개발용 
load_dotenv()

# 환경 변수
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 크롤링 타겟 사이트
TARGET_SITE = "https://www.e-policy.or.kr/web/lay1/program/S1T9C14/curation/list.do"