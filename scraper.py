import asyncio
from playwright.async_api import async_playwright
import json

# 저장 기능을 담당하는 별도 함수
def save_to_json(data, filename="crawled_data.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"파일 저장 완료: {filename}")

async def scrape_all_pages(base_url):
    results = []
    all_links = set() 
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("1. 전체 1~8페이지 상세 링크 수집 시작...")
        
        for current_page in range(1, 9):
            clean_base_url = base_url.split('?')[0]
            page_url = f"{clean_base_url}?rows=9&cpage={current_page}"
            
            print(f"[{current_page}/8] 목록 페이지 접속 중...")
            try:
                await page.goto(page_url, wait_until="domcontentloaded", timeout=120000)
                
                try:
                    await page.wait_for_selector('a.curating__con', timeout=10000)
                except Exception:
                    print(f"{current_page}페이지가 너무 느리거나 링크가 없습니다. 다음 페이지로 넘어갑니다.")
                    continue  
                
                links = await page.evaluate("Array.from(document.querySelectorAll('a.curating__con')).map(a => a.href)")
                
                if not links:
                    print(f"{current_page}페이지에 더 이상 수집할 링크가 없습니다.")
                    break
                    
                all_links.update(links)
                print(f"{len(links)}개 링크 추가 완료 (현재 누적: {len(all_links)}개)")
                
            except Exception as e:
                print(f"{current_page}페이지 목록 로드 실패: {e}")
                
        # set을 다시 list로 변환
        all_links = list(all_links)
        print(f"\n총 {len(all_links)}개의 상세 페이지 링크 수집을 완료했습니다!")
        
        print("\n2. 상세 페이지 내용(Content) 추출 시작...")
        
        for idx, link in enumerate(all_links):
            print(f"[{idx+1}/{len(all_links)}] 스크래핑 중: {link}")
            try:
                await page.goto(link, wait_until="domcontentloaded", timeout=120000)
                await page.wait_for_timeout(2000) 
                
                content = await page.inner_text("body")
                results.append({"url": link, "content": content})
            except Exception as e:
                print(f"페이지 로드 실패 ({link}): {e}")
                
        await browser.close()
   
    return results