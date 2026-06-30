import google.generativeai as genai
import json

genai.configure(api_key="GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

def analyze_and_extract(content, url):
    prompt = f"""
    당신은 지원사업 정보를 추출하는 전문 에이전트입니다. 
    제공된 웹 페이지 텍스트를 분석하여 아래 JSON 형식으로 정보를 추출하세요.
    페이지가 공고나 신청 페이지가 아니라면 'skip'을 반환하세요.
    
    필수 데이터: 
    - target (소상공인/일반가구/기후취약계층), action_name, action_des, source(주관처), takes(사업 신청 시 받을 수 있는 것, time(신청 기간), need(신청에 필요한 서류), level(난이도)
    
    텍스트: {content[:10000]}
    url: {url}
    
    JSON 형식만 반환하세요:
    """
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text.replace('```json', '').replace('```', ''))
    except:
        return None