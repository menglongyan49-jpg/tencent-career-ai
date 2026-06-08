"""
工具函数模块
"""

def format_datetime(dt_str: str) -> str:
    """格式化日期时间"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y年%m月%d日 %H:%M")
    except:
        return dt_str


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def extract_keywords(text: str, min_length: int = 2) -> list:
    """简单关键词提取"""
    import re
    # 移除标点符号
    text = re.sub(r'[^\w\s]', ' ', text)
    # 分词
    words = text.split()
    # 过滤短词
    return [w for w in words if len(w) >= min_length]