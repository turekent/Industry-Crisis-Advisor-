"""
API路由：提供实时数据接口（增强版 - 更稳定、更可靠）
主要改进：
1. 添加重试机制（最多3次）
2. 添加请求超时（10秒）
3. 添加并发控制（最多同时3个请求）
4. 添加数据缓存（5分钟有效期）
5. 添加健康检查接口
6. 改进价格提取逻辑
"""
import os
import json
import logging
import asyncio
import re
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
import functools

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# ==================== 配置项 ====================
CONFIG = {
    "max_retries": 3,           # 最大重试次数
    "timeout": 10,              # 请求超时（秒）
    "cache_ttl": 300,           # 缓存有效期（秒）- 5分钟
    "max_concurrent": 3,        # 最大并发请求数
    "request_delay": 0.5        # 请求间隔（秒）- 防止限流
}

# ==================== 缓存系统 ====================
class SimpleCache:
    """简单的内存缓存"""
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if datetime.now() > item["expires_at"]:
            del self._cache[key]
            return None
        
        return item["data"]
    
    def set(self, key: str, data: Any, ttl: int = None):
        ttl = ttl or CONFIG["cache_ttl"]
        self._cache[key] = {
            "data": data,
            "expires_at": datetime.now() + timedelta(seconds=ttl)
        }
    
    def clear(self):
        self._cache.clear()

# 全局缓存实例
cache = SimpleCache()

# ==================== 并发控制 ====================
class ConcurrencyLimiter:
    """并发限制器"""
    def __init__(self, max_concurrent: int):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._lock = asyncio.Lock()
        self._request_count = 0
    
    async def acquire(self):
        await self._semaphore.acquire()
        async with self._lock:
            self._request_count += 1
            logger.info(f"并发请求数: {self._request_count}")
        # 添加延迟，防止限流
        await asyncio.sleep(CONFIG["request_delay"])
    
    def release(self):
        self._semaphore.release()

# 全局并发限制器
limiter = ConcurrencyLimiter(CONFIG["max_concurrent"])

# ==================== 权威来源配置 ====================
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

# ==================== 数据模型 ====================
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
    cached: bool = False

class PriceResponse(BaseModel):
    """价格响应"""
    success: bool
    data: Dict[str, Any]
    timestamp: str
    message: str = ""
    cached: bool = False

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    services: Dict[str, bool]
    uptime: str

# ==================== 工具函数 ====================
def get_source_info(url: str) -> Dict[str, Any]:
    """从URL提取来源信息"""
    if not url:
        return {"name": "未知来源", "tier": 4, "icon": "📄"}
    
    for domain, info in AUTHORITATIVE_SOURCES.items():
        if domain in url:
            return info
    
    return {"name": "其他来源", "tier": 4, "icon": "📄"}

async def retry_search(client: SearchClient, query: str, count: int = 5, need_summary: bool = False, max_retries: int = None):
    """
    带重试机制的搜索函数
    """
    max_retries = max_retries or CONFIG["max_retries"]
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # 使用 asyncio.wait_for 添加超时
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.web_search,
                    query=query,
                    count=count,
                    need_summary=need_summary
                ),
                timeout=CONFIG["timeout"]
            )
            return response
        except asyncio.TimeoutError:
            last_error = f"请求超时（{CONFIG['timeout']}秒）"
            logger.warning(f"Search timeout (attempt {attempt + 1}/{max_retries}): {query}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Search failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
        
        # 如果不是最后一次尝试，等待后重试
        if attempt < max_retries - 1:
            await asyncio.sleep(1 * (attempt + 1))  # 递增等待时间
    
    raise Exception(f"搜索失败（已重试{max_retries}次）: {last_error}")

def is_today_news(publish_time: str) -> bool:
    """
    判断新闻是否是今天的
    """
    if not publish_time:
        return False
    
    today = date.today()
    
    # 尝试解析各种时间格式
    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # 2024-01-01
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 2024年1月1日
        r'(\d{1,2})小时前',  # 5小时前
        r'(\d{1,2})分钟前',  # 30分钟前
        r'刚刚',
        r'今天'
    ]
    
    for pattern in patterns:
        if re.search(pattern, publish_time):
            # 如果是"小时前"、"分钟前"、"刚刚"、"今天"，都认为是今天的
            if pattern in [r'(\d{1,2})小时前', r'(\d{1,2})分钟前', r'刚刚', r'今天']:
                return True
            
            # 如果是具体日期，检查是否是今天
            match = re.search(pattern, publish_time)
            if match and len(match.groups()) >= 3:
                try:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    news_date = date(year, month, day)
                    return news_date == today
                except:
                    pass
    
    return False

def extract_price_from_text(text: str, material_type: str) -> Dict[str, Any]:
    """
    从文本中提取价格信息
    返回：{"price": 价格, "change": 涨跌幅, "unit": 单位}
    """
    result = {"price": "--", "change": "--", "unit": ""}
    
    # 价格提取规则
    price_patterns = {
        "oil": [
            (r'(\d+\.?\d*)\s*美元.*?桶', "美元/桶"),
            (r'(\d+\.?\d*)\s*USD.*?bbl', "美元/桶"),
        ],
        "copper": [
            (r'(\d+\.?\d*)\s*美元.*?吨', "美元/吨"),
            (r'LME.*?(\d+\.?\d*)', "美元/吨"),
        ],
        "aluminum": [
            (r'(\d+\.?\d*)\s*美元.*?吨', "美元/吨"),
            (r'沪铝.*?(\d+\.?\d*)', "元/吨"),
        ],
        "palladium": [
            (r'(\d+\.?\d*)\s*美元.*?盎司', "美元/盎司"),
        ],
        "gold": [
            (r'(\d+\.?\d*)\s*美元.*?盎司', "美元/盎司"),
            (r'金价.*?(\d+\.?\d*)', "美元"),
        ],
        "scfi": [
            (r'(\d+\.?\d*)\s*点', "点"),
            (r'SCFI.*?(\d+\.?\d*)', "点"),
        ]
    }
    
    # 涨跌幅提取
    change_patterns = [
        (r'(涨|涨跌|上涨)\s*(\d+\.?\d*)\s*%', "up"),
        (r'(跌|下跌)\s*(\d+\.?\d*)\s*%', "down"),
        (r'(涨|涨跌|上涨)\s*(\d+\.?\d*)\s*美元', "up"),
        (r'(跌|下跌)\s*(\d+\.?\d*)\s*美元', "down"),
    ]
    
    # 提取价格
    if material_type in price_patterns:
        for pattern, unit in price_patterns[material_type]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["price"] = match.group(1)
                result["unit"] = unit
                break
    
    # 提取涨跌幅
    for pattern, direction in change_patterns:
        match = re.search(pattern, text)
        if match:
            change_value = match.group(2)
            arrow = "↑" if direction == "up" else "↓"
            result["change"] = f"{arrow}{change_value}%"
            break
    
    return result

# ==================== 启动时间（用于健康检查）====================
START_TIME = datetime.now()

# ==================== API 接口 ====================
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口
    """
    uptime = datetime.now() - START_TIME
    
    # 测试搜索服务是否可用
    services = {
        "search_api": True,
        "cache": True,
        "limiter": True
    }
    
    # 简单测试搜索API
    try:
        ctx = new_context(method="health_check")
        client = SearchClient(ctx=ctx)
        # 不实际搜索，只测试客户端是否可用
        services["search_api"] = True
    except Exception as e:
        services["search_api"] = False
        logger.error(f"Search API health check failed: {str(e)}")
    
    return HealthResponse(
        status="healthy" if all(services.values()) else "degraded",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        services=services,
        uptime=str(uptime).split('.')[0]  # 去掉微秒
    )

@router.get("/cache/clear")
async def clear_cache():
    """
    清除缓存（调试用）
    """
    cache.clear()
    return {"success": True, "message": "缓存已清除"}

@router.get("/news/realtime", response_model=NewsResponse)
async def get_realtime_news():
    """
    获取实时市场新闻（优先权威来源）
    改进：添加重试、超时、缓存、并发控制
    """
    # 检查缓存
    cache_key = "realtime_news"
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info("Returning cached news data")
        return NewsResponse(
            success=True,
            data=cached_data["news"],
            timestamp=cached_data["timestamp"],
            message="获取成功（缓存）",
            cached=True
        )
    
    try:
        logger.info("Fetching realtime market news from authoritative sources...")
        
        # 创建搜索客户端
        ctx = new_context(method="get_realtime_news")
        client = SearchClient(ctx=ctx)
        
        all_news = []
        seen_titles = set()
        
        # 获取今天的日期
        today = date.today().strftime("%Y-%m-%d")
        
        # 使用并发限制
        await limiter.acquire()
        
        try:
            # 1. 优先搜索顶级权威来源（彭博社、路透社、华尔街日报）
            tier1_queries = [
                f"site:bloomberg.com OR site:reuters.com OR site:wsj.com 原油价格 OR oil price {today}",
                f"site:bloomberg.com OR site:reuters.com 铜价格 OR copper price {today}",
                f"site:bloomberg.com OR site:reuters.com 中东局势 供应链 {today}"
            ]
            
            for query in tier1_queries:
                try:
                    response = await retry_search(client, query, count=5, need_summary=False)
                    
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
                response = await retry_search(client, twitter_query, count=5, need_summary=False)
                
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
                    response = await retry_search(client, query, count=3, need_summary=False)
                    
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
                    response = await retry_search(client, query, count=3, need_summary=False)
                    
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
            
            # 缓存结果
            cache.set(cache_key, {
                "news": all_news,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return NewsResponse(
                success=True,
                data=all_news,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message=f"获取成功，共{len(all_news)}条新闻",
                cached=False
            )
            
        finally:
            limiter.release()
        
    except Exception as e:
        logger.error(f"Failed to fetch news: {str(e)}", exc_info=True)
        return NewsResponse(
            success=False,
            data=[],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message=f"获取失败: {str(e)}",
            cached=False
        )

@router.get("/prices/all", response_model=PriceResponse)
async def get_all_prices():
    """
    获取所有关键原材料价格
    改进：添加重试、超时、缓存、更好的价格提取
    """
    # 检查缓存
    cache_key = "all_prices"
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info("Returning cached price data")
        return PriceResponse(
            success=True,
            data=cached_data["prices"],
            timestamp=cached_data["timestamp"],
            message="获取成功（缓存）",
            cached=True
        )
    
    try:
        logger.info("Fetching all material prices...")
        
        materials = {
            "oil": {"name": "布伦特原油", "search": "布伦特原油价格 最新"},
            "copper": {"name": "LME铜", "search": "LME铜价 最新"},
            "aluminum": {"name": "LME铝", "search": "LME铝价 最新"},
            "palladium": {"name": "钯金", "search": "钯金价格 最新"},
            "gold": {"name": "黄金", "search": "黄金价格 最新"},
            "scfi": {"name": "SCFI运费", "search": "SCFI集装箱运费 最新"}
        }
        
        all_prices = {}
        
        # 创建搜索客户端
        ctx = new_context(method="get_all_prices")
        client = SearchClient(ctx=ctx)
        
        # 使用并发限制
        await limiter.acquire()
        
        try:
            for material, info in materials.items():
                try:
                    response = await retry_search(client, info["search"], count=3, need_summary=False)
                    
                    price_data = {
                        "material": material,
                        "name": info["name"],
                        "price": "--",
                        "change": "--",
                        "unit": "",
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
                            
                            # 合并标题和摘要进行价格提取
                            text = (item.title or "") + " " + (item.snippet or "")
                            
                            # 使用改进的价格提取函数
                            extracted = extract_price_from_text(text, material)
                            
                            if extracted["price"] != "--" and price_data["price"] == "--":
                                price_data["price"] = extracted["price"]
                                price_data["change"] = extracted["change"]
                                price_data["unit"] = extracted["unit"]
                    
                    all_prices[material] = price_data
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch {material}: {str(e)}")
                    all_prices[material] = {
                        "material": material,
                        "name": info["name"],
                        "price": "--",
                        "change": "--",
                        "error": str(e)
                    }
            
            # 缓存结果
            cache.set(cache_key, {
                "prices": all_prices,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return PriceResponse(
                success=True,
                data=all_prices,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message="获取成功",
                cached=False
            )
            
        finally:
            limiter.release()
        
    except Exception as e:
        logger.error(f"Failed to fetch prices: {str(e)}", exc_info=True)
        return PriceResponse(
            success=False,
            data={},
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message=f"获取失败: {str(e)}",
            cached=False
        )
