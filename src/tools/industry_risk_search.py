"""
行业风险搜索工具
针对六大行业（游艇、生物医药、PCB、新型储能、打印耗材、跨境电商）提供实时风险信息检索
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Dict, Any, Optional
import json


# 六大行业的关键原材料和关联指标配置
INDUSTRY_CONFIG = {
    "PCB": {
        "materials": ["电解铜箔", "覆铜板(CCL)", "钯/金电镀药水"],
        "indicators": ["LME铜价", "钯金现货"],
        "search_keywords": ["PCB", "印刷电路板", "电解铜箔", "覆铜板", "钯金", "电镀药水"]
    },
    "游艇": {
        "materials": ["不饱和聚酯树脂", "乙烯基树脂", "胶衣", "进口发动机"],
        "indicators": ["布伦特原油"],
        "search_keywords": ["游艇", "树脂", "胶衣", "进口发动机", "Volvo", "Mercury"]
    },
    "生物医药": {
        "materials": ["API原料药", "异丙醇", "乙腈溶剂", "液氦"],
        "indicators": ["中东空运溢价", "卡塔尔航道"],
        "search_keywords": ["生物医药", "原料药", "API", "异丙醇", "乙腈", "液氦"]
    },
    "新型储能": {
        "materials": ["PVDF粘结剂", "电解液溶剂(DMC/EMC)", "铝箔"],
        "indicators": ["沪铝主力", "电力成本预期"],
        "search_keywords": ["新型储能", "PVDF", "电解液", "DMC", "EMC", "铝箔"]
    },
    "打印耗材": {
        "materials": ["聚合碳粉", "ABS/HIPS塑料粒子", "显影滚轴"],
        "indicators": ["远东塑料价格指数"],
        "search_keywords": ["打印耗材", "聚合碳粉", "ABS", "HIPS", "塑料粒子", "显影滚轴"]
    },
    "跨境电商": {
        "materials": ["瓦楞纸箱", "航空燃油附加费", "集装箱运价"],
        "indicators": ["SCFI运费指数", "好望角绕行指数"],
        "search_keywords": ["跨境电商", "瓦楞纸箱", "航空燃油", "集装箱运价", "SCFI"]
    }
}


@tool
def industry_risk_search(
    industry: str,
    runtime: ToolRuntime = None
) -> str:
    """
    搜索特定行业的实时风险信息，包括战争动态、原材料价格波动、物流延误等。
    
    Args:
        industry: 行业名称，支持：PCB、游艇、生物医药、新型储能、打印耗材、跨境电商
        
    Returns:
        返回JSON格式的搜索结果，包含风险动态、原材料信息、物流状况等
    """
    ctx = runtime.context if runtime else new_context(method="industry_risk_search")
    
    # 验证行业名称
    if industry not in INDUSTRY_CONFIG:
        return json.dumps({
            "success": False,
            "error": f"不支持的行业: {industry}。支持的行业: {', '.join(INDUSTRY_CONFIG.keys())}"
        }, ensure_ascii=False)
    
    config = INDUSTRY_CONFIG[industry]
    
    # 构建搜索查询
    search_queries = [
        f"伊朗战争 {industry} 原材料价格 物流延误",
        f"中东局势 {industry} 供应链影响",
        f"{industry} {' '.join(config['materials'][:2])} 价格波动"
    ]
    
    client = SearchClient(ctx=ctx)
    
    results = []
    for query in search_queries:
        try:
            response = client.web_search_with_summary(
                query=query,
                count=5
            )
            
            if response.web_items:
                for item in response.web_items[:3]:  # 每个查询取前3条
                    results.append({
                        "title": item.title,
                        "source": item.site_name,
                        "url": item.url,
                        "snippet": item.snippet,
                        "publish_time": item.publish_time
                    })
            
            # 如果有AI总结，也添加进去
            if response.summary and query == search_queries[0]:
                results.insert(0, {
                    "title": "AI风险分析摘要",
                    "source": "AI分析",
                    "snippet": response.summary,
                    "is_summary": True
                })
                
        except Exception as e:
            continue
    
    # 整理返回数据
    output = {
        "success": True,
        "industry": industry,
        "materials": config["materials"],
        "indicators": config["indicators"],
        "risk_updates": results[:10],  # 最多返回10条
        "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return json.dumps(output, ensure_ascii=False, indent=2)


def get_industry_config(industry: str) -> Optional[Dict[str, Any]]:
    """
    获取特定行业的配置信息
    
    Args:
        industry: 行业名称
        
    Returns:
        行业配置字典，如果不存在则返回None
    """
    return INDUSTRY_CONFIG.get(industry)


def list_supported_industries() -> list:
    """
    获取支持的行业列表
    
    Returns:
        支持的行业名称列表
    """
    return list(INDUSTRY_CONFIG.keys())
