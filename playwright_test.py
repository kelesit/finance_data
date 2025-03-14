from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
    )
    page = browser.new_page()
    page.goto("https://www.investing.com/economic-calendar/", wait_until="domcontentloaded")
    # page.goto("https://www.marketwatch.com/economy-politics/calendar", wait_until="domcontentloaded")
    page.screenshot(path="example.png")

    script = """
    const table = document.querySelector('#economicCalendarData');
    return table && table.rows.length > 1;
    """

    # result = page.evaluate("""
    # (() => {
    #     try {
    #         const table = document.querySelector('#economicCalendarData');
    #         const hasData = table && table.rows.length > 1;
    #         return { success: true, result: hasData };
    #     } catch (err) {
    #         return { success: false, error: err.toString(), stack: err.stack };
    #     }
    # })()
    # """)

    result = page.evaluate(
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

    browser.close()