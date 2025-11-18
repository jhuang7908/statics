"""
生成统计模拟数据脚本
运行后会在 data/ 目录生成多个 CSV 测试文件
"""
import pandas as pd
import numpy as np
import os
import sys

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 创建 data 目录
os.makedirs('data', exist_ok=True)

# 设置随机种子以保证可重复性
np.random.seed(42)

print("开始生成模拟数据...")

# ==================== 1. 两组比较（正态分布） ====================
n1, n2 = 30, 30
group1 = np.random.normal(loc=10, scale=2, size=n1)
group2 = np.random.normal(loc=12, scale=2, size=n2)  # 均值差异

df_two_normal = pd.DataFrame({
    'group': ['Group_A'] * n1 + ['Group_B'] * n2,
    'value': np.concatenate([group1, group2])
})

df_two_normal.to_csv('data/two_groups_normal.csv', index=False)
print("[OK] 已生成：data/two_groups_normal.csv")

# ==================== 2. 两组比较（非正态分布） ====================
n1, n2 = 25, 25
# 第一组：对数正态分布
group1 = np.random.lognormal(mean=2, sigma=0.5, size=n1)
# 第二组：带离群点的偏态分布
group2 = np.random.gamma(shape=2, scale=3, size=n2)
# 添加一些离群点
outliers = np.random.uniform(20, 30, size=3)
group2 = np.concatenate([group2, outliers])

df_two_nonnormal = pd.DataFrame({
    'group': ['Treatment'] * len(group1) + ['Control'] * len(group2),
    'value': np.concatenate([group1, group2])
})

df_two_nonnormal.to_csv('data/two_groups_nonnormal.csv', index=False)
print("[OK] 已生成：data/two_groups_nonnormal.csv")

# ==================== 3. 多组比较（ANOVA） ====================
n_per_group = 20
group_a = np.random.normal(loc=15, scale=3, size=n_per_group)
group_b = np.random.normal(loc=18, scale=3, size=n_per_group)
group_c = np.random.normal(loc=20, scale=3, size=n_per_group)
group_d = np.random.normal(loc=16, scale=3, size=n_per_group)

df_anova = pd.DataFrame({
    'treatment': (['Drug_A'] * n_per_group + 
                  ['Drug_B'] * n_per_group + 
                  ['Drug_C'] * n_per_group + 
                  ['Placebo'] * n_per_group),
    'response': np.concatenate([group_a, group_b, group_c, group_d])
})

df_anova.to_csv('data/anova_three_groups.csv', index=False)
print("[OK] 已生成：data/anova_three_groups.csv")

# ==================== 4. 相关性分析（线性相关） ====================
n = 50
x = np.random.normal(loc=10, scale=3, size=n)
# y 与 x 有中等程度的线性相关
y = 2 + 1.5 * x + np.random.normal(loc=0, scale=2, size=n)

df_corr = pd.DataFrame({
    'x': x,
    'y': y
})

df_corr.to_csv('data/correlation_linear.csv', index=False)
print("[OK] 已生成：data/correlation_linear.csv")

# ==================== 5. 简单线性回归 ====================
n = 40
x = np.linspace(0, 20, n)
# y = 3 + 2*x + 噪声
y = 3 + 2 * x + np.random.normal(loc=0, scale=1.5, size=n)

df_reg = pd.DataFrame({
    'dose': x,
    'effect': y
})

df_reg.to_csv('data/regression_simple.csv', index=False)
print("[OK] 已生成：data/regression_simple.csv")

# ==================== 额外：混合数据（包含多个变量） ====================
n = 60
df_mixed = pd.DataFrame({
    'patient_id': range(1, n + 1),
    'age': np.random.normal(loc=45, scale=10, size=n).astype(int),
    'gender': np.random.choice(['Male', 'Female'], size=n),
    'treatment': np.random.choice(['A', 'B', 'C'], size=n),
    'baseline': np.random.normal(loc=100, scale=15, size=n),
    'outcome': np.random.normal(loc=85, scale=12, size=n),
    'score': np.random.uniform(0, 100, size=n)
})

df_mixed.to_csv('data/mixed_data.csv', index=False)
print("[OK] 已生成：data/mixed_data.csv（包含多个变量类型）")

print("\n[完成] 所有模拟数据生成完成！")
print(f"[路径] 数据文件保存在：{os.path.abspath('data')}")

