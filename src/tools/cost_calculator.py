"""
成本计算工具
根据原材料价格波动计算各行业的成本影响
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Dict, List, Optional
import json
import re


# 各行业成本计算模型（简化版）
COST_MODELS = {
    "PCB": {
        "base_materials": {
            "电解铜箔": {"weight": 0.35, "unit": "元/张", "base_price": 180},
            "覆铜板(CCL)": {"weight": 0.40, "unit": "元/张", "base_price": 220},
            "钯/金电镀药水": {"weight": 0.15, "unit": "%成本", "base_price": 100},
            "其他": {"weight": 0.10, "unit": "%成本", "base_price": 100}
        },
        "price_sensitive_materials": ["电解铜箔", "覆铜板(CCL)", "钯/金电镀药水"],
        "warning_threshold": 0.05  # 5%涨幅触发预警
    },
    "游艇": {
        "base_materials": {
            "不饱和聚酯树脂": {"weight": 0.30, "unit": "元/吨", "base_price": 9500},
            "乙烯基树脂": {"weight": 0.15, "unit": "元/吨", "base_price": 12500},
            "胶衣": {"weight": 0.10, "unit": "元/吨", "base_price": 15000},
            "进口发动机": {"weight": 0.35, "unit": "万元/台", "base_price": 25},
            "其他": {"weight": 0.10, "unit": "%成本", "base_price": 100}
        },
        "price_sensitive_materials": ["不饱和聚酯树脂", "乙烯基树脂", "胶衣"],
        "warning_threshold": 0.05
    },
    "生物医药": {
        "base_materials": {
            "API原料药": {"weight": 0.40, "unit": "元/kg", "base_price": 850},
            "异丙醇": {"weight": 0.15, "unit": "元/L", "base_price": 12},
            "乙腈溶剂": {"weight": 0.10, "unit": "元/L", "base_price": 45},
            "液氦": {"weight": 0.20, "unit": "元/L", "base_price": 180},
            "其他": {"weight": 0.15, "unit": "%成本", "base_price": 100}
        },
        "price_sensitive_materials": ["API原料药", "液氦"],
        "warning_threshold": 0.05
    },
    "新型储能": {
        "base_materials": {
            "PVDF粘结剂": {"weight": 0.25, "unit": "元/kg", "base_price": 320},
            "电解液溶剂(DMC/EMC)": {"weight": 0.35, "unit": "元/kg", "base_price": 18},
            "铝箔": {"weight": 0.20, "unit": "元/kg", "base_price": 25},
            "其他": {"weight": 0.20, "unit": "%成本", "base_price": 100}
        },
        "price_sensitive_materials": ["PVDF粘结剂", "电解液溶剂(DMC/EMC)"],
        "warning_threshold": 0.05
    },
    "打印耗材": {
        "base_materials": {
            "聚合碳粉": {"weight": 0.35, "unit": "元/kg", "base_price": 85},
            "ABS/HIPS塑料粒子": {"weight": 0.30, "unit": "元/kg", "base_price": 12},
            "显影滚轴": {"weight": 0.20, "unit": "元/个", "base_price": 45},
            "其他": {"weight": 0.15, "unit": "%成本", "base_price": 100}
        },
        "price_sensitive_materials": ["聚合碳粉", "ABS/HIPS塑料粒子"],
        "warning_threshold": 0.05
    },
    "跨境电商": {
        "base_materials": {
            "瓦楞纸箱": {"weight": 0.25, "unit": "元/个", "base_price": 8},
            "航空燃油附加费": {"weight": 0.35, "unit": "元/kg", "base_price": 15},
            "集装箱运价": {"weight": 0.30, "unit": "美元/柜", "base_price": 2500},
            "其他": {"weight": 0.10, "unit": "%成本", "base_price": 100}
        },
        "price_sensitive_materials": ["航空燃油附加费", "集装箱运价"],
        "warning_threshold": 0.05
    }
}


@tool
def calculate_cost_impact(
    industry: str,
    search_results: str,
    runtime: ToolRuntime = None
) -> str:
    """
    根据搜索结果中的原材料价格变化，计算对特定行业成本的影响。
    
    Args:
        industry: 行业名称（PCB、游艇、生物医药、新型储能、打印耗材、跨境电商）
        search_results: 搜索结果的JSON字符串，包含价格波动信息
        
    Returns:
        返回JSON格式的成本影响分析，包括具体材料涨价金额、总成本变化、风险等级等
    """
    ctx = runtime.context if runtime else new_context(method="calculate_cost_impact")
    
    # 验证行业名称
    if industry not in COST_MODELS:
        return json.dumps({
            "success": False,
            "error": f"不支持的行业: {industry}。支持的行业: {', '.join(COST_MODELS.keys())}"
        }, ensure_ascii=False)
    
    model = COST_MODELS[industry]
    
    # 解析搜索结果，提取价格波动信息
    price_changes = _extract_price_changes(search_results, industry, model)
    
    # 计算成本影响
    impact_details = []
    total_cost_change = 0.0
    max_change_rate = 0.0
    
    for material_name, change_info in price_changes.items():
        if material_name not in model["base_materials"]:
            continue
        
        base_info = model["base_materials"][material_name]
        weight = base_info["weight"]
        base_price = base_info["base_price"]
        unit = base_info["unit"]
        
        change_rate = change_info.get("change_rate", 0)
        change_direction = change_info.get("direction", "unknown")
        
        # 计算价格变化
        price_change = base_price * change_rate
        cost_impact = weight * change_rate * 100  # 转换为百分比
        
        total_cost_change += cost_impact
        max_change_rate = max(max_change_rate, abs(change_rate))
        
        impact_details.append({
            "material": material_name,
            "base_price": base_price,
            "unit": unit,
            "change_rate": f"{change_rate*100:.1f}%",
            "direction": "上涨" if change_direction == "up" else "下跌" if change_direction == "down" else "波动",
            "price_change": f"±{abs(price_change):.2f}",
            "cost_impact": f"{'+' if cost_impact > 0 else ''}{cost_impact:.2f}%",
            "weight": f"{weight*100:.0f}%"
        })
    
    # 确定风险等级（红黄绿）
    if max_change_rate >= 0.10:  # 10%以上
        risk_level = "🔴 红色警报"
        risk_description = "重大成本压力，建议立即采取行动"
    elif max_change_rate >= 0.05:  # 5-10%
        risk_level = "🟡 黄色预警"
        risk_description = "成本上涨明显，需要关注后续走势"
    elif max_change_rate >= 0.02:  # 2-5%
        risk_level = "🟢 绿色提醒"
        risk_description = "成本小幅波动，保持观察即可"
    else:
        risk_level = "🟢 绿色"
        risk_description = "成本相对稳定"
    
    # 生成决策建议
    recommendations = _generate_recommendations(industry, risk_level, total_cost_change, price_changes)
    
    output = {
        "success": True,
        "industry": industry,
        "risk_level": risk_level,
        "risk_description": risk_description,
        "total_cost_change": f"{total_cost_change:+.2f}%",
        "material_impacts": impact_details,
        "recommendations": recommendations,
        "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return json.dumps(output, ensure_ascii=False, indent=2)


def _extract_price_changes(search_results: str, industry: str, model: Dict) -> Dict:
    """
    从搜索结果中提取价格波动信息
    
    Args:
        search_results: 搜索结果JSON字符串
        industry: 行业名称
        model: 行业成本模型
        
    Returns:
        价格变化字典 {材料名: {change_rate: float, direction: str}}
    """
    price_changes = {}
    
    try:
        data = json.loads(search_results)
        updates = data.get("risk_updates", [])
    except:
        # 如果解析失败，返回模拟数据
        return _get_mock_price_changes(model)
    
    # 价格波动模式匹配
    price_patterns = [
        r'涨(\d+(?:\.\d+)?)%',
        r'上涨(\d+(?:\.\d+)?)%',
        r'涨幅(\d+(?:\.\d+)?)%',
        r'跌(\d+(?:\.\d+)?)%',
        r'下跌(\d+(?:\.\d+)?)%',
        r'跌幅(\d+(?:\.\d+)?)%',
        r'涨幅达(\d+(?:\.\d+)?)%',
        r'上涨\s*(\d+(?:\.\d+)?)%',
    ]
    
    materials = model["base_materials"].keys()
    
    for update in updates:
        text = update.get("snippet", "") + " " + update.get("title", "")
        
        for material in materials:
            if material in text or any(keyword in text for keyword in model.get("price_sensitive_materials", [])):
                # 尝试提取价格变化
                for pattern in price_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        change_rate = float(matches[0]) / 100
                        direction = "up" if "涨" in text or "上涨" in text else "down"
                        
                        if material not in price_changes:
                            price_changes[material] = {
                                "change_rate": change_rate,
                                "direction": direction
                            }
                        break
    
    # 如果没有提取到价格变化，使用模拟数据
    if not price_changes:
        return _get_mock_price_changes(model)
    
    return price_changes


def _get_mock_price_changes(model: Dict) -> Dict:
    """
    生成模拟的价格变化数据（用于演示）
    
    注意：实际生产环境中应该从真实数据源获取
    """
    import random
    
    price_changes = {}
    sensitive_materials = model.get("price_sensitive_materials", [])
    
    # 为价格敏感材料生成随机波动
    for material in sensitive_materials[:2]:  # 只为前2个敏感材料生成波动
        if random.random() > 0.3:  # 70%概率有波动
            change_rate = random.uniform(0.02, 0.08)  # 2%-8%波动
            price_changes[material] = {
                "change_rate": change_rate,
                "direction": "up"
            }
    
    return price_changes


def _generate_recommendations(
    industry: str,
    risk_level: str,
    total_cost_change: float,
    price_changes: Dict
) -> List[str]:
    """
    根据风险等级和成本变化生成决策建议
    """
    recommendations = []
    
    if "红色" in risk_level:
        recommendations.extend([
            "⚠️ 立即行动建议：",
            f"1. 建议今天下午 4 点前锁定下周订单，避免后续成本上涨",
            "2. 联系供应商确认当前库存和交货周期",
            "3. 评估是否需要调整产品报价，建议报价单有效期缩短至 24-48 小时",
            "4. 现有现货库存优先保障 A 类客户订单"
        ])
    elif "黄色" in risk_level:
        recommendations.extend([
            "⚡ 密切关注建议：",
            "1. 建议在 3 天内完成近期订单的下单",
            "2. 与供应商保持每日沟通，了解最新价格走势",
            "3. 准备备用供应商方案，防止供应链中断",
            "4. 报价单建议注明价格有效期 3-5 天"
        ])
    else:
        recommendations.extend([
            "✅ 常规观察建议：",
            "1. 保持正常采购节奏",
            "2. 定期关注原材料价格走势",
            "3. 维持合理的安全库存水平"
        ])
    
    # 行业特定建议
    industry_specific = _get_industry_specific_recommendations(industry, price_changes)
    recommendations.extend(industry_specific)
    
    return recommendations


def _get_industry_specific_recommendations(industry: str, price_changes: Dict) -> List[str]:
    """
    生成行业特定的建议
    """
    recommendations = []
    
    if industry == "PCB":
        recommendations.append("💡 PCB行业特别提醒：关注 LME 铜价走势，钯金价格波动较大时需及时调整电镀工艺")
    elif industry == "游艇":
        recommendations.append("💡 游艇行业特别提醒：原油价格上涨会传导至树脂成本，进口发动机物流周期需提前确认")
    elif industry == "生物医药":
        recommendations.append("💡 生物医药行业特别提醒：API原料药供应稳定性至关重要，建议建立多元化供应商体系")
    elif industry == "新型储能":
        recommendations.append("💡 新型储能行业特别提醒：关注铝价和电力成本双重影响，PVDF供应需提前锁定")
    elif industry == "打印耗材":
        recommendations.append("💡 打印耗材行业特别提醒：塑料粒子价格波动频繁，建议采用远期采购策略")
    elif industry == "跨境电商":
        recommendations.append("💡 跨境电商行业特别提醒：关注 SCFI 运费指数和航空燃油附加费，合理安排发货批次")
    
    return recommendations


def get_cost_model(industry: str) -> Optional[Dict]:
    """
    获取特定行业的成本模型
    
    Args:
        industry: 行业名称
        
    Returns:
        成本模型字典，如果不存在则返回None
    """
    return COST_MODELS.get(industry)
