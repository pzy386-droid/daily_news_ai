import json
import csv
import re
import os
from datetime import datetime

def process_crawler_data(raw_file_path, output_format="csv"):
    """处理已存在的爬虫数据文件"""
    # 1. 读取已有爬虫数据
    print(f"读取数据文件：{raw_file_path}")
    if not os.path.exists(raw_file_path):
        raise FileNotFoundError(f"文件不存在：{raw_file_path}")
    
    with open(raw_file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    print(f"原始数据条数：{len(raw_data)}")

    # 2. 数据清洗
    cleaned_data = []
    seen = set()  # 去重标记
    for item in raw_data:
        # 去重：避免重复数据
        item_key = tuple(sorted(item.items()))
        if item_key in seen:
            continue
        seen.add(item_key)

        # 清洗文本（去除空格、特殊字符）
        clean_title = item.get("title", "").strip()
        clean_content = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？]", "", item.get("content", "").strip())
        
        # 清洗日期（统一为YYYY-MM-DD）
        date_str = item.get("publish_date", "")
        date_match = re.search(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})|(\d{1,2})[-/](\d{1,2})[-/](\d{4})", date_str)
        clean_date = None
        if date_match:
            if date_match.group(1):
                clean_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
            else:
                clean_date = f"{date_match.group(6)}-{date_match.group(4).zfill(2)}-{date_match.group(5).zfill(2)}"
        
        # 清洗数值（提取纯数字）
        read_count = float(re.search(r"\d+", item.get("read_count", "0")).group()) if item.get("read_count") else 0
        comment_num = int(item.get("comment_num", "0")) if item.get("comment_num") else 0

        # 过滤无效数据（标题非空、日期有效、阅读量≥100）
        if clean_title and clean_date and read_count >= 100:
            cleaned_data.append({
                "标题": clean_title,
                "内容": clean_content,
                "发布日期": clean_date,
                "阅读量": read_count,
                "评论数": comment_num
            })

    print(f"清洗后有效数据条数：{len(cleaned_data)}")

    # 3. 保存处理结果
    output_dir = os.path.join(os.path.expanduser("~\\Desktop"), "processed_crawler_data")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(output_dir, f"processed_data_{timestamp}.{output_format}")

    if output_format == "csv":
        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cleaned_data[0].keys())
            writer.writeheader()
            writer.writerows(cleaned_data)
    elif output_format == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"处理结果已保存：{output_path}")
    return cleaned_data

if __name__ == "__main__":
    # 替换为你的爬虫数据文件路径（桌面的crawler_data.json）
    RAW_FILE = os.path.join(os.path.expanduser("~\\Desktop"), "crawler_data.json")
    # 执行处理（输出CSV格式）
    process_crawler_data(RAW_FILE, output_format="csv")