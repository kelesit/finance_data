
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime


def extract_table_data(html, table_title_pattern):
    soup = BeautifulSoup(html, 'html.parser')
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
    
    headers = []
    header_row = table.find('thead').find('tr')
    for th in header_row.find_all('th'):
        headers.append(th.text.strip())

    data = []
    current_date = None

    for tr in table.find('tbody').find_all('tr'):
        row_data = [td.text.strip() for td in tr.find_all('td')]

        # 检查是否是日期行
        if len(row_data) > 0 and re.search(r'\b(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY),', row_data[0]):
            current_date = row_data[0]
            continue

        if current_date and 'None scheduled' not in row_data[1]:
            complete_row = [current_date, row_data[0]] + row_data[1:]
            data.append(complete_row)

    if not data:
        print(f"未找到数据行")
        return None
    
    df_headers = ['Date', 'Time'] + headers[1:]
    df = pd.DataFrame(data, columns=df_headers)
    return df

def extract_html(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
        
    # 提取当前周数据
    this_week_df = extract_table_data(html, r"This Week's Major U\.S\. Economic Reports")
    
    # 提取下周数据
    next_week_df = extract_table_data(html, r"Next Week's Major U\.S\. Economic Reports")
    
    timestamp = datetime.now().strftime("%Y%m%d")
    # 同时保存为CSV文件
    csv_file_this_week = f"d:/work/Study/finance_data/us_economic_calendar_this_week_{timestamp}.csv"
    csv_file_next_week = f"d:/work/Study/finance_data/us_economic_calendar_next_week_{timestamp}.csv"
    
    if this_week_df is not None:
        this_week_df.to_csv(csv_file_this_week, index=False)
        print(f"本周数据已保存到 {csv_file_this_week}")
    
    if next_week_df is not None:
        next_week_df.to_csv(csv_file_next_week, index=False)
        print(f"下周数据已保存到 {csv_file_next_week}")

    return this_week_df, next_week_df

def extract_economic_calendar(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', id='economicCalendarData')
    if not table:
        print("未找到经济日历数据表格")
        return None
    
    data = []
    current_date = None

    for row in table.find_all('tr'):
        if 'theDay' in row.get('class', ''):
            date_text = row.get_text().strip()


    

def extract_html2(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    this_week_df = extract_economic_calendar(html)
    print(this_week_df)
    

if __name__ == "__main__":
    # html_file = "finance_calendar.html"
    html_file = '/Users/hsy/Work/finance_data/output/investing_calendar/this_week_raw_20250318_212015.html'
    # this_week_df, next_week_df = extract_html(html_file)
    extract_html2(html_file=html_file)
    print("Done!")

