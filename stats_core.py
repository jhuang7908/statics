"""
经典统计分析核心函数
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import shapiro, levene
import statsmodels.api as sm
from statsmodels.stats.power import ttest_power


def two_group_compare(df, value_col, group_col, alpha=0.05):
    """
    两组比较：自动选择 t 检验或 Mann-Whitney U 检验
    
    参数:
        df: DataFrame
        value_col: 数值变量列名
        group_col: 分组变量列名
        alpha: 显著性水平
    
    返回:
        dict: 包含方法名、统计量、p值、额外信息、中文解释
    """
    # 获取两组数据
    groups = df[group_col].unique()
    if len(groups) != 2:
        raise ValueError(f"分组变量必须恰好有 2 个组，当前有 {len(groups)} 个组")
    
    group1 = df[df[group_col] == groups[0]][value_col].dropna()
    group2 = df[df[group_col] == groups[1]][value_col].dropna()
    
    if len(group1) < 3 or len(group2) < 3:
        raise ValueError("每组至少需要 3 个观测值")
    
    # 正态性检验（Shapiro-Wilk，样本量较小时）
    # 注意：Shapiro-Wilk 在样本量 > 5000 时可能不准确
    n1, n2 = len(group1), len(group2)
    use_shapiro = n1 <= 5000 and n2 <= 5000
    
    if use_shapiro:
        _, p_norm1 = shapiro(group1)
        _, p_norm2 = shapiro(group2)
        both_normal = p_norm1 > 0.05 and p_norm2 > 0.05
    else:
        # 样本量太大时，使用偏度和峰度检验
        from scipy.stats import normaltest
        _, p_norm1 = normaltest(group1)
        _, p_norm2 = normaltest(group2)
        both_normal = p_norm1 > 0.05 and p_norm2 > 0.05
    
    # 方差齐性检验（Levene）
    _, p_var = levene(group1, group2)
    equal_var = p_var > 0.05
    
    # 选择检验方法
    if both_normal and equal_var:
        # 独立样本 t 检验
        stat, p_value = stats.ttest_ind(group1, group2, equal_var=True)
        method_name = "独立样本 t 检验（等方差）"
        
        # 计算效应量（Cohen's d）
        pooled_std = np.sqrt(((n1 - 1) * group1.std()**2 + (n2 - 1) * group2.std()**2) / (n1 + n2 - 2))
        cohens_d = (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0
        
        extra_info = {
            'group1_mean': group1.mean(),
            'group2_mean': group2.mean(),
            'group1_std': group1.std(),
            'group2_std': group2.std(),
            'cohens_d': cohens_d,
            'normality_p1': p_norm1 if use_shapiro else None,
            'normality_p2': p_norm2 if use_shapiro else None,
            'levene_p': p_var
        }
        
    elif both_normal and not equal_var:
        # Welch's t 检验（不等方差）
        stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
        method_name = "Welch's t 检验（不等方差）"
        
        pooled_std = np.sqrt((group1.std()**2 / n1 + group2.std()**2 / n2))
        cohens_d = (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0
        
        extra_info = {
            'group1_mean': group1.mean(),
            'group2_mean': group2.mean(),
            'group1_std': group1.std(),
            'group2_std': group2.std(),
            'cohens_d': cohens_d,
            'normality_p1': p_norm1 if use_shapiro else None,
            'normality_p2': p_norm2 if use_shapiro else None,
            'levene_p': p_var
        }
        
    else:
        # Mann-Whitney U 检验（非参数）
        stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        method_name = "Mann-Whitney U 检验（非参数）"
        
        # 计算效应量（r = Z / sqrt(N)）
        z_score = stats.norm.ppf(p_value / 2) if p_value < 0.5 else 0
        r_effect = abs(z_score) / np.sqrt(n1 + n2)
        
        extra_info = {
            'group1_median': group1.median(),
            'group2_median': group2.median(),
            'group1_iqr': group1.quantile(0.75) - group1.quantile(0.25),
            'group2_iqr': group2.quantile(0.75) - group2.quantile(0.25),
            'r_effect': r_effect,
            'normality_p1': p_norm1 if use_shapiro else None,
            'normality_p2': p_norm2 if use_shapiro else None
        }
    
    # 生成解释
    if p_value < alpha:
        explanation_zh = f"p = {p_value:.4f} < {alpha}，两组间差异具有统计学意义（α = {alpha}）。"
    else:
        explanation_zh = f"p = {p_value:.4f} ≥ {alpha}，两组间差异无统计学意义（α = {alpha}）。"
    
    return {
        'method_name': method_name,
        'stat': stat,
        'p_value': p_value,
        'extra_info': extra_info,
        'explanation_zh': explanation_zh
    }


def anova_oneway(df, value_col, group_col, alpha=0.05):
    """
    单因素方差分析（ANOVA）
    
    参数:
        df: DataFrame
        value_col: 数值变量列名
        group_col: 分组变量列名
        alpha: 显著性水平
    
    返回:
        dict: 包含方法名、统计量、p值、额外信息、中文解释
    """
    # 获取各组数据
    groups = df[group_col].unique()
    if len(groups) < 2:
        raise ValueError("分组变量至少需要 2 个组")
    
    group_data = [df[df[group_col] == g][value_col].dropna() for g in groups]
    
    # 检查每组至少 2 个观测
    if any(len(g) < 2 for g in group_data):
        raise ValueError("每组至少需要 2 个观测值")
    
    # 执行 ANOVA
    f_stat, p_value = stats.f_oneway(*group_data)
    
    # 计算组间和组内平方和
    all_values = df[value_col].dropna()
    grand_mean = all_values.mean()
    
    ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in group_data)
    ss_within = sum((g - g.mean()).pow(2).sum() for g in group_data)
    ss_total = ss_between + ss_within
    
    df_between = len(groups) - 1
    df_within = len(all_values) - len(groups)
    df_total = len(all_values) - 1
    
    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_within = ss_within / df_within if df_within > 0 else 0
    
    # 计算效应量（eta-squared）
    eta_squared = ss_between / ss_total if ss_total > 0 else 0
    
    # 组均值
    group_means = {g: data.mean() for g, data in zip(groups, group_data)}
    group_stds = {g: data.std() for g, data in zip(groups, group_data)}
    
    extra_info = {
        'n_groups': len(groups),
        'group_means': group_means,
        'group_stds': group_stds,
        'ss_between': ss_between,
        'ss_within': ss_within,
        'ss_total': ss_total,
        'df_between': df_between,
        'df_within': df_within,
        'ms_between': ms_between,
        'ms_within': ms_within,
        'eta_squared': eta_squared
    }
    
    method_name = "单因素方差分析（One-way ANOVA）"
    
    # 生成解释
    if p_value < alpha:
        explanation_zh = f"p = {p_value:.4f} < {alpha}，各组间差异具有统计学意义（α = {alpha}）。建议进行事后检验（如 Tukey HSD）以确定具体哪些组间存在差异。"
    else:
        explanation_zh = f"p = {p_value:.4f} ≥ {alpha}，各组间差异无统计学意义（α = {alpha}）。"
    
    return {
        'method_name': method_name,
        'stat': f_stat,
        'p_value': p_value,
        'extra_info': extra_info,
        'explanation_zh': explanation_zh
    }


def correlation(df, col_x, col_y, method="auto", alpha=0.05):
    """
    相关性分析：自动选择 Pearson 或 Spearman
    
    参数:
        df: DataFrame
        col_x: 变量 X 列名
        col_y: 变量 Y 列名
        method: "auto", "pearson", "spearman"
        alpha: 显著性水平
    
    返回:
        dict: 包含方法名、统计量、p值、额外信息、中文解释
    """
    # 去除缺失值
    data = df[[col_x, col_y]].dropna()
    
    if len(data) < 3:
        raise ValueError("至少需要 3 对有效观测值")
    
    x = data[col_x]
    y = data[col_y]
    
    # 自动选择方法
    if method == "auto":
        # 检查是否近似正态（使用偏度和峰度）
        from scipy.stats import normaltest
        _, p_x = normaltest(x)
        _, p_y = normaltest(y)
        
        if p_x > 0.05 and p_y > 0.05:
            method = "pearson"
        else:
            method = "spearman"
    
    # 执行相关性检验
    if method == "pearson":
        stat, p_value = stats.pearsonr(x, y)
        method_name = "Pearson 相关系数"
    else:
        stat, p_value = stats.spearmanr(x, y)
        method_name = "Spearman 等级相关系数"
    
    # 计算置信区间（仅 Pearson）
    if method == "pearson" and len(data) > 3:
        n = len(data)
        z = np.arctanh(stat)  # Fisher's z transformation
        se = 1 / np.sqrt(n - 3)
        z_lower = z - 1.96 * se
        z_upper = z + 1.96 * se
        ci_lower = np.tanh(z_lower)
        ci_upper = np.tanh(z_upper)
        ci = (ci_lower, ci_upper)
    else:
        ci = None
    
    extra_info = {
        'correlation_coefficient': stat,
        'n': len(data),
        'x_mean': x.mean(),
        'y_mean': y.mean(),
        'x_std': x.std(),
        'y_std': y.std(),
        'ci_95': ci
    }
    
    # 生成解释
    abs_r = abs(stat)
    if abs_r < 0.1:
        strength = "几乎无相关"
    elif abs_r < 0.3:
        strength = "弱相关"
    elif abs_r < 0.5:
        strength = "中等相关"
    elif abs_r < 0.7:
        strength = "强相关"
    else:
        strength = "极强相关"
    
    direction = "正" if stat > 0 else "负"
    
    if p_value < alpha:
        explanation_zh = f"r = {stat:.4f}，{direction}{strength}（p = {p_value:.4f} < {alpha}，具有统计学意义）。"
    else:
        explanation_zh = f"r = {stat:.4f}，{direction}{strength}（p = {p_value:.4f} ≥ {alpha}，无统计学意义）。"
    
    return {
        'method_name': method_name,
        'stat': stat,
        'p_value': p_value,
        'extra_info': extra_info,
        'explanation_zh': explanation_zh
    }


def linear_regression_simple(df, x_col, y_col, alpha=0.05):
    """
    简单线性回归
    
    参数:
        df: DataFrame
        x_col: 自变量列名
        y_col: 因变量列名
        alpha: 显著性水平
    
    返回:
        dict: 包含方法名、统计量、p值、额外信息、中文解释
    """
    # 去除缺失值
    data = df[[x_col, y_col]].dropna()
    
    if len(data) < 3:
        raise ValueError("至少需要 3 对有效观测值")
    
    x = data[x_col]
    y = data[y_col]
    
    # 使用 statsmodels 进行回归
    X = sm.add_constant(x)  # 添加常数项
    model = sm.OLS(y, X).fit()
    
    # 提取结果
    slope = model.params[x_col]
    intercept = model.params['const']
    r_squared = model.rsquared
    p_value = model.pvalues[x_col]
    
    # F 统计量
    f_stat = model.fvalue
    f_pvalue = model.f_pvalue
    
    # 残差标准误
    std_err = np.sqrt(model.mse_resid)
    
    # 斜率的标准误和置信区间
    slope_se = model.bse[x_col]
    slope_ci = model.conf_int(alpha=alpha).loc[x_col]
    
    extra_info = {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'adj_r_squared': model.rsquared_adj,
        'std_err': std_err,
        'slope_se': slope_se,
        'slope_ci_lower': slope_ci[0],
        'slope_ci_upper': slope_ci[1],
        'f_statistic': f_stat,
        'f_pvalue': f_pvalue,
        'n': len(data)
    }
    
    method_name = "简单线性回归（OLS）"
    
    # 生成解释
    if p_value < alpha:
        explanation_zh = f"回归方程：y = {intercept:.4f} + {slope:.4f} × x。斜率具有统计学意义（p = {p_value:.4f} < {alpha}），R² = {r_squared:.4f}。"
    else:
        explanation_zh = f"回归方程：y = {intercept:.4f} + {slope:.4f} × x。斜率无统计学意义（p = {p_value:.4f} ≥ {alpha}），R² = {r_squared:.4f}。"
    
    return {
        'method_name': method_name,
        'stat': f_stat,  # 使用 F 统计量
        'p_value': p_value,  # 斜率的 p 值
        'extra_info': extra_info,
        'explanation_zh': explanation_zh
    }

