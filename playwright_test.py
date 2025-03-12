from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
    )
    page = browser.new_page()
    page.goto("https://www.investing.com/economic-calendar/", wait_until="domcontentloaded")
    # page.goto("https://www.marketwatch.com/economy-politics/calendar", wait_until="domcontentloaded")
    page.screenshot(path="example.png")
    browser.close()