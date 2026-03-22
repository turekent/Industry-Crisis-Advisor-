"""
API路由：提供实时数据接口（优化版 - 优先获取权威来源）
"""
import os
import json
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# 权威来源配置
AUTHORITATIVE_SOURCES = {
    # 国际顶级财经媒体（Tier 1）
    "bloomberg.com": {"name": "彭博社", "tier": 1, "icon": "📊"},
    "reuters.com": {"name": "路透社", "tier": 1, "icon": "📰"},
    "wsj.com": {"name": "华尔街日报", "tier": 1, "icon": "📈"},
    "ft.com": {"name": "金融时报", "tier": 1, "icon": "💹"},
    
    # 国内权威财经媒体（Tier 2）
    "caixin.com": {"name": "财新网", "tier": 2, "icon": "📰"},
    "yicai.com": {"name": "第一财经", "tier": 2, "icon": "💹"},
    "eastmoney.com": {"name": "东方财富", "tier": 2, "icon": "📊"},
    "finance.sina.com.cn": {"name": "新浪财经", "tier": 2, "icon": "📈"},
    "wallstreetcn.com": {"name": "华尔街见闻", "tier": 2, "icon": "💹"},
    
    # 社交媒体大V（Tier 3）
    "twitter.com": {"name": "X/Twitter", "tier": 3, "icon": "🐦"},
    "x.com": {"name": "X/Twitter", "tier": 3, "icon": "🐦"}
}

# 著名财经大V账号
INFLUENTIAL_ACCOUNTS = [
    "zerohedge",      # 零对冲
    "business",       # 彭博商业
    "Reuters",        # 路透社官方
    "wolfstreet",     # Wolf Street
    "jessefelder"     # Jesse Felder
]


class IndustryQuery(BaseModel):
    """行业查询请求"""
    industry: str
    detail: str = ""


class NewsResponse(BaseModel):
    """新闻响应"""
    success: bool
    data: List[Dict[str, Any]]
    timestamp: str
    message: str = ""


class PriceResponse(BaseModel):
    """价格响应"""
    success: bool
    data: Dict[str, Any]
    timestamp: str
    message: str = ""


def get_source_info(url: str) -> Dict[str, Any]:
    """从URL提取来源信息"""
    if not url:
        return {"name": "未知来源", "tier": 4, "icon": "📄"}
    
    for domain, info in AUTHORITATIVE_SOURCES.items():
        if domain in url:
            return info
    
    return {"name": "其他来源", "tier": 4, "icon": "📄"}


@router.get("/news/realtime", response_model=NewsResponse)
async def get_realtime_news():
    """
    获取实时市场新闻（优先权威来源）
    """
    try:
        logger.info("Fetching realtime market news from authoritative sources...")
        
        # 创建搜索客户端
        ctx = new_context(method="get_realtime_news")
        client = SearchClient(ctx=ctx)
        
        all_news = []
        seen_titles = set()
        
        # 获取今天的日期
        today = date.today().strftime("%Y-%m-%d")
        
        # 1. 优先搜索顶级权威来源（彭博社、路透社、华尔街日报）
        tier1_queries = [
            f"site:bloomberg.com OR site:reuters.com OR site:wsj.com 原油价格 OR oil price {today}",
            f"site:bloomberg.com OR site:reuters.com 铜价格 OR copper price {today}",
            f"site:bloomberg.com OR site:reuters.com 中东局势 供应链 {today}"
        ]
        
        for query in tier1_queries:
            try:
                response = client.web_search(
                    query=query,
                    count=5,
                    need_summary=False
                )
                
                if response.web_items:
                    for item in response.web_items:
                        if item.title not in seen_titles:
                            source_info = get_source_info(item.url)
                            news_item = {
                                "type": "市场动态",
                                "title": item.title,
                                "source": source_info["name"],
                                "source_icon": source_info["icon"],
                                "source_tier": source_info["tier"],
                                "url": item.url,
                                "snippet": item.snippet,
                                "time": item.publish_time or "今天"
                            }
                            all_news.append(news_item)
                            seen_titles.add(item.title)
            except Exception as e:
                logger.warning(f"Failed to search tier1 sources: {str(e)}")
                continue
        
        # 2. 搜索X/Twitter大V观点
        twitter_query = f"site:twitter.com OR site:x.com 石油价格 OR oil price OR 中东局势 {today}"
        try:
            response = client.web_search(
                query=twitter_query,
                count=5,
                need_summary=False
            )
            
            if response.web_items:
                for item in response.web_items:
                    if item.title not in seen_titles:
                        source_info = get_source_info(item.url)
                        news_item = {
                            "type": "大V观点",
                            "title": item.title,
                            "source": source_info["name"],
                            "source_icon": source_info["icon"],
                            "source_tier": source_info["tier"],
                            "url": item.url,
                            "snippet": item.snippet,
                            "time": item.publish_time or "今天"
                        }
                        all_news.append(news_item)
                        seen_titles.add(item.title)
        except Exception as e:
            logger.warning(f"Failed to search Twitter: {str(e)}")
        
        # 3. 搜索国内权威财经媒体
        tier2_queries = [
            f"site:eastmoney.com OR site:finance.sina.com.cn OR site:wallstreetcn.com 原油价格 {today}",
            f"site:caixin.com OR site:yicai.com 中东局势 影响 {today}",
            f"site:eastmoney.com 铜价 铝价 {today}"
        ]
        
        for query in tier2_queries:
            try:
                response = client.web_search(
                    query=query,
                    count=3,
                    need_summary=False
                )
                
                if response.web_items:
                    for item in response.web_items:
                        if item.title not in seen_titles:
                            source_info = get_source_info(item.url)
                            news_item = {
                                "type": "市场动态",
                                "title": item.title,
                                "source": source_info["name"],
                                "source_icon": source_info["icon"],
                                "source_tier": source_info["tier"],
                                "url": item.url,
                                "snippet": item.snippet,
                                "time": item.publish_time or "今天"
                            }
                            all_news.append(news_item)
                            seen_titles.add(item.title)
            except Exception as e:
                logger.warning(f"Failed to search tier2 sources: {str(e)}")
                continue
        
        # 4. 补充搜索（综合来源）
        general_queries = [
            f"布伦特原油价格 {today}",
            f"LME铜价 铝价 {today}",
            f"钯金价格 黄金价格 {today}",
            f"SCFI集装箱运费 {today}",
            f"中东局势 供应链影响 {today}"
        ]
        
        for query in general_queries:
            try:
                response = client.web_search(
                    query=query,
                    count=3,
                    need_summary=False
                )
                
                if response.web_items:
                    for item in response.web_items:
                        if item.title not in seen_titles:
                            source_info = get_source_info(item.url)
                            news_item = {
                                "type": "市场动态",
                                "title": item.title,
                                "source": source_info["name"],
                                "source_icon": source_info["icon"],
                                "source_tier": source_info["tier"],
                                "url": item.url,
                                "snippet": item.snippet,
                                "time": item.publish_time or "今天"
                            }
                            all_news.append(news_item)
                            seen_titles.add(item.title)
            except Exception as e:
                logger.warning(f"Failed to search general sources: {str(e)}")
                continue
        
        # 按权威性排序（tier越小越权威）
        all_news.sort(key=lambda x: (x.get("source_tier", 4), x.get("time", "")))
        
        # 限制返回20条
        all_news = all_news[:20]
        
        return NewsResponse(
            success=True,
            data=all_news,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message=f"获取成功，共{len(all_news)}条新闻"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch news: {str(e)}")
        return NewsResponse(
            success=False,
            data=[],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message=f"获取失败: {str(e)}"
        )


@router.get("/prices/{material}", response_model=PriceResponse)
async def get_material_price(material: str):
    """
    获取指定材料的价格
    支持的材料：copper, aluminum, oil, gold, silver, palladium
    """
    try:
        logger.info(f"Fetching price for: {material}")
        
        # 创建搜索客户端
        ctx = new_context(method="get_material_price")
        client = SearchClient(ctx=ctx)
        
        material_names = {
            "copper": "LME铜价",
            "aluminum": "沪铝价格",
            "oil": "布伦特原油价格",
            "gold": "黄金价格",
            "silver": "白银价格",
            "palladium": "钯金价格"
        }
        
        name = material_names.get(material, material)
        query = f"{name} 最新价格 2026"
        
        response = client.web_search(
            query=query,
            count=3,
            need_summary=False
        )
        
        price_data = {
            "material": material,
            "name": name,
            "sources": []
        }
        
        if response.web_items:
            for item in response.web_items:
                price_data["sources"].append({
                    "title": item.title,
                    "source": item.site_name,
                    "url": item.url,
                    "snippet": item.snippet
                })
        
        return PriceResponse(
            success=True,
            data=price_data,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message="获取成功"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch price: {str(e)}")
        return PriceResponse(
            success=False,
            data={},
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message=f"获取失败: {str(e)}"
        )


@router.get("/prices/all", response_model=PriceResponse)
async def get_all_prices():
    """
    获取所有关键原材料价格
    """
    try:
        logger.info("Fetching all material prices...")
        
        materials = {
            "copper": "LME铜价",
            "aluminum": "沪铝价格",
            "oil": "布伦特原油价格",
            "palladium": "钯金价格"
        }
        
        all_prices = {}
        
        # 创建搜索客户端
        ctx = new_context(method="get_all_prices")
        client = SearchClient(ctx=ctx)
        
        for material, name in materials.items():
            try:
                query = f"{name} 最新价格 2026"
                response = client.web_search(
                    query=query,
                    count=3,
                    need_summary=False
                )
                
                price_data = {
                    "material": material,
                    "name": name,
                    "price": "--",
                    "change": 0,
                    "sources": []
                }
                
                if response.web_items:
                    for item in response.web_items:
                        price_data["sources"].append({
                            "title": item.title,
                            "source": item.site_name,
                            "url": item.url,
                            "snippet": item.snippet
                        })
                        
                        # 尝试从标题或摘要中提取价格
                        import re
                        # 匹配价格模式，如：11930美元/吨 或 112.04美元/桶
                        price_patterns = [
                            r'(\d+\.?\d*)\s*美元/吨',
                            r'(\d+\.?\d*)\s*美元/桶',
                            r'(\d+\.?\d*)\s*元/吨',
                            r'报价(\d+\.?\d*)',
                            r'(\d+\.?\d*)\s*美元/盎司'
                        ]
                        
                        for pattern in price_patterns:
                            match = re.search(pattern, item.title + item.snippet)
                            if match:
                                price_data["price"] = match.group(1)
                                break
                
                all_prices[material] = price_data
                
            except Exception as e:
                logger.warning(f"Failed to fetch {material}: {str(e)}")
                all_prices[material] = {
                    "material": material,
                    "name": name,
                    "price": "--",
                    "error": str(e)
                }
        
        return PriceResponse(
            success=True,
            data=all_prices,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message="获取成功"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch all prices: {str(e)}")
        return PriceResponse(
            success=False,
            data={},
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message=f"获取失败: {str(e)}"
        )


@router.post("/analyze/industry")
async def analyze_industry(query: IndustryQuery):
    """
    分析指定行业的风险
    """
    try:
        logger.info(f"Analyzing industry: {query.industry}")
        
        # 创建搜索客户端
        ctx = new_context(method="analyze_industry")
        client = SearchClient(ctx=ctx)
        
        # 搜索该行业的风险信息
        search_query = f"{query.industry} 中东局势 影响 原材料 价格风险"
        response = client.web_search_with_summary(
            query=search_query,
            count=5
        )
        
        analysis_data = {
            "industry": query.industry,
            "summary": response.summary if hasattr(response, 'summary') else "",
            "sources": []
        }
        
        if response.web_items:
            for item in response.web_items:
                analysis_data["sources"].append({
                    "title": item.title,
                    "source": item.site_name,
                    "url": item.url,
                    "snippet": item.snippet
                })
        
        return {
            "success": True,
            "industry": query.industry,
            "data": analysis_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze industry: {str(e)}")
        return {
            "success": False,
            "industry": query.industry,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "service": "Industry Risk Advisor API",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
