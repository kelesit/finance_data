import pandas as pd
import re
import os
from datetime import datetime

def extract_calendar_data(markdown_file):
    print(f"开始从 {markdown_file} 提取经济日历数据...")
    
    # 检查文件是否存在
    if not os.path.exists(markdown_file):
        print(f"错误: 文件 {markdown_file} 不存在!")
        return None
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None
    # 提取"本周"和"下周"部分的数据
    this_week_pattern = r"# This Week's Major U.S. Economic Reports.*?(?=# Next Week's Major)"
    next_week_pattern = r"# Next Week's Major U.S. Economic Reports.*?(?=# Last Week's|$)"
    
    this_week_section = re.search(this_week_pattern, content, re.DOTALL)
    next_week_section = re.search(next_week_pattern, content, re.DOTALL)
    
    if not this_week_section:
        print("警告: 未找到本周数据部分!")
    if not next_week_section:
        print("警告: 未找到下周数据部分!")

    this_week_data = parse_calendar_section(this_week_section.group(0)) if this_week_section else []
    next_week_data = parse_calendar_section(next_week_section.group(0)) if next_week_section else []
    
    # 合并数据并转换为DataFrame
    all_data = this_week_data + next_week_data
    df = pd.DataFrame(all_data, columns=['Date', 'Time', 'Report', 'Period', 'Actual', 'Forecast', 'Previous'])
    
    # 导出为CSV
    df.to_csv('us_economic_calendar.csv', index=False)
    print(f"已提取 {len(df)} 条经济数据记录并保存到 us_economic_calendar.csv")
    
    return df

def parse_calendar_section(section):

    calendar_df = pd.DataFrame(columns=['Date', 'Time(ET)', 'Report', 'Period', 'Actual', 'Forecast', 'Previous'])
    lines = section.strip().split('\n')
    data = []
    
    current_date = None
    for line in lines:
        # 跳过标题行和表格格式行
        if '# ' in line or '---|---' in line or 'Time (ET) | Report' in line:
            continue
        
        # 检查是否是日期行
        if '**' in line and ('MONDAY' in line or 'TUESDAY' in line or 'WEDNESDAY' in line 
                            or 'THURSDAY' in line or 'FRIDAY' in line):
            current_date = line.strip('* \n')
            continue
        
        # 解析数据行
        if '|' in line and current_date:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:  # 确保有足够的列
                time = parts[1].strip()
                report = parts[2].strip()
                period = parts[3].strip()
                actual = parts[4].strip()
                forecast = parts[5].strip()
                previous = parts[6].strip() if len(parts) > 6 else ""
                
                data.append([current_date, time, report, period, actual, forecast, previous])
    
    return data

if __name__ == "__main__":
    calendar_file = "d:/work/Study/finance_data/finance_calendar.md"
    df = extract_calendar_data(calendar_file)
    print(df.head())