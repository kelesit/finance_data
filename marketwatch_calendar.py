"""
MarketWatch 经济日历数据爬虫
爬取 MarketWatch 网站的经济日历数据，包括美国主要经济报告和美联储讲话日程
同时解析数据并保存为结构化CSV格式
"""

import asyncio
import logging
from pathlib import Path
import argparse
from datetime import datetime
import re
import pandas as pd
from bs4 import BeautifulSoup

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

class MarketWatchCalendarCrawler:
    """MarketWatch 经济日历数据爬虫"""

    DEFAULT_OUTPUT_DIR = Path("output/marketwatch_calendar")
    DEFAULT_URL = "https://www.marketwatch.com/economy-politics/calendar"
    DEFAULT_USER_DATA_PATH = Path(__file__).parent / "chrome_profile"
    DEFAULT_THIS_WEEK_CSS_SELECTOR = "#maincontent > div:nth-child(1) > div.region.region--primary > div:nth-child(4) > div > div > table"
    DEFAULT_NEXT_WEEK_CSS_SELECTOR = "#maincontent > div:nth-child(1) > div.region.region--primary > div:nth-child(6) > div > div > table"

    # 表格标题匹配模式
    THIS_WEEK_TITLE = r"This Week's Major U\.S\. Economic Reports"
    NEXT_WEEK_TITLE = r"Next Week's Major U\.S\. Economic Reports"

    def __init__(self,
                output_dir = None,
                user_data_path=None,
                headless=False,
                url=None):
        """
        初始化爬虫
        
        Args:
            output_dir:输出目录
            user_data_path:Chrome 用户配置数据目录 （防止人机验证）
            headless:是否启用无头模式
            url:爬取的 URL
        """
        self.output_dir = Path(output_dir) if output_dir else self.DEFAULT_OUTPUT_DIR
        self.user_data_path = Path(user_data_path) if user_data_path else self.DEFAULT_USER_DATA_PATH
        self.headless = headless
        self.url = url if url else self.DEFAULT_URL

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 爬虫配置
        self.browser_config = self._get_browser_config()
        self.run_config = self._get_crawler_run_config()

        # 存储爬取结果
        self.html_content = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_browser_config(self):
        """获取浏览器配置"""
        return BrowserConfig(
            headless=self.headless,
            verbose=True,
            use_managed_browser=True,
            user_data_dir=str(self.user_data_path),
            browser_type="chromium",
        )
    
    def _get_crawler_run_config(self):
        """获取爬虫运行配置"""
        return CrawlerRunConfig(
            magic=True,  # 自动处理弹窗等
            simulate_user=True,  # 模拟用户行为
            override_navigator=True,
            # css_selector=self.DEFAULT_CSS_SELECTOR,  # 只获取经济日历部分
            word_count_threshold=10,  # 内容块最小字数
            exclude_external_links=True,  # 移除外部链接
            remove_overlay_elements=True,  # 移除弹窗
            process_iframes=True  # 处理iframe内容
        )
    
    async def crawl(self):
        """执行爬虫"""
        print(f"开始爬取 {self.url}")
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=self.url, config=self.run_config)

            if not result.success:
                print(f"爬取失败：{result.error}")
                print(f"状态码: {result.status_code}")
                return False
            
            print("爬取成功!")
            self.html_content = result.html
            self._save_result(result)
            return True
        except Exception as e:
            print(f"爬取失败: {e}")
            return False
        
    def _save_result(self, result):
        """保存爬取结果"""
        timestamp = self.timestamp
        # 保存 Markdown 格式
        md_path = self.output_dir / f"finance_calendar_{timestamp}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print(f"Markdown 已保存至: {md_path}")
        
        # 保存原始 HTML
        html_path = self.output_dir / f"finance_calendar_{timestamp}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"HTML 已保存至: {html_path}")
        
        # 保存清理后的 HTML
        clean_html_path = self.output_dir / f"finance_calendar_clean_{timestamp}.html"
        with open(clean_html_path, "w", encoding="utf-8") as f:
            f.write(result.cleaned_html)
        print(f"清理后的 HTML 已保存至: {clean_html_path}")


    def extract_table_data(self, table_title_pattern):
        """
        从HTML中提取特定标题下的表格数据
        
        Args:
            table_title_pattern: 标题的正则表达式匹配模式
            
        Returns:
            pandas.DataFrame: 提取的表格数据，如果未找到则返回None
        """
        if not self.html_content:
            print("HTML内容为空，请先运行爬虫")
            return None
            
        soup = BeautifulSoup(self.html_content, 'html.parser')
        titles_elements = soup.find_all('h1')
        target_title = None
        
        for title in titles_elements:
            if re.search(table_title_pattern, title.text):
                target_title = title
                break
                
        if target_title is None:
            print(f"未找到标题: {table_title_pattern}")
            return None
        
        table = target_title.find_next('table')
        if not table:
            print(f"在标题'{target_title.text}'后未找到表格")
            return None
        
        # 提取表头
        headers = []
        header_row = table.find('thead').find('tr')
        for th in header_row.find_all('th'):
            headers.append(th.text.strip())

        # 提取表格数据
        data = []
        current_date = None

        for tr in table.find('tbody').find_all('tr'):
            row_data = [td.text.strip() for td in tr.find_all('td')]

            # 检查是否是日期行
            if len(row_data) > 0 and re.search(r'\b(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY),', row_data[0]):
                current_date = row_data[0]
                continue

            if current_date and 'None scheduled' not in " ".join(row_data):
                complete_row = [current_date, row_data[0]] + row_data[1:]
                data.append(complete_row)

        if not data:
            print(f"未找到数据行")
            return None
        
        df_headers = ['Date', 'Time'] + headers[1:]
        df = pd.DataFrame(data, columns=df_headers)
        return df
    
    def extract_calendar_data(self):
        """提取经济日历数据"""
        if not self.html_content:
            print("HTML内容为空，请先运行爬虫")
            return None
        
        this_week_df = self.extract_table_data(self.THIS_WEEK_TITLE)
        next_week_df = self.extract_table_data(self.NEXT_WEEK_TITLE)

        # 保存为CSV文件
        if this_week_df is not None:
            csv_file_this_week = self.output_dir / f"us_economic_calendar_this_week_{self.timestamp}.csv"
            this_week_df.to_csv(csv_file_this_week, index=False)
            print(f"本周数据已保存到 {csv_file_this_week}")
        
        if next_week_df is not None:
            csv_file_next_week = self.output_dir / f"us_economic_calendar_next_week_{self.timestamp}.csv"
            next_week_df.to_csv(csv_file_next_week, index=False)
            print(f"下周数据已保存到 {csv_file_next_week}")
            
        return this_week_df, next_week_df


async def main():
    parser = argparse.ArgumentParser(description="MarketWatch 经济日历数据爬虫")
    parser.add_argument("--output_dir", type=str, help="输出目录")
    parser.add_argument("--user_data_path", type=str, help="Chrome 用户配置数据目录")
    parser.add_argument("--headless", action="store_true", help="是否启用无头模式")
    parser.add_argument("--url", type=str, help="爬取的 URL")
    args = parser.parse_args()

    crawler = MarketWatchCalendarCrawler(
        output_dir=args.output_dir,
        user_data_path=args.user_data_path,
        headless=args.headless,
        url=args.url
    )

    success = await crawler.crawl()

    if success:
        this_week_df, next_week_df = crawler.extract_calendar_data()
        print("Done!")
        return 0
    else:
        return  1


if __name__ == "__main__":
    asyncio.run(main())