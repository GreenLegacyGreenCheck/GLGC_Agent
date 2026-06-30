from playwright.sync_api import sync_playwright

def get_page_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        links = page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href)")
        browser.close()
        return content, links