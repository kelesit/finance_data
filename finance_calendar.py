import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig ,CrawlerRunConfig
import os
from pathlib import Path

"""测试crawl4ai使用的demo"""


"""
爬取MarketWatch的日历数据
"""

async def main():
    user_data_path = r"D:\work\Study\finance_data\chrome_profile"
    
    browser_config = BrowserConfig( # 设置浏览器配置
        headless=False,
        verbose=True,
        use_managed_browser=True,
        user_data_dir=user_data_path,
        browser_type="chromium",
        )
    run_config = CrawlerRunConfig(  # 设置爬虫行为
        magic=True, # 自动处理弹窗等（实验性功能）
        simulate_user=True, # 模拟用户行为(鼠标移动等)
        override_navigator=True,
        
        # 设置css_selector, 只要This Week's Major U.S. Economic Reports & Fed Speakers部分 
        css_selector="#maincontent > div:nth-child(1) > div.region.region--primary > div:nth-child(4) > div > div > table > tbody",
        word_count_threshold=10,        # Minimum words per content block
        exclude_external_links=True,    # Remove external links
        remove_overlay_elements=True,   # Remove popups/modals
        process_iframes=True           # Process iframe content
    )


    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.marketwatch.com/economy-politics/calendar",
            config = run_config
        )
        
    if not result.success:  # 爬取失败
        print(f"Crawl failed: {result.error_message}")
        print(f"Status code: {result.status_code}")

    else:
        print("Crawl successful!")

        # result.markdown: 自动提取的Markdown格式文本 -- 会受到css_selector的影响
        with open("finance_calendar.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print("Done")

        # result.html: 原始HTML  -- 不会受到css_selector的影响, 保留完整的HTML
        with open("finance_calendar.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print("Done")

        # result.cleaned_html: 清理后的HTML -- 会受到css_selector的影响
        with open("finance_calendar_clean.html", "w", encoding="utf-8") as f:
            f.write(result.cleaned_html)



if __name__ == "__main__":
    asyncio.run(main())