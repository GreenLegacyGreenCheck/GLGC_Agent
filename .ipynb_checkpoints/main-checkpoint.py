from scraper import get_page_info
from agent import analyze_and_extract
import time

visited = set()

def crawl(url, depth=0):
    if depth > 3 or url in visited: return
    visited.add(url)
    
    print(f"[{depth} 단계] 분석 중: {url}")
    content, links = get_page_info(url)
    
    # 1. LLM 분석
    result = analyze_and_extract(content, url)
    
    # 2. 결과 저장 및 출력
    if result and result != 'skip':
        print(f"데이터 추출 성공: {result.get('action_name')}")
        # 여기서 백엔드 API로 전송하거나 DB에 저장
    else:
        # 3. 재귀 탐색
        for next_url in links:
            if "e-policy.or.kr" in next_url: # 도메인 제한
                time.sleep(1)
                crawl(next_url, depth + 1)

if __name__ == "__main__":
    start_url = "https://www.e-policy.or.kr/web/lay1/program/S1T9C14/curation/list.do"
    crawl(start_url)