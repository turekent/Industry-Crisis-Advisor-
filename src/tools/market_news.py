"""
市场新闻和价格监控工具（增强版）
获取最新的行业动态和大宗商品价格信息
支持混合数据源：专业API → 网络搜索 → 模拟数据
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Dict, List, Optional
import json
from datetime import datetime

# 导入价格API工具
from tools.price_api import get_realtime_prices, PRICE_SOURCES


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
    获取最新的市场新闻和大宗商品价格信息（混合方案）
    
    数据源优先级：
    1. 专业价格API（实时价格）
    2. 网络搜索（行业动态）
    3. 降级数据
    
    Returns:
        返回JSON格式的市场新闻和价格信息
    """
    ctx = runtime.context if runtime else new_context(method="get_market_news")
    
    client = SearchClient(ctx=ctx)
    
    # 收集所有新闻
    all_news = []
    
    # 1. 尝试从专业价格API获取实时价格
    try:
        from tools.price_api import get_realtime_prices
        import json as json_module
        
        # 获取所有关键指标的价格
        price_result_json = get_realtime_prices(runtime=runtime)
        price_result = json_module.loads(price_result_json)
        
        if price_result.get("success") and price_result.get("prices"):
            for price_data in price_result["prices"]:
                # 构建价格新闻项
                news_item = {
                    "type": "价格指标",
                    "indicator": price_data["indicator"],
                    "title": f"{price_data['indicator']} {'上涨' if price_data.get('direction') == 'up' else '下跌'} {price_data.get('change_rate', '0%')}",
                    "source": price_data.get("source_name", price_data.get("data_source", "未知来源")),
                    "url": price_data.get("source_url", ""),
                    "snippet": f"当前价格: {price_data.get('price', 'N/A')} {price_data['unit']}，涨跌幅: {price_data.get('change_rate', 'N/A')}，数据来源: {price_data.get('data_source', '未知')}",
                    "publish_time": price_data.get("publish_time", datetime.now().strftime("%Y-%m-%d %H:%M")),
                    "importance": PRICE_SOURCES.get(price_data["indicator"], {}).get("importance", "中"),
                    "unit": price_data["unit"],
                    "data_source": price_data.get("data_source", "未知"),
                    "confidence": price_data.get("confidence", 0),
                    "is_estimated": price_data.get("is_estimated", False)
                }
                all_news.append(news_item)
                
    except Exception as e:
        print(f"[价格API获取失败] {str(e)}，降级到网络搜索")
    
    # 2. 如果价格API失败，使用网络搜索补充
    if not any(news.get("type") == "价格指标" for news in all_news):
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
                            "unit": config["unit"],
                            "data_source": "网络搜索"
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
