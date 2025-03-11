# 金融数据爬取

## setup

使用uv管理python环境

1. Basic package installation

    ```bash
    uv sync
    ```

2. Install playwright browsers, confirms your environment is ready to crawl

    ```bash
    crawl4ai-setup
    ```

3. Diagnostics

    ```bash
    crawl4ai-diagnostics
    ```

    This command attempts to: - Check Python version compatibility - Verify Playwright installation - Inspect environment variables or library conflicts

    If any issues arise, follow its suggestions (e.g., installing additional system packages) and re-run crawl4ai-setup.

4. Create and use persistent browser profiles
    由于反爬虫机制，需要先使用`& "C:\Users\baycheer\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe" --user-data-dir="D:\work\Study\finance_data\chrome_profile"`启动浏览器，登录网站，完成人机验证，然后关闭浏览器。再使用`crawl4ai`进行爬取。
    非常重要，否则会被反爬虫机制拦截。
    *details*: <https://docs.crawl4ai.com/advanced/identity-based-crawling/>

    Workflow
    1. Login externally (via CLI or your normal Chrome with --user-data-dir=...).
    2. Close that browser.
    3. Use the same folder in user_data_dir= in Crawl4AI.
    4. Crawl – The site sees your identity as if you’re the same user who just logged in.

    ```bash
    # Find the Playwright Chromium binary
    playwright install --dry-run

    # Launch the Playwright Chromium binary with a custom user-data directory
    # Windows example
    & "C:\Users\baycheer\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe" --user-data-dir="D:\work\Study\finance_data\chrome_profile"
    ```

## Usage

目前只有一个爬虫，爬取`https://www.marketwatch.com/economy-politics/calendar`的日历数据。

finance_calendar.py
