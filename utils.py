import json
import re

def extract_json_from_text(text):
    """LLM 응답에서 순수 JSON만 추출하여 파싱합니다."""
    try:
        clean_text = re.sub(r'```json', '', text)
        clean_text = re.sub(r'```', '', clean_text).strip()
        
        return json.loads(clean_text)
    except Exception as e:
        print(f"JSON 파싱 실패 (원본 텍스트 일부: {text[:50]}...): {e}")
        return None