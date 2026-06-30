import sys
import asyncio
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 내부 모듈 임포트
from scraper import scrape_all_pages
from agent import analyze_and_extract
from config import TARGET_SITE

app = FastAPI(title="GLGC 크롤링 에이전트 API")

# 크롤링 결과를 담아둘 인메모리 캐시
crawled_data_cache = []

@app.get("/api/crawled-data")
async def get_crawled_data(refresh: bool = False):
    global crawled_data_cache
    if crawled_data_cache and not refresh:
        print("캐시된 데이터를 반환합니다.")
        return {
            "status": "success", 
            "total_count": len(crawled_data_cache), 
            "data": crawled_data_cache
        }
        
    print("새로운 크롤링 및 LLM 분석을 시작합니다...")
    
    # 1. 스크래핑 파이프라인 가동
    pages_data = await scrape_all_pages(TARGET_SITE)
    valid_data_list = []
    
    # 2. LLM 분석 파이프라인 가동
    for item in pages_data:
        extracted_json = await analyze_and_extract(item['content'], item['url'])
        if extracted_json:
            print(f"  ✅ 추출 성공: {extracted_json.get('name', '이름 없음')}")
            valid_data_list.append(extracted_json)
        else:
            print(f"  ⏭️ 스킵됨: {item['url']}")
            
    # 3. 결과 캐싱
    crawled_data_cache = valid_data_list
    
    return {
        "status": "success", 
        "total_count": len(crawled_data_cache), 
        "data": crawled_data_cache
    }
    

if __name__ == "__main__":
    import sys
    import asyncio
    

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
uvicorn.run(app, host="127.0.0.1", port=8001)