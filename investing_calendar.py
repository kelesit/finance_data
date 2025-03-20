from pathlib import Path
from datetime import datetime
import json
import asyncio
import pandas as pd
from bs4 import BeautifulSoup

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode


class InvestingCalendarCrawler:
    """https://www.investing.com/economic-calendar/ 爬虫"""

    DEFAULT_OUTPUT_DIR = Path("output/investing_calendar")
    DEFAULT_URL = "https://www.investing.com/economic-calendar/"
    DEFAULT_USER_DATA_PATH = Path(__file__).parent / "chrome_profile"

    def __init__(self,
                 output_dir=None,
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

        # 浏览器配置
        self.browser_config = self._get_browser_config()
        
        # 存储爬取结果
        self.html_content = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.this_week_raw_html = None
        self.next_week_raw_html = None
        self.this_week_cleaned_html = None
        self.next_week_cleaned_html = None
        self.this_week_md = None
        self.next_week_md = None

    def _get_browser_config(self):
        """获取浏览器配置"""
        return BrowserConfig(
            headless=self.headless,
            verbose=True,
            use_managed_browser=True,
            user_data_dir=str(self.user_data_path),
            browser_type="chromium",
        )
    
    async def run(self):
        """运行爬虫"""
        try:
            session_id = "investing_calendar"
            base_wait = """js:() => {
                const table = document.querySelector('#economicCalendarData');
                return table && table.rows.length > 1;
            }"""

            # 1. 加载页面，等待表格加载完成
            config1 = CrawlerRunConfig(
                wait_for=base_wait,
                session_id=session_id,
                cache_mode=CacheMode.BYPASS,
            )

            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(
                    url=self.url,
                    config=config1
                )
                print("页面加载完成")
                # print(result.cleaned_html)

                try:
                    # 2. 控制过滤器, 选择国家等其他条件
                    country_ids = [
                        '37',   #中国
                        '25',  #澳大利亚
                        '6',   #加拿大
                        '35', # 日本  
                        '5', # 美国
                        '72', #欧盟
                        ]
                    contry_ids_json = json.dumps(country_ids)
                    js_filter = f"""
                    var selector = document.querySelector('#filterStateAnchor');
                    if (selector) selector.click();

                    setTimeout(() => {{
                    
                        // 先清除默认选中
                        document.querySelectorAll('input[id^="country"]').forEach(cb => cb.checked = false);

                        // 选择国家
                        const countryCheckboxes = document.querySelectorAll('input[id^="country"]');
                        countryCheckboxes.forEach(cb => {{
                            const id = cb.id.replace('country', '');
                            if ({contry_ids_json}.includes(id)) {{
                                cb.checked = true;
                            }}
                        }});

                        // 选择种类
                        // TODO
                        // 选择重要程度
                        // TODO
                        // 点击应用
                        const submit_btn = document.querySelector('#ecSubmitButton');
                        submit_btn.click();

                    }}, 1000);  //给1秒等待过滤器面板展开
                    """

#                     js_filter = f"""
# var selector = document.querySelector('#filterStateAnchor');
# if (selector) selector.click();

# setTimeout(() => {{

#     // 先清除默认选中
#     document.querySelectorAll('input[id^="country"]').forEach(cb => cb.checked = false);

#     // 选择国家
#     const countryCheckboxes = document.querySelectorAll('input[id^="country"]');
#     countryCheckboxes.forEach(cb => {{
#         const id = cb.id.replace('country', '');
#         if (["37", "25", "6", "35", "5", "72"].includes(id)) {{
#             cb.checked = true;
#         }}
#     }});

#     // 选择种类
#     // TODO
#     // 选择重要程度
#     // TODO
#     // 点击应用
#     const submit_btn = document.querySelector('#ecSubmitButton');
#     submit_btn.click();

# }}, 1000);  //给1秒等待过滤器面板展开
# """
                    wait_for_load = """js:() => {
                        // #filtersWrapper 的display属性变为none时，过滤器加载完成
                        const filterWrapper = document.querySelector('#filtersWrapper');
                        return filterWrapper && filterWrapper.style.display === 'none';
                    }"""

                    config_filter = CrawlerRunConfig(
                        session_id=session_id,
                        js_code=js_filter,
                        wait_for=wait_for_load,
                        cache_mode=CacheMode.BYPASS,
                        js_only=True,   # 继续同一个浏览器会话
                    )
                    result_filter = await crawler.arun(
                        url=self.url,
                        config=config_filter
                    )
                    print("过滤器加载完成")
                    #print(result_filter.cleaned_html)

                    try:
                        # 3. 提取本周数据
                        js_this_week = """
                        const thisWeek_Btn = document.querySelector('#timeFrame_thisWeek');
                        if (thisWeek_Btn) thisWeek_Btn.click();
                        """

                        #economicCalendarData
                        # wait_for_this_week = """js:() => {
                        #     const table = document.querySelector('#economicCalendarData');
                        #     return table && table.rows.length > 1;
                        # }"""
                        wait_for_this_week = """js:() => {
                            const loading = document.querySelector('#economicCalendarLoading');
                            return loading && loading.style.display === 'none';
                        }"""
                        # wait_for_this_week = """js:() => {
                        #     const dayHeaders = document.querySelectorAll('tr[id^="theDay"]');
                        #     return dayHeaders.length >=5
                        # }"""

                        config_this_week = CrawlerRunConfig(
                            session_id=session_id,
                            js_code=js_this_week,
                            wait_for=wait_for_this_week,
                            cache_mode=CacheMode.BYPASS,
                            js_only=True,
                        )
                        result_this_week = await crawler.arun(
                            url=self.url,
                            config=config_this_week
                        )
                        print("本周数据加载完成")
                        self.this_week_raw_html = result_this_week.html
                        self.this_week_cleaned_html = result_this_week.cleaned_html
                        self.this_week_md = result_this_week.markdown
                        # 4. 提取下周数据
                        js_next_week = """
                        const nextWeek_Btn = document.querySelector('#timeFrame_nextWeek');
                        if (nextWeek_Btn) nextWeek_Btn.click();
                        """

                        wait_for_next_week = """js:() => {
                            const loading = document.querySelector('#economicCalendarLoading');
                            return loading && loading.style.display === 'none';
                        }"""

                        config_next_week = CrawlerRunConfig(
                            session_id=session_id,
                            js_code=js_next_week,
                            wait_for=wait_for_next_week,
                            cache_mode=CacheMode.BYPASS,
                            js_only=True,
                        )
                        result_next_week = await crawler.arun(
                            url=self.url,
                            config=config_next_week
                        )
                        print("下周数据加载完成")
                        self.next_week_raw_html = result_next_week.html
                        self.next_week_cleaned_html = result_next_week.cleaned_html
                        self.next_week_md = result_next_week.markdown

                        print("爬取完成")
                        return True
                    except Exception as e:
                        print(f"数据提取失败: {e}")
                        return False
                
                except Exception as e:
                    print(f"过滤器调整失败: {e}")
                    return False

        except Exception as e:
            print(f"首页加载失败: {e}")
            return False
        
    def save_results(self):
        """保存爬取结果"""
        if self.this_week_raw_html:
            with open(self.output_dir / f"this_week_raw_{self.timestamp}.html", "w", encoding="utf-8") as f:
                f.write(self.this_week_raw_html)
        if self.next_week_raw_html:
            with open(self.output_dir / f"next_week_raw_{self.timestamp}.html", "w", encoding="utf-8") as f:
                f.write(self.next_week_raw_html)
        if self.this_week_cleaned_html:
            with open(self.output_dir / f"this_week_cleaned_{self.timestamp}.html", "w", encoding="utf-8") as f:
                f.write(self.this_week_cleaned_html)
        if self.next_week_cleaned_html:
            with open(self.output_dir / f"next_week_cleaned_{self.timestamp}.html", "w", encoding="utf-8") as f:
                f.write(self.next_week_cleaned_html)
        if self.this_week_md:
            with open(self.output_dir / f"this_week_{self.timestamp}.md", "w", encoding="utf-8") as f:
                f.write(self.this_week_md)
        if self.next_week_md:
            with open(self.output_dir / f"next_week_{self.timestamp}.md", "w", encoding="utf-8") as f:
                f.write(self.next_week_md)
        print("结果保存成功")

    def extract_economic_calendar(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', id='economicCalendarData')
        if not table:
            print("未找到经济日历数据表格")
            return None
        
        data = []
        current_date = None

        for row in table.find_all('tr'):
            day_td = row.find('td', class_='theDay')
            if day_td:
                date_text = row.get_text().strip()
                try:
                    current_date = datetime.strptime(date_text, '%A, %B %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    current_date = date_text
                continue

            if 'js-event-item' in row.get('class', []):
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue

                time_cell = cells[0].get_text().strip() if len(cells) > 0 else""

                country = cells[1].find('span').get('title')
                currency = cells[1].get_text().strip()
                importance = ""
                bull_icons = cells[2].find_all('i', class_='grayFullBullishIcon')
                importance = len(bull_icons) if bull_icons else 0

                event = ""
                event_link = cells[3].find('a')
                event = event_link.get_text().strip()

                actual = cells[4].get_text().strip()
                forecast = cells[5].get_text().strip()
                previous = cells[6].get_text().strip()

                event_data = {
                    'Date': current_date,
                    'Time': time_cell,
                    'Country': country,
                    'Currency': currency,
                    'Importance': importance,
                    'Event': event,
                    'Event Link': event_link.get('href'),
                    'Actual': actual,
                    'Forecast': forecast,
                    'Previous': previous
                }
                data.append(event_data)

        if data:
            return pd.DataFrame(data)
        else:
            return None

    def extract2csv(self):
        this_week_html_file = self.output_dir / f"this_week_raw_{self.timestamp}.html"
        next_week_html_file = self.output_dir / f"next_week_raw_{self.timestamp}.html"

        with open(this_week_html_file, 'r', encoding='utf-8') as f:
            this_week_html_content = f.read()

        with open(next_week_html_file, 'r', encoding='utf-8') as f:
            next_week_html_content = f.read()

        this_week_df = self.extract_economic_calendar(this_week_html_content)
        next_week_df = self.extract_economic_calendar(next_week_html_content)

        if this_week_df is not None:
            csv_file_this_week = self.output_dir / f"investing_calendar_this_week_{self.timestamp}.csv"
            this_week_df.to_csv(csv_file_this_week, index=False)
            print(f"本周数据已保存到 {csv_file_this_week}")

        if next_week_df is not None:
            csv_file_next_week = self.output_dir / f"investing_calendar_next_week_{self.timestamp}.csv"
            next_week_df.to_csv(csv_file_next_week, index=False)
            print(f"下周数据已保存到 {csv_file_next_week}")

        return this_week_df, next_week_df

async def main():
    crawler = InvestingCalendarCrawler()
    success = await crawler.run()
    if success:
        crawler.save_results()
        print("爬取数据保存成功")
        crawler.extract2csv()
        print('Done!')
        return 0
    else:
        return 1


if __name__ == "__main__":
    asyncio.run(main())

    """
    待解决的疑问：
    1. js_filter如果使用json.dumps()转换后运行，会大大延迟，60s左右才能完成，原因是什么？
    
    2. 
    javascript代码执行有问题，crawl4ai官方代码也运行不了。
    问题所在：
    /crawl4ai/async_crawler_strategy.py 
    robust_execute_user_script() 
    照例来讲不应该有问题，
    但是在这里会出现问题，原因是什么？"""