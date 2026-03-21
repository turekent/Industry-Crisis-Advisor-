"""
API路由：提供实时数据接口（简化版）
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


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


@router.get("/news/realtime", response_model=NewsResponse)
async def get_realtime_news():
    """
    获取实时市场新闻
    """
    try:
        logger.info("Fetching realtime market news...")
        
        # 创建搜索客户端
        ctx = new_context(method="get_realtime_news")
        client = SearchClient(ctx=ctx)
        
        all_news = []
        
        # 搜索关键市场指标
        indicators = ["布伦特原油价格", "LME铜价", "钯金价格", "集装箱运费"]
        
        for indicator in indicators:
            try:
                query = f"{indicator} 最新价格 2026"
                response = client.web_search(
                    query=query,
                    count=2,
                    need_summary=False
                )
                
                if response.web_items:
                    for item in response.web_items:
                        news_item = {
                            "type": "价格指标",
                            "title": item.title,
                            "source": item.site_name,
                            "url": item.url,
                            "snippet": item.snippet,
                            "time": item.publish_time or "刚刚"
                        }
                        all_news.append(news_item)
            except Exception as e:
                logger.warning(f"Failed to search {indicator}: {str(e)}")
                continue
        
        # 搜索中东局势
        try:
            query = "中东局势 供应链影响 原材料"
            response = client.web_search(
                query=query,
                count=3,
                need_summary=False
            )
            
            if response.web_items:
                for item in response.web_items:
                    news_item = {
                        "type": "局势动态",
                        "title": item.title,
                        "source": item.site_name,
                        "url": item.url,
                        "snippet": item.snippet,
                        "time": item.publish_time or "刚刚"
                    }
                    all_news.append(news_item)
        except Exception as e:
            logger.warning(f"Failed to search Middle East news: {str(e)}")
        
        return NewsResponse(
            success=True,
            data=all_news[:10],  # 返回最多10条
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message="获取成功"
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
