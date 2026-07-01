import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import extract_json_from_text

import os
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")

async def analyze_and_extract(content, base_url):
    prompt = f"""
    당신은 제공된 웹 페이지 텍스트를 분석하여 '에너지 지원사업' 정보를 추출하는 전문 데이터 분석가입니다.
    
    [🚨 스킵(Skip) 방지 절대 규칙 🚨]
    텍스트에 '지원', '에너지', '요금', '복지', '사업' 등의 단어나 정책 내용이 조금이라도 포함되어 있다면 절대 skip하지 마세요. 
    오직 '로그인 필요', '페이지 없음(404)', '접근 권한 없음' 같은 완전한 에러/빈 화면일 경우에만 {{"status": "skip"}}을 반환하세요.
    
    [추출 규칙 및 강제 할당]
    1. cause: 내용이 애매하더라도 반드시 ['냉방설비 노후화', '단열 불량', '절약시설 부재', '운영 습관'] 4개 중 가장 억지로라도 연관성 있는 1개를 무조건 선택하세요. (다른 단어 절대 사용 금지)
    2. target: 반드시 ['소상공인', '기후취약계층', '일반가구'] 3개 중 가장 범위가 겹치는 1개를 무조건 선택하세요. (예: 저소득층/노인 -> 기후취약계층, 일반시민/도민 -> 일반가구 로 강제 매칭)
    3. url: 텍스트 본문 내에 있는 '신청 사이트', '바로가기' 등의 실제 링크 주소를 찾아 우선 작성하고, 절대 못 찾겠으면 기본 URL({base_url})을 출력하세요.
    4. saving: 본문에 수치가 있다면 그 수치를 추출하고, 없다면 아래 [탄소 절감량 추정 가이드]를 참고하여 지원 내용(action_des)에 맞는 예상 절감 효과를 문자열로 출력하세요.
    5. 나머지 항목은 텍스트를 바탕으로 요약 및 추출하세요. 정보가 부족하면 "내용 없음"이라고 적되, 전체를 skip하지는 마세요.
    
    [탄소 절감량 추정 가이드]
    - 고효율 기기 교체 (냉난방기, 보일러, LED 등): "기존 설비 대비 약 20~30% 에너지 및 탄소 배출 절감 예상"
    - 단열/창호 개선 (건물 에너지 효율화): "난방 에너지 요구량 감소로 연간 약 15~25% 탄소 배출 절감 예상"
    - 신재생 에너지 설치 (태양광 등): "화석연료 대체로 직접적인 탄소 배출 대폭 감소 (연간 약 1~2톤 CO2 절감 예상)"
    - 행동 변화 및 진단 (에너지 컨설팅, 절약 캠페인): "운영 효율화를 통해 약 5~10% 탄소 배출 절감 예상"
    - 요금 지원 (바우처, 현금 지원 등 설비 변화 없음): "직접적인 탄소 절감 효과 산출 어려움 (비용 부담 완화 목적)"
    
    [JSON 출력 템플릿] (반드시 이 키 순서와 구조를 지킬 것)
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
    
    
    for attempt in range(3): # 에러 나면 최대 3번까지 스스로 재시도
        try:
            response = await model.generate_content_async(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            if not response.text:
                return None
                
            result_json = json.loads(response.text.strip())
            
            if result_json.get("status") == "skip":
                return None
                
            return result_json
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota" in error_msg:
                print(f"⚠️ 429 속도 제한 방어막 가동! 40초 대기 후 재시도합니다... (시도: {attempt+1}/3)")
                await asyncio.sleep(40)
            else:
                print(f"DEBUG_ERROR (LLM 분석 실패): {e}")
                return None
                
    return None