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
    crawl4ai-doctor
    ```

    This command attempts to: - Check Python version compatibility - Verify Playwright installation - Inspect environment variables or library conflicts

    If any issues arise, follow its suggestions (e.g., installing additional system packages) and re-run crawl4ai-setup.

4. Create and use persistent browser profiles
    ```bash
    # macOS example
    playwright install --dry-run    # 得到Playwright Chromium二进制文件地址

    mkdir -p /Users/hsy/Work/finance_data/chrome_profile    # 创建用户数据目录

    /Users/hsy/Library/Caches/ms-playwright/chromium-1155/chrome-mac/Chromium.app/Contents/MacOS/Chromium --user-data-dir=/Users/hsy/Work/finance_data/chrome_profile    # 启动浏览器，登录marketwatch网站，完成人机验证，然后关闭浏览器
    ```

    *details*: <https://docs.crawl4ai.com/advanced/identity-based-crawling/>

    
    ```bash
    # Windows example
    # Find the Playwright Chromium binary
    playwright install --dry-run

    # Launch the Playwright Chromium binary with a custom user-data directory
    # Windows example
    & "C:\Users\baycheer\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe" --user-data-dir="D:\work\Study\finance_data\chrome_profile"
    ```

## Usage

目前只有一个爬虫，爬取`https://www.marketwatch.com/economy-politics/calendar`的日历数据。

marketwatch_calendar.py

[invest](https://www.investing.com/economic-calendar/)网站的数据爬取还在开发中。
investing_calendar.py
investing_calendar copy.py