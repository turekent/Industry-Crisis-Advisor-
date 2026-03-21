"""
市场新闻和价格监控工具
获取最新的行业动态和大宗商品价格信息
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Dict, List, Optional
import json
from datetime import datetime


# 关键大宗商品和指标配置
MARKET_INDICATORS = {
    "布伦特原油": {
        "keywords": ["布伦特原油", "Brent原油", "国际油价", "原油价格"],
        "unit": "美元/桶",
        "importance": "极高"
    },
    "LME铜价": {
        "keywords": ["LME铜", "铜价", "铜期货", "电解铜价格"],
        "unit": "美元/吨",
        "importance": "高"
    },
    "钯金现货": {
        "keywords": ["钯金", "钯金价格", "贵金属"],
        "unit": "美元/盎司",
        "importance": "高"
    },
    "SCFI运费指数": {
        "keywords": ["SCFI", "集装箱运价", "海运费", "运费指数"],
        "unit": "指数点",
        "importance": "高"
    },
    "沪铝主力": {
        "keywords": ["沪铝", "铝价", "铝期货"],
        "unit": "元/吨",
        "importance": "中"
    }
}

# 六大行业的关键词配置
INDUSTRY_KEYWORDS = {
    "PCB": ["PCB", "印刷电路板", "覆铜板", "电解铜箔", "钯金"],
    "游艇": ["游艇", "树脂", "胶衣", "进口发动机", "船艇"],
    "生物医药": ["生物医药", "原料药", "API", "液氦", "医药"],
    "新型储能": ["新型储能", "锂电池", "PVDF", "电解液", "储能"],
    "打印耗材": ["打印耗材", "碳粉", "硒鼓", "墨盒", "塑料粒子"],
    "跨境电商": ["跨境电商", "集装箱运价", "航空燃油", "物流", "电商"]
}


@tool
def get_market_news(runtime: ToolRuntime = None) -> str:
    """
    获取最新的市场新闻和大宗商品价格信息
    包括原油、铜价、钯金、运费指数等关键指标
    
    Returns:
        返回JSON格式的市场新闻和价格信息
    """
    ctx = runtime.context if runtime else new_context(method="get_market_news")
    
    client = SearchClient(ctx=ctx)
    
    # 收集所有新闻
    all_news = []
    
    # 1. 搜索关键大宗商品价格
    for indicator, config in MARKET_INDICATORS.items():
        try:
            query = f"{indicator} 最新价格 2026"
            response = client.web_search(
                query=query,
                count=3,
                need_summary=False
            )
            
            if response.web_items:
                for item in response.web_items:
                    news_item = {
                        "type": "价格指标",
                        "indicator": indicator,
                        "title": item.title,
                        "source": item.site_name,
                        "url": item.url,
                        "snippet": item.snippet,
                        "publish_time": item.publish_time or "近期",
                        "importance": config["importance"],
                        "unit": config["unit"]
                    }
                    all_news.append(news_item)
        except Exception:
            continue
    
    # 2. 搜索各行业的最新动态
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        try:
            query = f"{' '.join(keywords[:2])} 最新动态 中东局势 影响"
            response = client.web_search(
                query=query,
                count=2,
                need_summary=False
            )
            
            if response.web_items:
                for item in response.web_items:
                    news_item = {
                        "type": "行业动态",
                        "industry": industry,
                        "title": item.title,
                        "source": item.site_name,
                        "url": item.url,
                        "snippet": item.snippet,
                        "publish_time": item.publish_time or "近期",
                        "importance": "高" if industry in ["PCB", "游艇", "生物医药"] else "中"
                    }
                    all_news.append(news_item)
        except Exception:
            continue
    
    # 3. 搜索中东局势对供应链的影响
    try:
        query = "中东局势 伊朗 供应链影响 原材料价格"
        response = client.web_search_with_summary(
            query=query,
            count=5
        )
        
        if response.web_items:
            for item in response.web_items:
                news_item = {
                    "type": "局势动态",
                    "indicator": "中东局势",
                    "title": item.title,
                    "source": item.site_name,
                    "url": item.url,
                    "snippet": item.snippet,
                    "publish_time": item.publish_time or "近期",
                    "importance": "极高"
                }
                all_news.append(news_item)
    except Exception:
        pass
    
    # 去重（基于标题）
    seen_titles = set()
    unique_news = []
    for news in all_news:
        if news["title"] not in seen_titles:
            seen_titles.add(news["title"])
            unique_news.append(news)
    
    # 按重要性排序
    importance_order = {"极高": 0, "高": 1, "中": 2}
    unique_news.sort(key=lambda x: importance_order.get(x.get("importance", "中"), 2))
    
    # 限制返回10条
    result_news = unique_news[:10]
    
    output = {
        "success": True,
        "total": len(result_news),
        "news": result_news,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return json.dumps(output, ensure_ascii=False, indent=2)


def get_market_news_direct() -> Dict:
    """
    直接获取市场新闻（不通过工具装饰器）
    用于API调用
    """
    try:
        ctx = new_context(method="get_market_news_direct")
        client = SearchClient(ctx=ctx)
        
        # 收集所有新闻
        all_news = []
        
        # 搜索中东局势对供应链的影响
        query = "中东局势 伊朗 战争 供应链 原材料价格 物流 2026"
        response = client.web_search_with_summary(
            query=query,
            count=10
        )
        
        if response.web_items:
            for item in response.web_items:
                news_item = {
                    "type": "局势动态",
                    "title": item.title,
                    "source": item.site_name,
                    "url": item.url,
                    "snippet": item.snippet[:100] + "..." if len(item.snippet) > 100 else item.snippet,
                    "publish_time": item.publish_time or "近期"
                }
                all_news.append(news_item)
        
        # 去重
        seen_titles = set()
        unique_news = []
        for news in all_news:
            if news["title"] not in seen_titles:
                seen_titles.add(news["title"])
                unique_news.append(news)
        
        return {
            "success": True,
            "total": len(unique_news[:10]),
            "news": unique_news[:10],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "news": [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
