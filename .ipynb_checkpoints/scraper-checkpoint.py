import asyncio
from playwright.async_api import async_playwright

async def scrape_all_pages(base_url):
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("1. 메인 페이지 접속 중...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=120000)
        
        links = await page.evaluate("Array.from(document.querySelectorAll('a.curating__con')).map(a => a.href)")
        links = list(set(links))
        
        print(f"총 {len(links)}개의 상세 페이지 링크를 찾았습니다.")
        
        for idx, link in enumerate(links):
            print(f"[{idx+1}/{len(links)}] 스크래핑 중: {link}")
            try:
                await page.goto(link, wait_until="domcontentloaded", timeout=120000)
                await page.wait_for_timeout(2000) 
                
                content = await page.inner_text("body")
                results.append({"url": link, "content": content})
            except Exception as e:
                print(f"페이지 로드 실패 ({link}): {e}")
                
        await browser.close()
        
    return results