"""
蒙特卡洛模拟：计算每个猫格类型的出现概率
模拟逻辑与 index.html 中 computeResult() 完全一致
"""

import random
import math
from collections import defaultdict

# ── 20种猫格原型向量 [D2, D7, D3, D6] ──────────────────────────
NORMAL_TYPES = [
    ("ZZZZ", [2, 2, 3, 2]),  # 瞌睡虫
    ("OJBK",  [1, 1, 1, 3]),  # 关我屁事
    ("MONK",  [1, 1, 3, 5]),  # 绝育僧
    ("CLEN",  [1, 1, 5, 3]),  # 洁癖星人
    ("BOSS",  [1, 3, 5, 4]),  # 霸总
    ("SEXY",  [3, 1, 1, 3]),  # 肚皮尤物
    ("MALO",  [1, 1, 1, 4]),  # 打工猫喽
    ("FOOD",  [2, 2, 5, 4]),  # 干饭机器
    ("YOLO",  [3, 3, 1, 1]),  # 穷开心
    ("GOGO",  [5, 5, 3, 4]),  # 跑酷选手
    ("WOC",   [4, 3, 2, 1]),  # 握草无敌
    ("CRAZ",  [4, 1, 1, 1]),  # 疯批本批
    ("FIRE",  [5, 5, 3, 2]),  # 显眼包
    ("TALK",  [5, 5, 1, 3]),  # 碎嘴话唠
    ("HUGS",  [3, 4, 1, 1]),  # 粘人挂件
    ("SOUL",  [5, 5, 5, 3]),  # 灵魂床伴
]

# ── 各维度题目映射 ─────────────────────────────────────────────
# dim -> question indices (0-based)
DIM_QUESTIONS = {
    "D2":    [1, 3, 5, 14],          # q2, q4, q6, q15
    "D7":    [0, 4, 9, 14],          # q1, q5, q10, q15
    "D3":    [2, 6, 8],              # q3, q7, q9
    "D6":    [7, 11, 12, 13],        # q8, q12, q13, q14
}
EASTER_Q = 10  # q11 (0-based index)

# ── 隐藏款触发条件（与JS一致）──────────────────────────────────
ZONE_PENALTY = {
    'LL': 0, 'MM': 0, 'HH': 0,
    'LM': 1, 'ML': 1, 'HM': 1, 'MH': 1,
    'LH': 2, 'HL': 2,
}

def get_zone(s):
    """1-5分制 -> L/M/H"""
    return 'L' if s < 2.5 else ('H' if s > 3.5 else 'M')

def compute_type(user_vec, easter_val):
    """
    复现 JS computeResult() 逻辑
    user_vec: [D2, D7, D3, D6] 归一化分数 (1.0~5.0)
    返回类型代码
    """
    user_zones = [get_zone(s) for s in user_vec]

    # ── 计算与所有常规类型的有效距离 ──────────────────────────
    ranked = []
    for code, tvec in NORMAL_TYPES:
        dist_sq = sum((user_vec[i] - tvec[i]) ** 2 for i in range(4)) ** 0.5
        exact = sum(1 for i in range(4) if abs(user_vec[i] - tvec[i]) < 0.5)
        sim = max(0, round((1 - dist_sq / math.sqrt(4 * 16)) * 100))

        # 区间惩罚
        t_zones = [get_zone(v) for v in tvec]
        penalty = sum(ZONE_PENALTY.get(user_zones[i] + t_zones[i], 0) for i in range(4))
        eff_dist = dist_sq + penalty
        ranked.append((code, eff_dist, dist_sq, exact, sim, tvec))

    ranked.sort(key=lambda x: (x[1], -x[3], -x[4]))

    # ── Top-3 加权随机抽取 ─────────────────────────────────────
    top3 = ranked[:3]
    weights = [1 / (r[1] + 0.1) ** 2 for r in top3]
    total_w = sum(weights)
    pick = random.random() * total_w
    best_normal = top3[0][0]
    cum = 0
    for i, w in enumerate(weights):
        cum += w
        if pick <= cum:
            best_normal = top3[i][0]
            break

    # ── 隐藏款判断 ─────────────────────────────────────────────
    d2, d7, d3, d6 = user_vec
    mean = (d2 + d7 + d3 + d6) / 4

    # ANCE 小祖宗
    if easter_val == 5 and d3 >= 3.5 and d7 >= 3.0:
        return "ANCE"
    # BABE 恋爱脑
    if d2 >= 3.5 and d7 >= 3.5 and d3 >= 3.5 and random.random() < 0.40:
        return "BABE"
    # MUM 妈猫
    if d2 < 3.5 and d7 >= 3.5 and d3 >= 3.5 and d6 >= 3.0 and random.random() < 0.75:
        return "MUM"
    # LUCK 招财猫
    if d2 >= 2.5 and d3 < 2.5 and d6 >= 3.5 and random.random() < 0.60:
        return "LUCK"

    return best_normal


def simulate_one():
    """
    模拟一个用户的随机答题 + 结果计算
    返回类型代码
    """
    # 15道题，每题随机选1-5
    answers = [random.randint(1, 5) for _ in range(15)]

    # 累积各维度原始分
    raw_sums = {"D2": 0, "D7": 0, "D3": 0, "D6": 0}
    raw_counts = {"D2": 0, "D7": 0, "D3": 0, "D6": 0}

    for qi, dim in [(0,"D7"),(1,"D2"),(2,"D3"),(3,"D2"),(4,"D7"),
                    (5,"D2"),(6,"D3"),(7,"D6"),(8,"D3"),(9,"D7"),
                    (10,"EASTER"),(11,"D6"),(12,"D6"),(13,"D6"),(14,"D2D7")]:
        val = answers[qi]
        if dim == "D2D7":
            raw_sums["D2"] += val; raw_counts["D2"] += 1
            raw_sums["D7"] += val; raw_counts["D7"] += 1
        elif dim != "EASTER":
            raw_sums[dim] += val
            raw_counts[dim] += 1

    # 归一化到1-5分制
    norm = {dim: raw_sums[dim] / raw_counts[dim] for dim in raw_sums}
    user_vec = [norm["D2"], norm["D7"], norm["D3"], norm["D6"]]
    easter_val = answers[10]

    return compute_type(user_vec, easter_val)


# ── 蒙特卡洛主循环 ─────────────────────────────────────────────
N = 1_000_000
print(f"Running Monte Carlo with {N:,} simulations...")

counts = defaultdict(int)
for _ in range(N):
    t = simulate_one()
    counts[t] += 1

# ── 输出结果 ────────────────────────────────────────────────────
CN_NAMES = {
    "ZZZZ": "瞌睡虫", "OJBK": "关我屁事", "MONK": "绝育僧",
    "CLEN": "洁癖星人", "BOSS": "霸总",     "SEXY": "肚皮尤物",
    "MALO": "打工猫喽", "FOOD": "干饭机器",  "YOLO": "穷开心",
    "GOGO": "跑酷选手", "WOC": "握草无敌",   "CRAZ": "疯批本批",
    "FIRE": "显眼包",   "TALK": "碎嘴话唠",  "HUGS": "粘人挂件",
    "SOUL": "灵魂床伴",
    "ANCE": "小祖宗",   "BABE": "恋爱脑",    "MUM": "妈猫",
    "LUCK": "招财猫",
}

total = sum(counts.values())
print(f"\n{'─'*55}")
print(f"{'猫格类型':<12} {'中文名':<10} {'次数':>8} {'概率':>8}")
print(f"{'─'*55}")

sorted_types = sorted(counts.items(), key=lambda x: -x[1])
for code, cnt in sorted_types:
    pct = cnt / total * 100
    name = CN_NAMES.get(code, code)
    bar = "█" * int(pct / 2)
    print(f"{code:<12} {name:<10} {cnt:>8,}  {pct:>6.2f}%  {bar}")

print(f"{'─'*55}")
print(f"{'合计':>24} {total:>8,}  100.00%")

# ── 验证：JS注释里说 ANCE <1%, BABE <2%, MUM <2%, LUCK <4% ──
print(f"\n✅ 隐藏款触发验证（基于 {N:,} 次模拟）:")
for code in ["ANCE", "BABE", "MUM", "LUCK"]:
    pct = counts[code] / total * 100
    print(f"   {code}: {pct:.3f}%")
