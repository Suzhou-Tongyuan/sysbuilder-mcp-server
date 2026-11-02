# -*- coding: utf-8 -*-
"""基于四个 Sysbuilder 导弹实例执行技术、周期、风险和经济架构权衡。

本脚本由 RunArchitectureTradeoff 在当前模型对象代码之后执行，因此直接读取
CFG_A/CFG_B/CFG_C/CFG_D 四个实例。评价只用于案例架构初筛，不替代统一仿真。
"""

import csv
import json
import math

import matplotlib.pyplot as plt
import numpy as np


RESULT_JSON = "F://SysbuilderMCP//output//车载防空导弹架构权衡结果.json"
RESULT_CSV = "F://SysbuilderMCP//output//车载防空导弹架构权衡结果.csv"

DIMENSION_WEIGHTS = {
    "技术性": 0.25,
    "周期": 0.25,
    "风险可控性": 0.25,
    "经济性": 0.25,
}

# 经验公式文档中的资料完整度、拓扑成熟度、布局成熟度和复杂度评分。
EXPERIENCE = {
    "CFG-A": {"参数完整度": 1.00, "动力成熟度": 1.00, "气动成熟度": 1.00, "复杂度评分": 1.00},
    "CFG-B": {"参数完整度": 0.95, "动力成熟度": 0.90, "气动成熟度": 1.00, "复杂度评分": 0.85},
    "CFG-C": {"参数完整度": 0.95, "动力成熟度": 1.00, "气动成熟度": 0.90, "复杂度评分": 0.85},
    "CFG-D": {"参数完整度": 0.90, "动力成熟度": 0.90, "气动成熟度": 0.90, "复杂度评分": 0.70},
}

SCHEMES = {
    "CFG-A": CFG_A演示样机,
    "CFG-B": CFG_B演示样机,
    "CFG-C": CFG_C演示样机,
    "CFG-D": CFG_D演示样机,
}


def clip01(value):
    """将评分限制在 0 到 1，适用于全部收益型评价指标。"""
    return max(0.0, min(1.0, float(value)))


def read_instance(instance):
    """提取架构实例的技术与几何参数，用于同口径权衡计算。"""
    return {
        "动力拓扑": instance.动力拓扑,
        "气动布局": instance.气动布局,
        "弹长": float(instance.弹长),
        "弹体直径": float(instance.弹体直径),
        "翼展": float(instance.翼展),
        "控制面展长": float(instance.控制面展长),
        "头锥长度": float(instance.头锥长度),
        "初始质量": float(instance.初始质量),
        "燃尽质量": float(instance.燃尽质量),
        "质心位置": float(instance.质心位置),
        "最大推力": float(instance.最大推力),
        "推进工作时间": float(instance.推进工作时间),
        "气动效率系数": float(instance.气动效率系数),
        "最大制导加速度": float(instance.最大制导加速度),
    }


def calculate_scores():
    """计算四维评分、设计边界预筛结果和综合架构权衡分数。"""
    data = {name: read_instance(instance) for name, instance in SCHEMES.items()}

    # 技术性采用模型中可直接计算的推进、气动、质量和制导能力参数。
    for values in data.values():
        values["推重指标"] = values["最大推力"] / values["初始质量"]
        values["推进剂质量分数"] = (
            values["初始质量"] - values["燃尽质量"]
        ) / values["初始质量"]

    max_thrust_mass = max(v["推重指标"] for v in data.values())
    max_burn_time = max(v["推进工作时间"] for v in data.values())
    max_aero_efficiency = max(v["气动效率系数"] for v in data.values())
    max_propellant_fraction = max(v["推进剂质量分数"] for v in data.values())

    min_mass = min(v["初始质量"] for v in data.values())
    min_length = min(v["弹长"] for v in data.values())
    min_span = min(v["翼展"] for v in data.values())

    results = []
    for name, values in data.items():
        exp = EXPERIENCE[name]

        technical_score = (
            0.30 * values["推重指标"] / max_thrust_mass
            + 0.25 * values["推进工作时间"] / max_burn_time
            + 0.20 * values["气动效率系数"] / max_aero_efficiency
            + 0.15 * values["推进剂质量分数"] / max_propellant_fraction
            + 0.10 * clip01(values["最大制导加速度"] / 250.0)
        )

        # 周期评分直接采用经验公式 preScore 的权重口径。
        period_score = (
            0.50 * exp["参数完整度"]
            + 0.30 * exp["动力成熟度"]
            + 0.20 * exp["气动成熟度"]
        )

        # 风险维度转换为“风险可控性”，分数越高表示资料和技术风险越低。
        risk_control_score = 0.25 * (
            exp["参数完整度"]
            + exp["动力成熟度"]
            + exp["气动成熟度"]
            + exp["复杂度评分"]
        )

        # 经济性综合质量、几何包络和复杂度；轻量紧凑且简单成熟的构型得分更高。
        economy_score = (
            0.35 * min_mass / values["初始质量"]
            + 0.20 * min_length / values["弹长"]
            + 0.15 * min_span / values["翼展"]
            + 0.30 * exp["复杂度评分"]
        )

        dimension_scores = {
            "技术性": clip01(technical_score),
            "周期": clip01(period_score),
            "风险可控性": clip01(risk_control_score),
            "经济性": clip01(economy_score),
        }
        overall_score = sum(
            dimension_scores[key] * weight
            for key, weight in DIMENSION_WEIGHTS.items()
        )

        # 缺少统一仿真输出时只执行可计算的设计参数预筛，不伪造严格 gatePass。
        design_boundary_pass = bool(
            values["初始质量"] > values["燃尽质量"] > 0.0
            and values["最大推力"] > 0.0
            and values["最大制导加速度"] <= 250.0
            and exp["参数完整度"] >= 0.90
        )

        results.append(
            {
                "方案": name,
                "动力拓扑": values["动力拓扑"],
                "气动布局": values["气动布局"],
                "技术性": dimension_scores["技术性"],
                "周期": dimension_scores["周期"],
                "风险可控性": dimension_scores["风险可控性"],
                "经济性": dimension_scores["经济性"],
                "综合评分": clip01(overall_score),
                "设计边界预筛通过": design_boundary_pass,
                "参数完整度": exp["参数完整度"],
                "复杂度评分": exp["复杂度评分"],
                "初始质量": values["初始质量"],
                "最大推力": values["最大推力"],
                "最大制导加速度": values["最大制导加速度"],
            }
        )

    results.sort(key=lambda row: row["综合评分"], reverse=True)
    for rank, row in enumerate(results, start=1):
        row["综合排名"] = rank

    candidates = [row for row in results if row["设计边界预筛通过"]]
    assert candidates, "没有通过设计边界预筛的候选构型"
    best = max(candidates, key=lambda row: row["综合评分"])
    return results, best


def write_results(results, best):
    """保存可复核的 JSON 和 CSV 权衡结果，便于后续评审追溯。"""
    payload = {
        "评价对象": "车载防空导弹四构型架构方案",
        "评价维度": list(DIMENSION_WEIGHTS.keys()),
        "维度权重": DIMENSION_WEIGHTS,
        "评价口径": "四维均为收益型分数，分数越高越优",
        "经验公式来源": "F://SysbuilderMCP//example//车载防空导弹//构型经验公式.md",
        "数据边界": (
            "未伪造 minMissDistance、guidanceCommandChatter 等统一仿真输出；"
            "本次为模型实例参数与经验成熟度驱动的架构初筛。"
        ),
        "严格门槛状态": "因统一仿真输出不完整，严格 gatePass 未计算",
        "最优方案": best["方案"],
        "最优方案综合评分": best["综合评分"],
        "结果": results,
    }
    with open(RESULT_JSON, "w", encoding="utf-8") as result_file:
        json.dump(payload, result_file, ensure_ascii=False, indent=2)

    fields = [
        "综合排名", "方案", "动力拓扑", "气动布局", "技术性", "周期",
        "风险可控性", "经济性", "综合评分", "设计边界预筛通过",
        "参数完整度", "复杂度评分", "初始质量", "最大推力", "最大制导加速度",
    ]
    with open(RESULT_CSV, "w", encoding="utf-8-sig", newline="") as result_file:
        writer = csv.DictWriter(result_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in results)


def draw_tradeoff(results, best):
    """绘制四维雷达图和综合评分图，供 Sysbuilder 自动保存为权衡证据。"""
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False

    dimensions = list(DIMENSION_WEIGHTS.keys())
    angles = np.linspace(0.0, 2.0 * math.pi, len(dimensions), endpoint=False)
    closed_angles = np.concatenate((angles, [angles[0]]))

    figure = plt.figure(figsize=(13, 6.5))
    radar = figure.add_subplot(1, 2, 1, polar=True)
    for row in sorted(results, key=lambda item: item["方案"]):
        values = [row[dimension] for dimension in dimensions]
        closed_values = np.concatenate((values, [values[0]]))
        width = 2.8 if row["方案"] == best["方案"] else 1.5
        radar.plot(closed_angles, closed_values, linewidth=width, marker="o", label=row["方案"])
        radar.fill(closed_angles, closed_values, alpha=0.08)
    radar.set_thetagrids(angles * 180.0 / math.pi, dimensions)
    radar.set_ylim(0.0, 1.0)
    radar.set_title("四构型架构权衡雷达图")
    radar.legend(loc="lower right", bbox_to_anchor=(1.28, -0.05))

    bar = figure.add_subplot(1, 2, 2)
    ordered = sorted(results, key=lambda item: item["综合评分"], reverse=True)
    colors = ["#2E86DE" if row["方案"] == best["方案"] else "#9EC5E5" for row in ordered]
    bars = bar.bar([row["方案"] for row in ordered], [row["综合评分"] for row in ordered], color=colors)
    bar.set_ylim(0.0, 1.05)
    bar.set_ylabel("综合评分")
    bar.set_title("等权四维综合评分")
    for item, patch in zip(ordered, bars):
        suffix = "（最优）" if item["方案"] == best["方案"] else ""
        bar.text(
            patch.get_x() + patch.get_width() / 2.0,
            patch.get_height() + 0.015,
            f"{item['综合评分']:.3f}{suffix}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    figure.suptitle("车载防空导弹架构权衡结果", fontsize=15)
    figure.tight_layout()
    plt.show()


def main():
    """完成四方案架构权衡并输出唯一最优方案。"""
    results, best = calculate_scores()
    write_results(results, best)
    draw_tradeoff(results, best)
    print("TRADEOFF_BEST:" + best["方案"])
    print("TRADEOFF_SCORE:" + f"{best['综合评分']:.6f}")
    for row in results:
        print(
            "TRADEOFF_RESULT:"
            + row["方案"]
            + ":"
            + f"{row['技术性']:.6f},"
            + f"{row['周期']:.6f},"
            + f"{row['风险可控性']:.6f},"
            + f"{row['经济性']:.6f},"
            + f"{row['综合评分']:.6f},"
            + str(row["设计边界预筛通过"])
        )


main()
