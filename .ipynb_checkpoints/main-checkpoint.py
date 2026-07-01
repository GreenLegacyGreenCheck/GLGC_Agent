import sys
import asyncio
import uvicorn
import json
import os
import requests  
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
    print(f"총 {len(pages_data)}개의 데이터를 LLM으로 분석합니다. (API 속도 제한 방지를 위해 천천히 진행됩니다...)")
    
    for idx, item in enumerate(pages_data):
        extracted_json = await analyze_and_extract(item['content'], item['url'])
        
        if extracted_json:
            print(f"[{idx+1}/{len(pages_data)}] ✅ 추출 성공: {extracted_json.get('name', '이름 없음')}")
            valid_data_list.append(extracted_json)
        else:
            print(f"[{idx+1}/{len(pages_data)}] ❌ 스킵됨: {item['url']}")
            
        if idx < len(pages_data) - 1:
            await asyncio.sleep(4.5)
            
    # 3. 파일 저장 (로컬 백업용)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(valid_data_list, f, ensure_ascii=False, indent=4)
        

    try:
        RAG_SERVER_URL = "https://glgc-rag.onrender.com/update-data" 
        
        payload = {"new_data": valid_data_list} 
        
        print("RAG 서버로 데이터를 전송합니다...")
        response = requests.post(RAG_SERVER_URL, json=payload)
        
        if response.status_code == 200:
            print("RAG 서버 DB 업데이트 성공:", response.json())
        else:
            print("전송 실패:", response.status_code, response.text)
            
    except Exception as e:
        print(f"RAG 서버 전송 중 에러 발생: {e}")
        
    return {"status": "success", "total_count": len(valid_data_list), "data": valid_data_list}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)