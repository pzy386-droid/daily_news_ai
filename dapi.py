import urllib.request
import json
from typing import Dict, Optional

# 替换为你的信息
QWEN_API_KEY = "sk-909b3f9181f847e499e78f23b68a17fb"  # 从控制台复制的sk-开头密钥
QWEN_MODEL = "qwen-plus"  # 模型名称（如qwen-plus）
# 对应文档中的Base URL（国内地域）
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# 爬虫数据
crawled_data: Dict[str, str] = {
    "title": "Attention Is All You Need",
    "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
    "category": "计算机科学（AI/自然语言处理）"
}

# 口播稿Prompt
prompt_template: str = """
任务：将arXiv爬虫数据转化为5分钟专业口语口播稿（2000字左右）
风格：专业不生硬，像资深学长分享，带“说实话”“你懂的”等自然口语垫词,用英语
结构要求：
1. 开场（1句）：学科+标题切入
2. 核心（3-4句）：提炼痛点+1-2个创新点+实际价值
3. 结尾（1句）：互动引导
输入数据：
标题：{title}
摘要：{abstract}
学科：{category}
直接输出口播稿！
"""

def generate_script(crawled_data: Dict[str, str]) -> Optional[str]:
    prompt: str = prompt_template.format(**crawled_data)
    # 文档指定的兼容模式请求格式
    payload: Dict[str, any] = {
        "model": QWEN_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 800
    }
    data: bytes = json.dumps(payload).encode("utf-8")
    
    # 认证方式（文档要求的Authorization格式）
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {QWEN_API_KEY}"
    }
    req = urllib.request.Request(QWEN_BASE_URL, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"❌ 错误详情：{str(e)}")
        return None

if __name__ == "__main__":
    print("💡 generating the script...")
    script = generate_script(crawled_data)
    if script:
        print(f"\n✅ successful ：\n{'-'*60}\n{script}")
        
        # 新增：把口播稿保存到文件
        output_file = "output_script.txt"  # 文件名可以自定义
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(script)
        print(f"\n📝 it was saved as：{output_file}")  # 提示保存成功
    else:
        print("❌ 生成失败")