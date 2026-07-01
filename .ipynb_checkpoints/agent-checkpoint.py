import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import extract_json_from_text

import os
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-pro")

async def analyze_and_extract(content, base_url):
    prompt = f"""
    당신은 제공된 웹 페이지 텍스트를 분석하여 '에너지 지원사업' 정보를 추출하는 전문 데이터 분석가입니다.
    아래 [추출 규칙]과 [탄소 절감량 추정 가이드], 그리고 [JSON 출력 템플릿]을 엄격하게 준수하여 데이터를 추출하세요.
    지원사업 내용이 아니라고 판단되면 {{"status": "skip"}} 만 반환하세요.
    
    [추출 규칙]
    1. cause: 반드시 ['냉방설비 노후화', '단열 불량', '절약시설 부재', '운영 습관'] 4개 중 텍스트와 가장 연관성 높은 1개만 출력.
    2. target: 반드시 ['소상공인', '기후취약계층', '일반가구'] 3개 중 가장 적합한 1개만 출력.
    3. url: 텍스트 본문 내에 있는 '신청 사이트', '바로가기' 등의 실제 링크 주소를 최우선으로 추출하고, 없다면 기본 URL({base_url})을 출력.
    4. saving: 본문에 수치가 있다면 그 수치를 추출하고, 없다면 [탄소 절감량 추정 가이드]를 참고하여 지원 내용(action_des)에 맞는 예상 절감 효과를 문자열로 출력.
    5. 나머지 항목은 텍스트를 바탕으로 요약 및 추출.
    6. 반환하는 JSON의 키(Key) 순서는 템플릿과 100% 동일해야 함.

    [탄소 절감량 추정 가이드]
    - 고효율 기기 교체 (냉난방기, 보일러, LED 등): "기존 설비 대비 약 20~30% 에너지 및 탄소 배출 절감 예상"
    - 단열/창호 개선 (건물 에너지 효율화): "난방 에너지 요구량 감소로 연간 약 15~25% 탄소 배출 절감 예상"
    - 신재생 에너지 설치 (태양광 등): "화석연료 대체로 직접적인 탄소 배출 대폭 감소 (연간 약 1~2톤 CO2 절감 예상)"
    - 행동 변화 및 진단 (에너지 컨설팅, 절약 캠페인): "운영 효율화를 통해 약 5~10% 탄소 배출 절감 예상"
    - 요금 지원 (에너지 바우처, 현금 지원 등 직접적인 설비 변화가 없는 경우): "직접적인 탄소 절감 효과 산출 어려움 (비용 부담 완화 목적)"
    
    [JSON 출력 템플릿]
    {{
        "cause": "규칙에 따른 1개 값",
        "name": "사업 공식 명칭",
        "url": "본문 내 링크 또는 기본 URL",
        "target": "규칙에 따른 1개 값",
        "action_name": "지원 내용 요약 (15자 이내)",
        "action_des": "지원 상세 내용",
        "source": "주관 기관",
        "takes": "사업 신청 시 받을 수 있는 혜택",
        "time": "신청 기간",
        "need": "신청에 필요한 서류 (없으면 신청 방법)",
        "level": "어려움, 중간, 쉬움 중 택 1",
        "saving": "가이드를 바탕으로 한 예상 절감 효과"
    }}
    
    텍스트:
    {content[:10000]}
    """
    
    try:
        # 🚀 Gemini API 자체 기능으로 JSON 출력 강제하기
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response.text:
            return None
            
        result_json = json.loads(response.text.strip())
        
        # skip 처리된 경우 걸러내기
        if result_json.get("status") == "skip":
            return None
            
        return result_json
        
    except Exception as e:
        print(f"DEBUG_ERROR (LLM 분석 실패): {e}")
        return None