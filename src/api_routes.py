"""
API路由：提供实时数据接口
用于前端页面调用获取最新数据
"""
import os
import json
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# 导入工具
from tools.market_news import MarketNewsTool
from tools.price_api import PriceAPITool
from tools.cost_calculator import CostCalculatorTool

router = APIRouter(prefix="/api", tags=["api"])

# 初始化工具实例
market_news_tool = MarketNewsTool()
price_api_tool = PriceAPITool()
cost_calculator_tool = CostCalculatorTool()


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
    前端可以定时调用此接口刷新数据
    """
    try:
        logger.info("Fetching realtime market news...")
        
        # 调用市场新闻工具
        result = market_news_tool._run(query="战争局势 原材料价格 中东冲突")
        
        # 解析结果
        news_data = []
        if result:
            # 尝试解析JSON
            try:
                parsed = json.loads(result)
                if isinstance(parsed, list):
                    news_data = parsed
                elif isinstance(parsed, dict) and "news" in parsed:
                    news_data = parsed["news"]
            except:
                # 如果不是JSON，作为文本处理
                news_data = [{
                    "title": "市场动态",
                    "content": result,
                    "source": "系统",
                    "time": "刚刚"
                }]
        
        return NewsResponse(
            success=True,
            data=news_data,
            timestamp=_get_current_time(),
            message="获取成功"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch news: {str(e)}")
        return NewsResponse(
            success=False,
            data=[],
            timestamp=_get_current_time(),
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
        
        # 调用价格API工具
        result = price_api_tool._run(material=material)
        
        # 解析结果
        price_data = {}
        if result:
            try:
                price_data = json.loads(result)
            except:
                price_data = {"raw": result}
        
        return PriceResponse(
            success=True,
            data=price_data,
            timestamp=_get_current_time(),
            message="获取成功"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch price: {str(e)}")
        return PriceResponse(
            success=False,
            data={},
            timestamp=_get_current_time(),
            message=f"获取失败: {str(e)}"
        )


@router.get("/prices/all", response_model=PriceResponse)
async def get_all_prices():
    """
    获取所有关键原材料价格
    """
    try:
        logger.info("Fetching all material prices...")
        
        materials = ["copper", "aluminum", "oil", "palladium"]
        all_prices = {}
        
        for material in materials:
            try:
                result = price_api_tool._run(material=material)
                if result:
                    try:
                        all_prices[material] = json.loads(result)
                    except:
                        all_prices[material] = {"raw": result}
            except Exception as e:
                logger.warning(f"Failed to fetch {material}: {str(e)}")
                all_prices[material] = {"error": str(e)}
        
        return PriceResponse(
            success=True,
            data=all_prices,
            timestamp=_get_current_time(),
            message="获取成功"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch all prices: {str(e)}")
        return PriceResponse(
            success=False,
            data={},
            timestamp=_get_current_time(),
            message=f"获取失败: {str(e)}"
        )


@router.post("/analyze/industry")
async def analyze_industry(query: IndustryQuery):
    """
    分析指定行业的风险
    """
    try:
        logger.info(f"Analyzing industry: {query.industry}")
        
        # 调用成本计算工具
        result = cost_calculator_tool._run(
            industry=query.industry,
            scenario=query.detail or "默认场景"
        )
        
        # 解析结果
        analysis_data = {}
        if result:
            try:
                analysis_data = json.loads(result)
            except:
                analysis_data = {"analysis": result}
        
        return {
            "success": True,
            "industry": query.industry,
            "data": analysis_data,
            "timestamp": _get_current_time()
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze industry: {str(e)}")
        return {
            "success": False,
            "industry": query.industry,
            "error": str(e),
            "timestamp": _get_current_time()
        }


@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "service": "Industry Risk Advisor API",
        "timestamp": _get_current_time()
    }


def _get_current_time() -> str:
    """获取当前时间字符串"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
