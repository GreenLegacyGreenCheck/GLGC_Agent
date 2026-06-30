import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import extract_json_from_text

import os
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")

async def analyze_and_extract(content, url):
    prompt = f"""
    당신은 텍스트를 읽고 '에너지 지원사업' 정보를 추출하는 전문 AI 에이전트입니다. 
    제공된 웹 페이지 텍스트를 분석하여 아래 JSON 형식에 맞춰 데이터를 추출하세요.
    페이지가 지원사업 내용이 아니라면 "skip" 이라고만 대답하세요.
    
    [추출할 JSON 키 값 설명]
    - cause: 사업 목적 (예: 냉방설비, 난방설비, 단열 불량, 친환경 설비, 절약시설, 운영 습관 중 택 1)
    - name: 사업 공식 명칭
    - url: {url}
    - target: 지원 대상 (소상공인, 기후취약계층, 일반가구 중 택 1)
    - action_name: 지원 내용 요약 (15자 이내)
    - action_des: 지원 상세 내용
    - source: 주관 기관 (예: 한국전력공사, 한국에너지공단, 특정 구청 등)
    - takes: 사업 신청 시 받을 수 있는 혜택
    - time: 신청 기간
    - need: 신청에 필요한 서류나 방법
    - level: 난이도 (어려움, 중간, 쉬움 중 택 1)
    - saving: 탄소 절감 효과 (알 수 없으면 "기존 설비 대비 절감"으로 작성)
    
    [규칙]
    반드시 JSON 객체 하나만 반환하세요.
    
    텍스트:
    {content[:10000]}
    """
    
    try:
        response = await model.generate_content_async(prompt)
        
        if not response.text:
            return None
        return extract_json_from_text(response.text.strip())
    except Exception as e:
        print(f"DEBUG_ERROR: {e}")
        return None