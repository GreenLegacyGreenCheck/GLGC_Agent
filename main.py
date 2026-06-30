import sys
import asyncio
import uvicorn
import json
import os
from fastapi import FastAPI
from scraper import scrape_all_pages
from agent import analyze_and_extract
from config import TARGET_SITE

# 윈도우 비동기 에러 방지 설정
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="GLGC 에너지 정보 API")
DATA_FILE = "analyzed_data.json"

@app.get("/api/crawled-data")
async def get_crawled_data(refresh: bool = False):
    if not refresh and os.path.exists(DATA_FILE):
        print("기존 데이터를 반환합니다.")
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return {"status": "success", "data": json.load(f)}
            
    print("새로운 크롤링 및 LLM 분석을 시작합니다...")
    
    # 1. 스크래핑
    pages_data = await scrape_all_pages(TARGET_SITE)
    valid_data_list = []
    
    # 2. 분석
    for item in pages_data:
        extracted_json = await analyze_and_extract(item['content'], item['url'])
        if extracted_json:
            print(f"추출 성공: {extracted_json.get('name', '이름 없음')}")
            valid_data_list.append(extracted_json)
        else:
            print(f"스킵됨: {item['url']}")
            
    # 3. 파일 저장
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(valid_data_list, f, ensure_ascii=False, indent=4)
        
    return {"status": "success", "total_count": len(valid_data_list), "data": valid_data_list}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)