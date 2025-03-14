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


### crawl4ai 代码修改
需要修改一下playright的执行脚本
不使用f-string直接插入JavaScript代码
site-packages/crawl4ai/async_crawler_strategy.py文件
```python
    async def robust_execute_user_script():
        ...
        try:
            result = await page.evaluate(
                """
                (async () => {
                    try {
                        // 使用 Function 构造函数包装用户脚本，正确处理 script 变量
                        const executeScript = () => {
                            """ + script + """
                        };
                        const script_result = executeScript();
                        return { success: true, result: script_result };
                    } catch (err) {
                        return { success: false, error: err.toString(), stack: err.stack };
                    }
                })();
                """
            )
```



## Usage

marketwatch_calendar.py
[marketwatch](https://www.marketwatch.com/economy-politics/calendar)


investing_calendar.py
[investing](https://www.investing.com/economic-calendar/)
(html, markdown数据爬取已完成，未完成解析部份)