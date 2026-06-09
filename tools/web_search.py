"""
网络搜索工具 - 为 Agent 提供实时信息获取能力
支持 Tavily API（推荐）和 DuckDuckGo（免费备选）
"""
import os
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import json


class WebSearchTool(ABC):
    """网络搜索工具基类"""

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        执行搜索
        返回: [{"title": str, "content": str, "url": str}]
        """
        pass

    def format_results(self, results: List[Dict], max_length: int = 2000) -> str:
        """格式化搜索结果为文本"""
        if not results:
            return "未找到相关搜索结果。"

        output = []
        total_length = 0

        for i, r in enumerate(results):
            entry = f"【{i+1}】{r.get('title', '无标题')}\n"
            entry += f"来源: {r.get('url', '未知')}\n"
            entry += f"摘要: {r.get('content', '无内容')[:500]}\n"

            if total_length + len(entry) > max_length:
                break

            output.append(entry)
            total_length += len(entry)

        return "\n".join(output)


class TavilySearchTool(WebSearchTool):
    """Tavily 搜索工具（推荐）

    特点：
    - 专为 AI Agent 设计
    - 返回结构化、干净的结果
    - 免费额度：1000 次/月

    使用前需要设置环境变量：TAVILY_API_KEY
    获取 API Key: https://tavily.com
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            print("警告: 未设置 TAVILY_API_KEY，搜索功能将不可用")

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self.api_key)
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",  # basic 或 advanced
                include_answer=True,   # 包含 AI 生成的答案摘要
            )

            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "url": item.get("url", ""),
                })

            # 如果有 AI 生成的答案摘要，放在第一位
            if response.get("answer"):
                results.insert(0, {
                    "title": "AI 摘要答案",
                    "content": response["answer"],
                    "url": "Tavily AI",
                })

            return results

        except ImportError:
            print("请安装 tavily: pip install tavily-python")
            return []
        except Exception as e:
            print(f"Tavily 搜索出错: {e}")
            return []


class DuckDuckGoSearchTool(WebSearchTool):
    """DuckDuckGo 搜索工具（免费备选）

    特点：
    - 完全免费，无需 API Key
    - 结果质量一般
    - 适合演示和测试
    """

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "content": r.get("body", ""),
                        "url": r.get("href", ""),
                    })

            return results

        except ImportError:
            print("请安装 duckduckgo-search: pip install duckduckgo-search")
            return []
        except Exception as e:
            print(f"DuckDuckGo 搜索出错: {e}")
            return []


class MockSearchTool(WebSearchTool):
    """模拟搜索工具（用于演示，无需真实 API）"""

    MOCK_DATA = {
        "腾讯": [
            {
                "title": "腾讯2025校园招聘启动",
                "content": "腾讯2025届校园招聘已于2024年8月正式启动，面向2025届应届毕业生。技术类岗位包括后端开发、前端开发、算法工程师等。",
                "url": "https://join.qq.com",
            },
            {
                "title": "腾讯暑期实习招聘时间",
                "content": "腾讯暑期实习通常在每年3-5月开放申请，面向大三、研一、研二学生。",
                "url": "https://join.qq.com/intern",
            },
        ],
        "面试": [
            {
                "title": "2025年互联网面试趋势",
                "content": "2025年互联网面试更注重项目实战经验，算法题难度适中，系统设计题比重增加。",
                "url": "https://example.com/interview-trends",
            },
        ],
    }

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """模拟搜索，根据关键词返回预设数据"""
        results = []
        for keyword, data in self.MOCK_DATA.items():
            if keyword in query:
                results.extend(data[:max_results])

        if not results:
            # 返回通用模拟结果
            results = [{
                "title": f"关于「{query}」的搜索结果",
                "content": f"这是关于「{query}」的模拟搜索结果。在实际部署时，将使用真实的搜索 API 获取实时信息。",
                "url": "https://example.com",
            }]

        return results[:max_results]


def get_search_tool(tool_type: str = "auto") -> WebSearchTool:
    """获取搜索工具实例

    Args:
        tool_type: "tavily" | "duckduckgo" | "mock" | "auto"

    Returns:
        WebSearchTool 实例
    """
    if tool_type == "tavily":
        return TavilySearchTool()
    elif tool_type == "duckduckgo":
        return DuckDuckGoSearchTool()
    elif tool_type == "mock":
        return MockSearchTool()
    else:  # auto
        # 优先尝试 Tavily
        if os.getenv("TAVILY_API_KEY"):
            return TavilySearchTool()
        # 其次尝试 DuckDuckGo
        try:
            from duckduckgo_search import DDGS
            return DuckDuckGoSearchTool()
        except ImportError:
            # 最后使用 Mock
            return MockSearchTool()


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 测试搜索工具
    tool = get_search_tool("mock")

    print("=" * 50)
    print("测试搜索: 腾讯2025校招时间")
    print("=" * 50)

    results = tool.search("腾讯2025校招时间")
    print(tool.format_results(results))