import pandas as pd
import numpy as np
import json
from datetime import datetime

# 读取CSV文件
df = pd.read_csv('AAPL_100DAYS.CSV')
print(f"数据行数: {len(df)}")

# 确保列名正确
df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

# 转换日期列
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date').reset_index(drop=True)

# 计算基本指标
total_days = len(df)
date_range_start = df['Date'].min().strftime('%Y-%m-%d')
date_range_end = df['Date'].max().strftime('%Y-%m-%d')

# YTD收益率 (以第一天收盘价为基准)
first_close = df.iloc[0]['Close']
last_close = df.iloc[-1]['Close']
ytd_return = ((last_close - first_close) / first_close) * 100

# 日均成交量
avg_volume = int(df['Volume'].mean())

# 区间最高价及日期
max_price_row = df.loc[df['High'].idxmax()]
max_price = max_price_row['High']
max_price_date = max_price_row['Date'].strftime('%Y-%m-%d')

# 区间最低价及日期
min_price_row = df.loc[df['Low'].idxmin()]
min_price = min_price_row['Low']
min_price_date = min_price_row['Date'].strftime('%Y-%m-%d')

# 平均日内振幅 (High - Low) / 前日收盘价 × 100%
df['PrevClose'] = df['Close'].shift(1)
# 跳过第一行（没有前日收盘价）
df['DailyRange'] = ((df['High'] - df['Low']) / df['PrevClose']) * 100
avg_daily_range = df['DailyRange'].mean()

# 涨跌天数
df['Change'] = df['Close'] - df['Open']
up_days = len(df[df['Change'] > 0])
down_days = len(df[df['Change'] < 0])

# 移动平均线
df['MA5'] = df['Close'].rolling(window=5).mean()
df['MA20'] = df['Close'].rolling(window=20).mean()

# 成交量最大的3个交易日
volume_top3 = df.nlargest(3, 'Volume')[['Date', 'Volume', 'Close', 'Open']].copy()
volume_top3['ChangePct'] = ((volume_top3['Close'] - volume_top3['Open']) / volume_top3['Open']) * 100
volume_top3['Date'] = volume_top3['Date'].dt.strftime('%Y-%m-%d')

# 趋势分析：最近10个交易日 vs 前10个交易日
last_10 = df.tail(10)
first_10 = df.head(10)
last_10_return = ((last_10['Close'].iloc[-1] - last_10['Close'].iloc[0]) / last_10['Close'].iloc[0]) * 100
first_10_return = ((first_10['Close'].iloc[-1] - first_10['Close'].iloc[0]) / first_10['Close'].iloc[0]) * 100

# 整体趋势判断
price_change = last_close - first_close
if price_change > 0:
    trend = "上涨"
elif price_change < 0:
    trend = "下跌"
else:
    trend = "震荡"

# 支撑与阻力位（简化版：近期高点和低点）
recent_lows = df.tail(20)['Low'].nsmallest(3).values.tolist()
recent_highs = df.tail(20)['High'].nlargest(3).values.tolist()

# 日内振幅较大的交易日（前5个）
df['IntradayRange'] = df['High'] - df['Low']
high_range_days = df.nlargest(5, 'IntradayRange')[['Date', 'IntradayRange', 'Close']].copy()
high_range_days['Date'] = high_range_days['Date'].dt.strftime('%Y-%m-%d')

# 准备图表数据
chart_data = {
    'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
    'opens': df['Open'].tolist(),
    'highs': df['High'].tolist(),
    'lows': df['Low'].tolist(),
    'closes': df['Close'].tolist(),
    'volumes': df['Volume'].tolist(),
    'ma5': df['MA5'].fillna(0).tolist(),
    'ma20': df['MA20'].fillna(0).tolist(),
    'volumeChanges': (df['Close'] > df['Open']).tolist()  # True表示上涨，False表示下跌
}

# 输出指标
print("=== 关键指标 ===")
print(f"总交易天数: {total_days}")
print(f"日期范围: {date_range_start} 至 {date_range_end}")
print(f"YTD收益率: {ytd_return:.2f}%")
print(f"日均成交量: {avg_volume:,}")
print(f"区间最高价: {max_price:.2f} ({max_price_date})")
print(f"区间最低价: {min_price:.2f} ({min_price_date})")
print(f"平均日内振幅: {avg_daily_range:.2f}%")
print(f"涨跌天数: 上涨{up_days}天, 下跌{down_days}天")
print(f"整体趋势: {trend}")
print(f"最近10个交易日涨跌幅: {last_10_return:.2f}%")
print(f"前10个交易日涨跌幅: {first_10_return:.2f}%")
print(f"近期支撑位 (低点): {recent_lows}")
print(f"近期阻力位 (高点): {recent_highs}")

print("\n=== 成交量最大3个交易日 ===")
for idx, row in volume_top3.iterrows():
    print(f"{row['Date']}: 成交量{row['Volume']:,}, 涨跌幅{row['ChangePct']:.2f}%")

print("\n=== 日内振幅最大5个交易日 ===")
for idx, row in high_range_days.iterrows():
    print(f"{row['Date']}: 振幅{row['IntradayRange']:.2f}, 收盘价{row['Close']:.2f}")

# 保存指标为JSON文件，供HTML使用
output = {
    'total_days': total_days,
    'date_range_start': date_range_start,
    'date_range_end': date_range_end,
    'ytd_return': round(ytd_return, 2),
    'avg_volume': avg_volume,
    'max_price': round(max_price, 2),
    'max_price_date': max_price_date,
    'min_price': round(min_price, 2),
    'min_price_date': min_price_date,
    'avg_daily_range': round(avg_daily_range, 2),
    'up_days': up_days,
    'down_days': down_days,
    'trend': trend,
    'last_10_return': round(last_10_return, 2),
    'first_10_return': round(first_10_return, 2),
    'recent_lows': [round(x, 2) for x in recent_lows],
    'recent_highs': [round(x, 2) for x in recent_highs],
    'volume_top3': volume_top3.to_dict('records'),
    'high_range_days': high_range_days.to_dict('records'),
    'chart_data': chart_data
}

with open('aapl_metrics.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n指标已保存到 aapl_metrics.json")