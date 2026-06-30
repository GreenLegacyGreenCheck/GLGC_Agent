from playwright.sync_api import sync_playwright

def get_page_info(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # 텍스트와 링크 수집
        content = page.inner_text("body")
        links = page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href)")
        
        browser.close()
        return content, list(set(links))