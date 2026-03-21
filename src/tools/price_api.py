"""
专业价格数据API工具
实现混合数据获取策略：专业API → 网络搜索 → 模拟数据
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Dict, List, Optional, Tuple
import json
import re
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 专业价格数据源配置
PRICE_SOURCES = {
    "布伦特原油": {
        "api_url": "https://api.oilpriceapi.com/v1/prices",  # 示例API（需要API Key）
        "search_keywords": ["布伦特原油价格", "Brent原油实时价格", "国际油价今日"],
        "unit": "美元/桶",
        "base_price": 75.0,
        "importance": "极高",
        "related_industries": ["游艇", "新型储能", "跨境电商"]
    },
    "LME铜价": {
        "api_url": "https://api.lme.com/v1/copper",  # 示例API（需要API Key）
        "search_keywords": ["LME铜价实时", "电解铜价格今日", "铜期货最新价"],
        "unit": "美元/吨",
        "base_price": 8500.0,
        "importance": "高",
        "related_industries": ["PCB", "新型储能"]
    },
    "钯金现货": {
        "api_url": "https://api.metals.com/v1/palladium",  # 示例API（需要API Key）
        "search_keywords": ["钯金价格今日", "钯金现货价格", "贵金属钯金行情"],
        "unit": "美元/盎司",
        "base_price": 1000.0,
        "importance": "高",
        "related_industries": ["PCB"]
    },
    "SCFI运费指数": {
        "api_url": "https://api.shipping.com/v1/scfi",  # 示例API（需要API Key）
        "search_keywords": ["SCFI运费指数今日", "集装箱运价最新", "海运费实时"],
        "unit": "指数点",
        "base_price": 2000.0,
        "importance": "高",
        "related_industries": ["跨境电商"]
    },
    "沪铝主力": {
        "api_url": "https://api.shfe.com/v1/aluminum",  # 示例API（需要API Key）
        "search_keywords": ["沪铝主力价格", "铝期货实时行情", "铝价今日"],
        "unit": "元/吨",
        "base_price": 18500.0,
        "importance": "中",
        "related_industries": ["新型储能"]
    },
    "黄金现货": {
        "api_url": "https://api.metals.com/v1/gold",  # 示例API（需要API Key）
        "search_keywords": ["黄金现货价格", "国际金价今日", "黄金实时行情"],
        "unit": "美元/盎司",
        "base_price": 2000.0,
        "importance": "高",
        "related_industries": ["PCB"]
    }
}


class PriceDataExtractor:
    """价格数据提取器 - 增强版"""
    
    # 价格匹配模式（按优先级排序）
    PRICE_PATTERNS = [
        # 标准格式
        r'(\d+(?:\.\d+)?)\s*美元/桶',
        r'(\d+(?:\.\d+)?)\s*美元/吨',
        r'(\d+(?:\.\d+)?)\s*美元/盎司',
        r'(\d+(?:\.\d+)?)\s*元/吨',
        
        # 价格范围格式
        r'价格[：:]\s*(\d+(?:\.\d+)?)',
        r'报价[：:]\s*(\d+(?:\.\d+)?)',
        r'现价[：:]\s*(\d+(?:\.\d+)?)',
        
        # 涨跌幅度格式
        r'涨[幅至]\s*(\d+(?:\.\d+)?)\s*%',
        r'上涨\s*(\d+(?:\.\d+)?)\s*%',
        r'涨幅\s*(\d+(?:\.\d+)?)\s*%',
        r'跌[幅至]\s*(\d+(?:\.\d+)?)\s*%',
        r'下跌\s*(\d+(?:\.\d+)?)\s*%',
        r'跌幅\s*(\d+(?:\.\d+)?)\s*%',
        
        # 价格区间格式
        r'(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)',
    ]
    
    # 时间匹配模式
    TIME_PATTERNS = [
        r'(\d{4}年\d{1,2}月\d{1,2}日)',
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{1,2}月\d{1,2}日)',
        r'今日',
        r'实时',
        r'最新',
    ]
    
    @classmethod
    def extract_price_from_text(cls, text: str, indicator: str) -> Optional[Dict]:
        """
        从文本中提取价格信息（增强版）
        
        Args:
            text: 包含价格信息的文本
            indicator: 指标名称（如"布伦特原油"）
            
        Returns:
            提取到的价格信息字典，包含价格、涨跌幅度等
        """
        result = {
            "price": None,
            "change_rate": None,
            "direction": None,
            "confidence": 0.0,
            "source_text": text[:200]
        }
        
        # 提取具体价格
        for pattern in cls.PRICE_PATTERNS[:4]:  # 前4个是具体价格模式
            match = re.search(pattern, text)
            if match:
                result["price"] = float(match.group(1))
                result["confidence"] = 0.8
                break
        
        # 提取涨跌幅度
        for pattern in cls.PRICE_PATTERNS[4:10]:  # 涨跌幅度模式
            match = re.search(pattern, text)
            if match:
                result["change_rate"] = float(match.group(1)) / 100
                if "涨" in pattern:
                    result["direction"] = "up"
                else:
                    result["direction"] = "down"
                result["confidence"] = max(result["confidence"], 0.7)
                break
        
        # 如果没有提取到价格，但提取到了涨跌幅度，使用基础价格推算
        if result["price"] is None and result["change_rate"] is not None:
            base_price = PRICE_SOURCES.get(indicator, {}).get("base_price", 100)
            if result["direction"] == "up":
                result["price"] = base_price * (1 + result["change_rate"])
            else:
                result["price"] = base_price * (1 - result["change_rate"])
            result["confidence"] = 0.5
            result["is_estimated"] = True
        
        return result if result["price"] is not None or result["change_rate"] is not None else None
    
    @classmethod
    def extract_publish_time(cls, text: str) -> Optional[str]:
        """提取发布时间"""
        for pattern in cls.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                if match.group(0) in ["今日", "实时", "最新"]:
                    return datetime.now().strftime("%Y-%m-%d %H:%M")
                return match.group(1)
        return None


@tool
def get_realtime_prices(
    indicators: List[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    获取实时价格数据（混合方案：专业API → 网络搜索 → 模拟数据）
    
    Args:
        indicators: 需要查询的指标列表，如["布伦特原油", "LME铜价"]
                   如果不指定，则返回所有关键指标
        
    Returns:
        返回JSON格式的价格数据，包含价格、涨跌幅、数据源等信息
    """
    ctx = runtime.context if runtime else new_context(method="get_realtime_prices")
    
    # 如果没有指定指标，查询所有
    if indicators is None:
        indicators = list(PRICE_SOURCES.keys())
    
    results = []
    data_source_stats = {
        "api_success": 0,
        "search_success": 0,
        "fallback_used": 0
    }
    
    for indicator in indicators:
        if indicator not in PRICE_SOURCES:
            logger.warning(f"未知的指标: {indicator}")
            continue
        
        config = PRICE_SOURCES[indicator]
        
        # 策略1: 尝试专业API（如果配置了API Key）
        api_result = _try_api_source(indicator, config, ctx)
        if api_result:
            results.append(api_result)
            data_source_stats["api_success"] += 1
            continue
        
        # 策略2: 降级到网络搜索
        search_result = _try_search_source(indicator, config, ctx)
        if search_result:
            results.append(search_result)
            data_source_stats["search_success"] += 1
            continue
        
        # 策略3: 最后使用基础价格（模拟数据）
        fallback_result = _get_fallback_data(indicator, config)
        results.append(fallback_result)
        data_source_stats["fallback_used"] += 1
    
    output = {
        "success": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_source_stats": data_source_stats,
        "prices": results,
        "total": len(results)
    }
    
    return json.dumps(output, ensure_ascii=False, indent=2)


def _try_api_source(indicator: str, config: Dict, ctx) -> Optional[Dict]:
    """
    尝试从专业API获取价格数据
    
    注意：需要配置相应的API Key才能使用
    当前版本作为占位，实际使用时需要配置真实的API
    """
    # 检查是否配置了API Key（通过环境变量）
    import os
    api_key = os.getenv(f"{indicator.upper().replace(' ', '_')}_API_KEY")
    
    if not api_key:
        logger.info(f"未配置 {indicator} 的API Key，跳过专业API")
        return None
    
    # 如果有API Key，尝试调用专业API
    # 这里是示例代码，实际使用时需要根据具体API文档实现
    try:
        # import requests
        # response = requests.get(
        #     config["api_url"],
        #     headers={"Authorization": f"Bearer {api_key}"},
        #     timeout=10
        # )
        # if response.status_code == 200:
        #     data = response.json()
        #     return {
        #         "indicator": indicator,
        #         "price": data["price"],
        #         "change_rate": data.get("change_rate", 0),
        #         "direction": "up" if data.get("change_rate", 0) > 0 else "down",
        #         "unit": config["unit"],
        #         "data_source": "专业API",
        #         "confidence": 0.95,
        #         "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        #         "related_industries": config["related_industries"]
        #     }
        pass
    except Exception as e:
        logger.error(f"API调用失败: {indicator}, 错误: {str(e)}")
    
    return None


def _try_search_source(indicator: str, config: Dict, ctx) -> Optional[Dict]:
    """
    从网络搜索获取价格数据（增强版）
    """
    try:
        client = SearchClient(ctx=ctx)
        
        # 构建搜索查询
        query = f"{' '.join(config['search_keywords'])} 最新价格 2026"
        
        response = client.web_search(
            query=query,
            count=5,
            need_summary=False
        )
        
        if not response.web_items:
            return None
        
        # 尝试从多个搜索结果中提取价格
        extracted_prices = []
        
        for item in response.web_items:
            text = f"{item.title} {item.snippet}"
            price_info = PriceDataExtractor.extract_price_from_text(text, indicator)
            
            if price_info and price_info["confidence"] > 0.5:
                price_info["source_url"] = item.url
                price_info["source_name"] = item.site_name
                price_info["publish_time"] = item.publish_time or PriceDataExtractor.extract_publish_time(text)
                extracted_prices.append(price_info)
        
        # 如果提取到了价格，选择置信度最高的
        if extracted_prices:
            best_price = max(extracted_prices, key=lambda x: x["confidence"])
            
            return {
                "indicator": indicator,
                "price": round(best_price["price"], 2) if best_price["price"] else None,
                "change_rate": f"{best_price['change_rate']*100:.1f}%" if best_price.get("change_rate") else None,
                "direction": best_price.get("direction", "stable"),
                "unit": config["unit"],
                "data_source": "网络搜索",
                "confidence": best_price["confidence"],
                "publish_time": best_price.get("publish_time", "近期"),
                "source_name": best_price.get("source_name", "未知来源"),
                "source_url": best_price.get("source_url", ""),
                "related_industries": config["related_industries"],
                "is_estimated": best_price.get("is_estimated", False)
            }
        
        return None
        
    except Exception as e:
        logger.error(f"网络搜索失败: {indicator}, 错误: {str(e)}")
        return None


def _get_fallback_data(indicator: str, config: Dict) -> Dict:
    """
    获取降级数据（基于基础价格的合理波动）
    """
    import random
    
    # 使用随机波动模拟真实价格变化（-5% 到 +5%）
    change_rate = random.uniform(-0.05, 0.05)
    base_price = config["base_price"]
    estimated_price = base_price * (1 + change_rate)
    
    return {
        "indicator": indicator,
        "price": round(estimated_price, 2),
        "change_rate": f"{abs(change_rate)*100:.2f}%",
        "direction": "up" if change_rate > 0 else "down" if change_rate < 0 else "stable",
        "unit": config["unit"],
        "data_source": "估算数据",
        "confidence": 0.3,
        "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "is_estimated": True,
        "base_price": base_price,
        "related_industries": config["related_industries"],
        "warning": "⚠️ 数据为估算值，仅供参考"
    }


def get_price_for_industry(industry: str, ctx=None) -> Dict[str, Dict]:
    """
    获取特定行业相关的所有价格指标
    
    Args:
        industry: 行业名称
        ctx: 运行时上下文
        
    Returns:
        价格数据字典
    """
    # 找出与该行业相关的所有指标
    relevant_indicators = []
    for indicator, config in PRICE_SOURCES.items():
        if industry in config.get("related_industries", []):
            relevant_indicators.append(indicator)
    
    if not relevant_indicators:
        return {"success": False, "error": f"未找到与 {industry} 相关的价格指标"}
    
    # 获取价格数据
    if ctx is None:
        ctx = new_context(method="get_price_for_industry")
    
    try:
        result_json = get_realtime_prices(indicators=relevant_indicators, runtime=None)
        return json.loads(result_json)
    except Exception as e:
        return {"success": False, "error": str(e)}


# 工具注册信息
__all__ = ["get_realtime_prices", "get_price_for_industry", "PRICE_SOURCES"]
