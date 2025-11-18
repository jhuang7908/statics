import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from stats_core import (
    two_group_compare,
    anova_oneway,
    correlation,
    linear_regression_simple
)
from ollama_client import ask_model
from io import BytesIO
from datetime import datetime
import platform
import os
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    REPORTLAB_AVAILABLE = True
    
    # 注册中文字体
    def register_chinese_fonts():
        """注册中文字体"""
        try:
            # Windows系统字体路径
            if platform.system() == 'Windows':
                # 尝试注册常见的中文字体
                font_paths = [
                    r'C:\Windows\Fonts\simhei.ttf',  # 黑体
                    r'C:\Windows\Fonts\simsun.ttc',  # 宋体
                    r'C:\Windows\Fonts\msyh.ttc',   # 微软雅黑
                    r'C:\Windows\Fonts\msyhbd.ttc',  # 微软雅黑 Bold
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            if 'simhei' in font_path.lower():
                                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                return 'ChineseFont'
                            elif 'simsun' in font_path.lower():
                                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                return 'ChineseFont'
                            elif 'msyh' in font_path.lower():
                                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                return 'ChineseFont'
                        except:
                            continue
                # 如果找不到字体文件，使用UnicodeCIDFont（需要reportlab的字体支持）
                try:
                    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))  # 宋体
                    return 'STSong-Light'
                except:
                    pass
            # Linux/Mac系统
            else:
                try:
                    # 尝试使用系统字体
                    font_paths = [
                        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # 文泉驿微米黑
                        '/System/Library/Fonts/PingFang.ttc',  # macOS 苹方
                    ]
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                            return 'ChineseFont'
                except:
                    pass
                # 使用UnicodeCIDFont作为备选
                try:
                    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                    return 'STSong-Light'
                except:
                    pass
        except Exception as e:
            pass
        return None
    
    CHINESE_FONT_NAME = register_chinese_fonts()
    
except ImportError:
    REPORTLAB_AVAILABLE = False
    CHINESE_FONT_NAME = None

# 设置页面配置
st.set_page_config(
    page_title="stat-IDE v1",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS - 参考Cursor的紧凑风格（更激进）
st.markdown("""
<style>
    /* 全局字体和行高优化 - 参考Cursor紧凑风格 */
    * {
        line-height: 1.3 !important;
    }
    
    /* 主容器 - 大幅减小padding */
    .main .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }
    
    /* 侧边栏整体 - 统一字体大小，和主页tabs一致 */
    .css-1d391kg {
        font-size: 0.85rem !important;
        padding: 0.3rem !important;
    }
    
    /* 侧边栏标题 - 统一字体 */
    .css-1lcbmhc .css-1outpf7 {
        font-size: 0.85rem !important;
        padding: 0.2rem 0 !important;
        margin-bottom: 0.1rem !important;
    }
    
    /* 侧边栏所有内容 - 统一字体大小（和主页tabs一致） */
    .css-1d391kg * {
        font-size: 0.85rem !important;
    }
    
    /* 侧边栏内容 - 文字和标签 - 统一字体 */
    .css-1d391kg p, .css-1d391kg label, .css-1d391kg .stSelectbox label,
    .css-1d391kg .stSlider label, .css-1d391kg .stCheckbox label,
    .css-1d391kg .stRadio label, .css-1d391kg .stNumberInput label {
        font-size: 0.85rem !important;
        margin-bottom: 0.1rem !important;
        line-height: 1.3 !important;
    }
    
    /* Radio选项文本 - 统一字体 */
    .css-1d391kg .stRadio label p,
    .css-1d391kg .stRadio [data-testid="stMarkdownContainer"] p,
    .css-1d391kg .stRadio [data-testid="stMarkdownContainer"],
    .css-1d391kg .stRadio div[data-baseweb="radio"] label,
    .css-1d391kg .stRadio span {
        font-size: 0.85rem !important;
        line-height: 1.3 !important;
    }
    
    /* 侧边栏输入框和选择框 */
    .css-1d391kg .stSelectbox, .css-1d391kg .stSlider, 
    .css-1d391kg .stCheckbox, .css-1d391kg .stNumberInput,
    .css-1d391kg .stRadio {
        margin-bottom: 0.2rem !important;
    }
    
    /* 侧边栏中所有radio选项的文本 - 统一字体 */
    .css-1d391kg [data-testid="stRadio"] label,
    .css-1d391kg [data-testid="stRadio"] span,
    .css-1d391kg [data-testid="stRadio"] div,
    .css-1d391kg [data-testid="stRadio"] button {
        font-size: 0.85rem !important;
    }
    
    /* Expander标题 - 统一字体 */
    .streamlit-expanderHeader {
        font-size: 0.85rem !important;
        padding: 0.25rem 0.4rem !important;
        margin-bottom: 0.1rem !important;
        line-height: 1.3 !important;
    }
    
    /* Expander内容 - 统一字体 */
    .streamlit-expanderContent {
        padding: 0.2rem 0.4rem !important;
        font-size: 0.85rem !important;
    }
    
    /* Expander内容中的所有元素 - 统一字体 */
    .streamlit-expanderContent * {
        font-size: 0.85rem !important;
    }
    
    /* 侧边栏中所有expander标题和内容 - 确保统一字体 */
    .css-1d391kg .streamlit-expanderHeader,
    .css-1d391kg .streamlit-expanderContent,
    .css-1d391kg .streamlit-expanderContent p,
    .css-1d391kg .streamlit-expanderContent li,
    .css-1d391kg .streamlit-expanderContent strong,
    .css-1d391kg .streamlit-expanderContent em {
        font-size: 0.85rem !important;
    }
    
    /* 侧边栏中方法说明的markdown内容 */
    .css-1d391kg .stMarkdown p,
    .css-1d391kg .stMarkdown li,
    .css-1d391kg .stMarkdown strong {
        font-size: 0.85rem !important;
    }
    
    /* 主内容区标题 - 更小 */
    h1 {
        font-size: 1.1rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.3 !important;
    }
    
    h2 {
        font-size: 0.95rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.3 !important;
    }
    
    h3 {
        font-size: 0.9rem !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        line-height: 1.2 !important;
        font-weight: 600 !important;
    }
    
    h4 {
        font-size: 0.8rem !important;
        margin-top: 0.15rem !important;
        margin-bottom: 0.15rem !important;
        line-height: 1.3 !important;
    }
    
    /* Markdown间距 - 更小 */
    .stMarkdown {
        margin-bottom: 0.2rem !important;
        font-size: 0.8rem !important;
    }
    
    /* 主内容区文字 */
    .main .stMarkdown p, .main .stMarkdown li {
        font-size: 0.8rem !important;
        line-height: 1.35 !important;
        margin-bottom: 0.15rem !important;
    }
    
    /* 按钮 - 更紧凑 */
    .stButton button {
        font-size: 0.8rem !important;
        padding: 0.25rem 0.6rem !important;
        margin: 0.15rem 0 !important;
        line-height: 1.3 !important;
    }
    
    /* Selectbox和Slider - 更紧凑 */
    .stSelectbox, .stSlider, .stCheckbox, .stNumberInput {
        margin-bottom: 0.2rem !important;
    }
    
    .stSelectbox label, .stSlider label, .stCheckbox label, .stNumberInput label {
        font-size: 0.75rem !important;
    }
    
    /* 表格 */
    .stDataFrame {
        font-size: 0.75rem !important;
    }
    
    /* Info和Warning框 - 更紧凑 */
    .stInfo, .stWarning, .stError, .stSuccess {
        font-size: 0.75rem !important;
        padding: 0.3rem !important;
        margin: 0.2rem 0 !important;
        line-height: 1.3 !important;
    }
    
    /* Columns间距 - 更小 */
    .stColumns {
        gap: 0.3rem !important;
    }
    
    /* 减小所有元素的垂直间距 */
    div[data-testid] {
        margin-bottom: 0.2rem !important;
    }
    
    /* 顶部栏 - 更紧凑，减少空白 */
    .css-1v0mbdj {
        padding: 0.1rem 0 !important;
    }
    
    /* 减少页面顶部空白 */
    header[data-testid="stHeader"] {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
    
    /* 顶部容器紧凑 */
    .stApp > header {
        padding-top: 0.1rem !important;
    }
    
    /* 减小radio和checkbox的间距 */
    .stRadio, .stCheckbox {
        margin-bottom: 0.15rem !important;
    }
    
    /* Radio选项文本大小 - 统一字体（和主页tabs一致） */
    .stRadio label,
    .stRadio [data-testid="stMarkdownContainer"],
    .stRadio [data-testid="stMarkdownContainer"] p,
    .stRadio div[data-baseweb="radio"] label,
    .stRadio span {
        font-size: 0.85rem !important;
        line-height: 1.3 !important;
    }
    
    /* 侧边栏中的h3标题（模块选择） - 与顶部标题一致 */
    .css-1d391kg h3 {
        font-size: 0.9rem !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        line-height: 1.2 !important;
        font-weight: 600 !important;
    }
    
    /* 顶部栏中的h3标题（stat-IDE标题） - 与侧边栏模块选择一致 */
    .main h3 {
        font-size: 0.9rem !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        line-height: 1.2 !important;
        font-weight: 600 !important;
    }
    
    /* 侧边栏中的所有文本元素 - 统一字体 */
    .css-1d391kg .stSelectbox,
    .css-1d391kg .stSlider,
    .css-1d391kg .stCheckbox,
    .css-1d391kg .stNumberInput,
    .css-1d391kg .stTextInput,
    .css-1d391kg .stTextArea,
    .css-1d391kg .stButton,
    .css-1d391kg .stFileUploader {
        font-size: 0.85rem !important;
    }
    
    /* 侧边栏中的Info和Warning框 - 统一字体 */
    .css-1d391kg .stInfo,
    .css-1d391kg .stWarning,
    .css-1d391kg .stError,
    .css-1d391kg .stSuccess {
        font-size: 0.85rem !important;
    }
    
    /* 减小slider的垂直间距 */
    .stSlider {
        margin-bottom: 0.2rem !important;
    }
    
    /* 代码块 */
    .stCodeBlock {
        font-size: 0.7rem !important;
        padding: 0.25rem !important;
        margin: 0.15rem 0 !important;
        line-height: 1.3 !important;
    }
    
    /* 文件上传器 */
    .stFileUploader {
        margin-bottom: 0.2rem !important;
    }
    
    /* Divider */
    hr {
        margin: 0.3rem 0 !important;
    }
    
    /* 顶部栏标题和tabs对齐 - 确保同一行顶部对齐 */
    [data-testid="stHorizontalBlock"]:has(> div:has(h3)) {
        align-items: flex-start !important;
    }
    
    /* 标题列垂直对齐到tabs顶部 */
    div[data-testid="stHorizontalBlock"] > div:first-child:has(h3) {
        display: flex !important;
        align-items: flex-start !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* tabs列 */
    div[data-testid="stHorizontalBlock"] > div:has([data-baseweb="tabs"]) {
        display: flex !important;
        align-items: flex-start !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* 标题h3在顶部栏中与tabs顶部对齐 */
    div[data-testid="stHorizontalBlock"] h3 {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    
    /* 确保tabs容器与标题顶部对齐 */
    [data-baseweb="tabs"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* tabs标签文字与标题文字顶部对齐 */
    [data-baseweb="tabs"] [role="tablist"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* tabs标签按钮与标题对齐 */
    [data-baseweb="tabs"] [role="tab"] {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 设置中文字体 - 确保正确显示中文
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False
# 确保字体设置生效
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 尝试设置具体的中文字体
try:
    # Windows 系统
    if platform.system() == 'Windows':
        # 尝试找到中文字体
        import matplotlib.font_manager as fm
        font_list = [f.name for f in fm.fontManager.ttflist]
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']
        for font_name in chinese_fonts:
            if font_name in font_list:
                plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
                matplotlib.rcParams['font.sans-serif'] = [font_name] + matplotlib.rcParams['font.sans-serif']
                break
    # Linux/Mac 系统
    else:
        # 尝试使用系统字体
        import matplotlib.font_manager as fm
        font_list = [f.name for f in fm.fontManager.ttflist]
        chinese_fonts = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC']
        for font_name in chinese_fonts:
            if font_name in font_list:
                plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
                matplotlib.rcParams['font.sans-serif'] = [font_name] + matplotlib.rcParams['font.sans-serif']
                break
except:
    pass

# 初始化 session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'current_results' not in st.session_state:
    st.session_state.current_results = None
if 'current_df' not in st.session_state:
    st.session_state.current_df = None
if 'current_params' not in st.session_state:
    st.session_state.current_params = {}
# 图形美化参数
if 'plot_fontsize' not in st.session_state:
    st.session_state.plot_fontsize = 10  # 默认9-10pt
if 'plot_linewidth' not in st.session_state:
    st.session_state.plot_linewidth = 0.8  # 默认细线
if 'plot_pointsize' not in st.session_state:
    st.session_state.plot_pointsize = 50  # 默认点大小（增大以便更明显）
if 'plot_show_legend' not in st.session_state:
    st.session_state.plot_show_legend = True
if 'plot_theme' not in st.session_state:
    st.session_state.plot_theme = "自然风格（Nature-like）"
if 'plot_color_scheme' not in st.session_state:
    st.session_state.plot_color_scheme = "蓝色系"
if 'plot_type' not in st.session_state:
    st.session_state.plot_type = "箱线图"
if 'plot_width' not in st.session_state:
    st.session_state.plot_width = 6.0  # 图形宽度（英寸）- 减小默认尺寸
if 'plot_height' not in st.session_state:
    st.session_state.plot_height = 4.5  # 图形高度（英寸）- 减小默认尺寸
if 'plot_aspect' not in st.session_state:
    st.session_state.plot_aspect = "正方形"  # 图形比例：宽、正方形、高
if 'show_pvalue' not in st.session_state:
    st.session_state.show_pvalue = True  # 是否显示P值
if 'show_stats' not in st.session_state:
    st.session_state.show_stats = []  # 显示的统计量：平均值、中位数、置信区间、标准差、标准误
if 'bar_width' not in st.session_state:
    st.session_state.bar_width = 0.7  # 柱状图宽度（0-1之间）
if 'bar_spacing' not in st.session_state:
    st.session_state.bar_spacing = 0.2  # 柱状图间距（组间距离）
if 'box_width' not in st.session_state:
    st.session_state.box_width = 0.6  # 箱线图宽度
if 'box_spacing' not in st.session_state:
    st.session_state.box_spacing = 0.3  # 箱线图间距
if 'violin_width' not in st.session_state:
    st.session_state.violin_width = 0.8  # 小提琴图宽度
if 'violin_spacing' not in st.session_state:
    st.session_state.violin_spacing = 0.2  # 小提琴图间距
if 'dot_width' not in st.session_state:
    st.session_state.dot_width = 0.5  # 点图标记大小（相对值）
if 'dot_spacing' not in st.session_state:
    st.session_state.dot_spacing = 0.2  # 点图间距

# ==================== 辅助函数 ====================
def validate_data_and_suggest(task, df, value_col=None, group_col=None, col_x=None, col_y=None, x_col=None, y_col=None):
    """
    验证数据是否适合当前统计方法，如果不适合则给出建议
    返回: (is_valid, suggestion_message)
    """
    if task == "两组比较（t 检验 / Mann–Whitney）":
        if not value_col or not group_col:
            return True, None
        
        groups = df[group_col].unique()
        n_groups = len(groups)
        
        if n_groups != 2:
            suggestion = f"""
数据不适合当前分析方法

当前数据有 {n_groups} 个组，而"两组比较"方法需要恰好 2 个组。

建议：
• 如果您的数据有 3 个或更多组，请选择"多组比较（单因素 ANOVA）"方法
• 如果您的数据只有 1 个组，请考虑：
  - 添加对照组数据
  - 使用单样本t检验（如果与理论值比较）
  - 检查分组变量是否正确选择

当前分组：{', '.join(map(str, groups))}
            """
            return True, suggestion  # 改为True，表示这是建议而不是错误
        else:
            # 检查样本量
            group1 = df[df[group_col] == groups[0]][value_col].dropna()
            group2 = df[df[group_col] == groups[1]][value_col].dropna()
            if len(group1) < 3 or len(group2) < 3:
                suggestion = f"""
数据样本量不足

当前数据中，{groups[0]}组有 {len(group1)} 个观测值，{groups[1]}组有 {len(group2)} 个观测值。

建议：
• 每组至少需要 3 个观测值才能进行统计分析
• 请检查数据是否完整上传
• 考虑增加样本量或合并相关组别
                """
                return False, suggestion
    
    elif task == "多组比较（单因素 ANOVA）":
        if not value_col or not group_col:
            return True, None
        
        groups = df[group_col].unique()
        n_groups = len(groups)
        
        if n_groups < 2:
            suggestion = f"""
数据不适合当前分析方法

当前数据只有 {n_groups} 个组，而"多组比较"方法需要至少 2 个组。

建议：
• 如果只有 1 个组，请选择"两组比较"方法（需要添加对照组）
• 检查分组变量是否正确选择
• 考虑添加更多组别或对照组数据

当前分组：{', '.join(map(str, groups))}
            """
            return False, suggestion
        elif n_groups == 2:
            suggestion = f"""
数据更适合使用两组比较方法

当前数据有 2 个组，虽然可以使用多组比较（ANOVA），但更推荐使用"两组比较（t 检验 / Mann–Whitney）"方法。

建议：
• 切换到"两组比较"方法，可以获得更精确的统计结果
• 两组比较方法会自动选择t检验或Mann-Whitney U检验
• 如果确实需要多组比较，可以继续使用当前方法

当前分组：{', '.join(map(str, groups))}
            """
            return True, suggestion  # 仍然可以分析，但给出建议
    
    elif task == "相关性分析（Pearson / Spearman）":
        if not col_x or not col_y:
            return True, None
        
        # 检查变量是否存在
        if col_x not in df.columns or col_y not in df.columns:
            suggestion = f"""
数据列不存在

请检查选择的变量是否正确。

建议：
• 确认变量 X 和变量 Y 都已正确选择
• 检查数据文件是否包含这些列
            """
            return False, suggestion
        
        # 检查有效数据量
        valid_data = df[[col_x, col_y]].dropna()
        if len(valid_data) < 3:
            suggestion = f"""
数据样本量不足

当前数据中，变量 {col_x} 和 {col_y} 的有效配对数据只有 {len(valid_data)} 个。

建议：
• 相关性分析至少需要 3 对有效数据
• 请检查数据是否完整，是否有缺失值
• 考虑增加样本量或检查数据质量
            """
            return False, suggestion
        
        # 检查变量是否为数值型
        if not pd.api.types.is_numeric_dtype(df[col_x]) or not pd.api.types.is_numeric_dtype(df[col_y]):
            suggestion = f"""
数据类型不适合

相关性分析需要两个数值型变量。

建议：
• 检查变量 {col_x} 和 {col_y} 是否为数值型
• 如果变量是分类变量，可以考虑：
  - 使用"两组比较"或"多组比较"方法（如果有分组变量）
  - 将分类变量转换为数值型（如果合理）
            """
            return False, suggestion
    
    elif task == "简单线性回归":
        if not x_col or not y_col:
            return True, None
        
        # 检查变量是否存在
        if x_col not in df.columns or y_col not in df.columns:
            suggestion = f"""
数据列不存在

请检查选择的自变量和因变量是否正确。

建议：
• 确认自变量 X 和因变量 Y 都已正确选择
• 检查数据文件是否包含这些列
            """
            return False, suggestion
        
        # 检查有效数据量
        valid_data = df[[x_col, y_col]].dropna()
        if len(valid_data) < 3:
            suggestion = f"""
数据样本量不足

当前数据中，自变量 {x_col} 和因变量 {y_col} 的有效配对数据只有 {len(valid_data)} 个。

建议：
• 线性回归至少需要 3 对有效数据
• 请检查数据是否完整，是否有缺失值
• 考虑增加样本量或检查数据质量
            """
            return False, suggestion
        
        # 检查变量是否为数值型
        if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
            suggestion = f"""
数据类型不适合

线性回归需要数值型的自变量和因变量。

建议：
• 检查变量 {x_col} 和 {y_col} 是否为数值型
• 如果变量是分类变量，可以考虑：
  - 使用"两组比较"或"多组比较"方法（如果有分组变量）
  - 将分类变量转换为数值型（如果合理）
            """
            return False, suggestion
        
        # 检查自变量是否有变异（不能是常数）
        if df[x_col].nunique() < 2:
            suggestion = f"""
自变量缺乏变异

自变量 {x_col} 的所有值都相同（只有一个唯一值），无法进行线性回归。

建议：
• 检查自变量是否正确选择
• 如果自变量确实是常数，考虑使用其他分析方法
• 确认数据是否正确上传
            """
            return False, suggestion
    
    return True, None

def suggest_alternative_method(error_msg, task, df, value_col=None, group_col=None, col_x=None, col_y=None, x_col=None, y_col=None):
    """
    根据错误信息智能推荐正确的统计方法
    返回: (recommended_method, suggestion_message, is_suggestion)
    is_suggestion: True表示这是建议（应使用st.info），False表示这是错误（应使用st.error）
    """
    error_lower = error_msg.lower()
    
    # 检查组数问题
    if "组" in error_msg or "group" in error_lower:
        if group_col and group_col in df.columns:
            try:
                groups = df[group_col].unique()
                n_groups = len(groups)
                
                if task == "两组比较（t 检验 / Mann–Whitney）":
                    if n_groups > 2:
                        return "多组比较（单因素 ANOVA）", f"""
数据不适合当前分析方法

当前数据有 {n_groups} 个组，而"两组比较"方法需要恰好 2 个组。

推荐方法：多组比较（单因素 ANOVA）

操作步骤：
1. 在左侧边栏的"分析设置"中，将"统计任务"改为"多组比较（单因素 ANOVA）"
2. 重新执行分析

当前分组：{', '.join(map(str, groups))}
                        """, True  # 这是建议，不是错误
                    elif n_groups == 1:
                        return "两组比较（t 检验 / Mann–Whitney）", f"""
数据不适合当前分析方法

当前数据只有 1 个组，无法进行比较分析。

建议：
• 添加对照组数据后再进行分析
• 如果与理论值比较，考虑使用单样本t检验
• 检查分组变量是否正确选择

当前分组：{', '.join(map(str, groups))}
                        """, True  # 这是建议，不是错误
                
                elif task == "多组比较（单因素 ANOVA）":
                    if n_groups == 2:
                        return "两组比较（t 检验 / Mann–Whitney）", f"""
数据更适合使用两组比较方法

当前数据有 2 个组，虽然可以使用多组比较（ANOVA），但更推荐使用"两组比较"方法。

推荐方法：两组比较（t 检验 / Mann–Whitney）

操作步骤：
1. 在左侧边栏的"分析设置"中，将"统计任务"改为"两组比较（t 检验 / Mann–Whitney）"
2. 重新执行分析

当前分组：{', '.join(map(str, groups))}
                        """, True  # 这是建议，不是错误
                    elif n_groups == 1:
                        return "两组比较（t 检验 / Mann–Whitney）", f"""
数据不适合当前分析方法

当前数据只有 1 个组，无法进行比较分析。

建议：
• 添加对照组数据后再进行分析
• 检查分组变量是否正确选择

当前分组：{', '.join(map(str, groups))}
                        """, True  # 这是建议，不是错误
            except:
                pass
    
    # 检查变量类型问题
    if "数值" in error_msg or "numeric" in error_lower or "类型" in error_msg:
        if task == "相关性分析（Pearson / Spearman）":
            return "相关性分析（Pearson / Spearman）", f"""
数据变量类型不匹配

错误信息：{error_msg}

建议：
• 确保选择的变量 X 和变量 Y 都是数值型变量
• 检查数据文件中的变量类型
• 如果变量是分类变量，考虑使用其他分析方法
            """, True  # 这是建议
        elif task == "线性回归（简单）":
            return "线性回归（简单）", f"""
数据变量类型不匹配

错误信息：{error_msg}

建议：
• 确保自变量 X 和因变量 Y 都是数值型变量
• 检查数据文件中的变量类型
• 如果变量是分类变量，考虑使用其他分析方法
            """, True  # 这是建议
    
    # 检查样本量问题
    if "样本" in error_msg or "sample" in error_lower or "观测" in error_msg:
        if task in ["两组比较（t 检验 / Mann–Whitney）", "多组比较（单因素 ANOVA）"]:
            return task, f"""
数据样本量不足

错误信息：{error_msg}

建议：
• 每组至少需要 3 个观测值才能进行统计分析
• 请检查数据是否完整上传
• 考虑增加样本量或合并相关组别
            """, False  # 这是错误，需要更多数据
    
    # 检查变量选择问题
    if "none" in error_lower or "are in the" in error_lower or "not in" in error_lower:
        return task, f"""
变量选择错误

错误信息：{error_msg}

建议：
• 检查左侧边栏的"变量选择"是否已正确选择变量
• 确认数据文件包含所需的列
• 重新选择变量并执行分析
        """, False  # 这是错误，变量未选择
    
    # 默认建议
    return None, f"""
数据分析遇到问题

错误信息：{error_msg}

建议：
• 检查数据是否符合当前统计方法的要求
• 确认变量选择是否正确
• 检查数据质量（是否有异常值、缺失值过多等）
• 查看左侧边栏的"方法说明"了解数据要求
• 如果问题持续，请尝试其他统计方法
    """, False  # 默认是错误

def apply_axis_settings(ax, x_scale=None, y_scale=None, x_min=None, x_max=None, y_min=None, y_max=None):
    """应用坐标轴设置（刻度类型和范围）"""
    # X轴设置
    if x_scale == "对数":
        ax.set_xscale('log')
    elif x_scale == "科学计数法":
        ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    if x_min is not None and x_max is not None:
        ax.set_xlim(x_min, x_max)
    
    # Y轴设置
    if y_scale == "对数":
        ax.set_yscale('log')
    elif y_scale == "科学计数法":
        ax.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)

def add_pvalue_text(ax, p_val, x_pos, y_max, fontsize, show_pvalue=True, groups=None, group_names=None):
    """在图形上添加P值标注（符合发表要求的位置和样式）
    注意：fontsize 应该是已经根据图形尺寸调整后的字体大小
    groups: 分组名称列表（用于显示两组数据的区别）
    group_names: 分组变量名称（用于显示）
    """
    if not show_pvalue:
        return
    
    # 格式化P值（符合发表要求：使用星号标记显著性）
    if p_val < 0.001:
        p_text = "***"
        p_full = f"p < 0.001"
    elif p_val < 0.01:
        p_text = "**"
        p_full = f"p < 0.01"
    elif p_val < 0.05:
        p_text = "*"
        p_full = f"p = {p_val:.3f}"
    else:
        p_text = f"p={p_val:.3f}" if p_val >= 0.01 else f"p={p_val:.2e}"
        p_full = f"p = {p_val:.3f}" if p_val >= 0.01 else f"p = {p_val:.2e}"
    
    # 如果有两组数据，显示两组数据的区别
    if groups is not None and len(groups) == 2:
        group1_name = str(groups[0])
        group2_name = str(groups[1])
        if p_val < 0.05:
            significance = "有显著差异" if p_val < 0.05 else "无显著差异"
            display_text = f"{group1_name} vs {group2_name}\n{p_full} ({significance})"
        else:
            display_text = f"{group1_name} vs {group2_name}\n{p_full} (无显著差异)"
    else:
        display_text = p_full
    
    # 在图形右上角添加P值（避免与标题重叠）
    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()
    x_pos_text = x_lim[1] * 0.98  # 右上角
    y_pos_text = y_lim[1] * 0.98  # 右上角
    
    # 使用较小的字体显示详细信息，确保使用支持中文的字体
    # 如果包含中文，使用英文显示以避免字体问题
    if groups is not None and len(groups) == 2:
        # 对于两组比较，使用英文显示以避免字体问题
        group1_name = str(groups[0])
        group2_name = str(groups[1])
        if p_val < 0.05:
            display_text_en = f"{group1_name} vs {group2_name}\n{p_full} (p<0.05)"
        else:
            display_text_en = f"{group1_name} vs {group2_name}\n{p_full} (ns)"
    else:
        display_text_en = p_full
    
    ax.text(x_pos_text, y_pos_text, display_text_en, 
           fontsize=fontsize*0.85, ha='right', va='top',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='black', alpha=0.9, linewidth=0.5),
           family='sans-serif')  # 明确指定字体族

# ==================== 图形美化主题设置函数 ====================
def apply_plot_style(fig, ax, fontsize, linewidth, pointsize, show_legend, theme, color_scheme):
    """应用图形美化参数"""
    # 根据颜色方案选择基础颜色
    if color_scheme == "蓝色系":
        base_colors = ['#4472C4', '#5B9BD5', '#70AD47', '#FFC000', '#7030A0', '#A5A5A5']
    elif color_scheme == "绿色系":
        base_colors = ['#70AD47', '#92D050', '#4472C4', '#FFC000', '#7030A0', '#A5A5A5']
    elif color_scheme == "橙色系":
        base_colors = ['#ED7D31', '#FFC000', '#4472C4', '#70AD47', '#7030A0', '#A5A5A5']
    elif color_scheme == "紫色系":
        base_colors = ['#7030A0', '#9C88FF', '#4472C4', '#ED7D31', '#70AD47', '#A5A5A5']
    elif color_scheme == "黑白灰系":
        # 黑白灰配色，适合黑白打印
        base_colors = ['#000000', '#404040', '#808080', '#C0C0C0', '#E0E0E0', '#FFFFFF']
    else:  # 经典配色
        base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # 根据主题和颜色方案组合调整颜色
    # 主题只影响整体风格，颜色方案决定具体颜色
    if "基础" in theme or "Basic" in theme:
        # 基础风格：直接使用颜色方案
        colors = base_colors
    elif "自然" in theme or "Nature" in theme:
        # 自然风格：根据颜色方案调整，但保持自然风格的特点
        if color_scheme == "蓝色系":
            colors = ['#4472C4', '#5B9BD5', '#70AD47', '#FFC000', '#7030A0', '#A5A5A5']
        elif color_scheme == "绿色系":
            colors = ['#70AD47', '#92D050', '#4472C4', '#FFC000', '#7030A0', '#A5A5A5']
        elif color_scheme == "橙色系":
            colors = ['#ED7D31', '#FFC000', '#4472C4', '#70AD47', '#7030A0', '#A5A5A5']
        elif color_scheme == "紫色系":
            colors = ['#7030A0', '#9C88FF', '#4472C4', '#ED7D31', '#70AD47', '#A5A5A5']
        elif color_scheme == "黑白灰系":
            colors = ['#000000', '#404040', '#808080', '#C0C0C0', '#E0E0E0', '#FFFFFF']
        else:  # 经典配色
            colors = ['#4472C4', '#ED7D31', '#70AD47', '#FFC000', '#7030A0', '#A5A5A5']
    else:  # 演示风格
        # 演示风格：根据颜色方案调整，但更鲜艳
        if color_scheme == "蓝色系":
            colors = ['#0066CC', '#3399FF', '#70AD47', '#FFC000', '#7030A0', '#666666']
        elif color_scheme == "绿色系":
            colors = ['#009900', '#33CC33', '#0066CC', '#FFC000', '#7030A0', '#666666']
        elif color_scheme == "橙色系":
            colors = ['#FF6600', '#FF9900', '#0066CC', '#009900', '#7030A0', '#666666']
        elif color_scheme == "紫色系":
            colors = ['#6600CC', '#9933FF', '#0066CC', '#FF6600', '#009900', '#666666']
        elif color_scheme == "黑白灰系":
            colors = ['#000000', '#404040', '#808080', '#C0C0C0', '#E0E0E0', '#FFFFFF']
        else:  # 经典配色
            colors = ['#0066CC', '#FF6600', '#009900', '#CC0000', '#6600CC', '#666666']
    
    # 应用颜色到当前调色板
    sns.set_palette(colors)
    
    # 设置字体大小
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + 
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(fontsize)
    
    # 设置轴线宽度
    for spine in ax.spines.values():
        spine.set_linewidth(linewidth)
    
    # 设置刻度线宽度
    ax.tick_params(width=linewidth, length=fontsize*0.8)
    
    # 设置图例
    if show_legend and ax.get_legend() is not None:
        legend = ax.get_legend()
        legend.set_fontsize(fontsize - 1)
        legend.get_frame().set_linewidth(linewidth)
    elif not show_legend:
        ax.legend().set_visible(False)
    
    # 设置网格（细线，低透明度）
    ax.grid(True, alpha=0.2, linewidth=linewidth*0.5)
    
    # 返回颜色列表供绘图使用
    return colors

def generate_python_code(task, df, params):
    """生成当前分析的Python代码"""
    python_code = "# 统计分析 Python 代码\n"
    python_code += "# 生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
    python_code += "# 导入库\n"
    python_code += "import pandas as pd\n"
    python_code += "import numpy as np\n"
    python_code += "from scipy import stats\n"
    python_code += "import matplotlib.pyplot as plt\n"
    python_code += "import seaborn as sns\n\n"
    python_code += "# 读取数据\n"
    python_code += f"df = pd.read_csv('your_data.csv')  # 请替换为您的数据文件路径\n\n"
    
    if task == "两组比较（t 检验 / Mann–Whitney）":
        value_col = params.get('value_col', 'value')
        group_col = params.get('group_col', 'group')
        alpha = params.get('alpha', 0.05)
        
        python_code += f"# 两组比较分析\n"
        python_code += f"value_col = '{value_col}'\n"
        python_code += f"group_col = '{group_col}'\n"
        python_code += f"alpha = {alpha}\n\n"
        python_code += f"group1 = df[df[group_col] == df[group_col].unique()[0]][value_col].dropna()\n"
        python_code += f"group2 = df[df[group_col] == df[group_col].unique()[1]][value_col].dropna()\n\n"
        python_code += f"# 正态性检验\n"
        python_code += f"from scipy.stats import shapiro, levene\n"
        python_code += f"_, p_norm1 = shapiro(group1)\n"
        python_code += f"_, p_norm2 = shapiro(group2)\n"
        python_code += f"_, p_var = levene(group1, group2)\n\n"
        python_code += f"# 选择检验方法\n"
        python_code += f"if p_norm1 > 0.05 and p_norm2 > 0.05 and p_var > 0.05:\n"
        python_code += f"    stat, p_value = stats.ttest_ind(group1, group2, equal_var=True)\n"
        python_code += f"    method = '独立样本 t 检验'\n"
        python_code += f"else:\n"
        python_code += f"    stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')\n"
        python_code += f"    method = 'Mann-Whitney U 检验'\n\n"
        python_code += f"print(f'方法: {{method}}')\n"
        python_code += f"print(f'统计量: {{stat:.4f}}, p 值: {{p_value:.4f}}')\n\n"
        python_code += f"# 绘图\n"
        python_code += f"fig, ax = plt.subplots(figsize=(8, 5))\n"
        python_code += f"sns.boxplot(data=df, x=group_col, y=value_col, ax=ax)\n"
        python_code += f"plt.title(f'两组比较: {{method}}')\n"
        python_code += f"plt.tight_layout()\n"
        python_code += f"plt.show()\n"
        
    elif task == "多组比较（单因素 ANOVA）":
        value_col = params.get('value_col', 'value')
        group_col = params.get('group_col', 'group')
        alpha = params.get('alpha', 0.05)
        
        python_code += f"# 单因素方差分析\n"
        python_code += f"value_col = '{value_col}'\n"
        python_code += f"group_col = '{group_col}'\n"
        python_code += f"alpha = {alpha}\n\n"
        python_code += f"groups = df[group_col].unique()\n"
        python_code += f"group_data = [df[df[group_col] == g][value_col].dropna() for g in groups]\n\n"
        python_code += f"f_stat, p_value = stats.f_oneway(*group_data)\n\n"
        python_code += f"print(f'F 统计量: {{f_stat:.4f}}, p 值: {{p_value:.4f}}')\n\n"
        python_code += f"# 事后检验（Tukey HSD）\n"
        python_code += f"from scipy.stats import tukey_hsd\n"
        python_code += f"if p_value < alpha:\n"
        python_code += f"    tukey_result = tukey_hsd(*group_data)\n"
        python_code += f"    print('Tukey HSD 事后检验结果:')\n"
        python_code += f"    print(tukey_result)\n\n"
        python_code += f"# 绘图\n"
        python_code += f"fig, ax = plt.subplots(figsize=(8, 5))\n"
        python_code += f"sns.boxplot(data=df, x=group_col, y=value_col, ax=ax)\n"
        python_code += f"plt.title('多组比较: 单因素 ANOVA')\n"
        python_code += f"plt.tight_layout()\n"
        python_code += f"plt.show()\n"
        
    elif task == "相关性分析（Pearson / Spearman）":
        col_x = params.get('col_x', 'x')
        col_y = params.get('col_y', 'y')
        method = params.get('method', 'auto')
        
        python_code += f"# 相关性分析\n"
        python_code += f"col_x = '{col_x}'\n"
        python_code += f"col_y = '{col_y}'\n"
        python_code += f"x = df[col_x].dropna()\n"
        python_code += f"y = df[col_y].dropna()\n\n"
        if method == 'auto' or method == 'pearson':
            python_code += f"stat, p_value = stats.pearsonr(x, y)\n"
            python_code += f"method_name = 'Pearson 相关系数'\n"
        else:
            python_code += f"stat, p_value = stats.spearmanr(x, y)\n"
            python_code += f"method_name = 'Spearman 等级相关系数'\n"
        python_code += f"print(f'方法: {{method_name}}')\n"
        python_code += f"print(f'相关系数: {{stat:.4f}}, p 值: {{p_value:.4f}}')\n\n"
        python_code += f"# 绘图\n"
        python_code += f"fig, ax = plt.subplots(figsize=(8, 5))\n"
        python_code += f"ax.scatter(x, y, alpha=0.6)\n"
        python_code += f"z = np.polyfit(x, y, 1)\n"
        python_code += f"p = np.poly1d(z)\n"
        python_code += f"ax.plot(x, p(x), 'r--', alpha=0.8, label='趋势线')\n"
        python_code += f"ax.set_xlabel(col_x)\n"
        python_code += f"ax.set_ylabel(col_y)\n"
        python_code += f"ax.set_title(f'相关性分析: {{method_name}}')\n"
        python_code += f"ax.legend()\n"
        python_code += f"plt.tight_layout()\n"
        python_code += f"plt.show()\n"
        
    elif task == "简单线性回归":
        x_col = params.get('x_col', 'x')
        y_col = params.get('y_col', 'y')
        alpha = params.get('alpha', 0.05)
        
        python_code += f"# 简单线性回归\n"
        python_code += f"x_col = '{x_col}'\n"
        python_code += f"y_col = '{y_col}'\n"
        python_code += f"alpha = {alpha}\n\n"
        python_code += f"x = df[x_col].dropna()\n"
        python_code += f"y = df[y_col].dropna()\n\n"
        python_code += f"from scipy import stats\n"
        python_code += f"slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)\n\n"
        python_code += f"print(f'回归方程: y = {{intercept:.4f}} + {{slope:.4f}} * x')\n"
        python_code += f"print(f'R² = {{r_value**2:.4f}}, p 值: {{p_value:.4f}}')\n\n"
        python_code += f"# 绘图\n"
        python_code += f"fig, ax = plt.subplots(figsize=(8, 5))\n"
        python_code += f"ax.scatter(x, y, alpha=0.6, label='数据点')\n"
        python_code += f"ax.plot(x, intercept + slope * x, 'r--', label='回归线')\n"
        python_code += f"ax.set_xlabel(x_col)\n"
        python_code += f"ax.set_ylabel(y_col)\n"
        python_code += f"ax.set_title('简单线性回归')\n"
        python_code += f"ax.legend()\n"
        python_code += f"plt.tight_layout()\n"
        python_code += f"plt.show()\n"
    
    return python_code

def generate_pdf_report(task, df, params, result, summary_text, fig=None):
    """生成PDF统计报告"""
    if not REPORTLAB_AVAILABLE:
        return None, "PDF生成功能需要安装reportlab库。请运行: pip install reportlab"
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    story = []
    styles = getSampleStyleSheet()
    
    # 创建支持中文的样式
    chinese_font = CHINESE_FONT_NAME if CHINESE_FONT_NAME else 'Helvetica'
    
    # 标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=16,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=1  # 居中
    )
    
    # 中文样式
    chinese_normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=10
    )
    
    chinese_heading2_style = ParagraphStyle(
        'ChineseHeading2',
        parent=styles['Heading2'],
        fontName=chinese_font,
        fontSize=12
    )
    
    chinese_heading3_style = ParagraphStyle(
        'ChineseHeading3',
        parent=styles['Heading3'],
        fontName=chinese_font,
        fontSize=11
    )
    
    # 报告信息样式
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=10,
        textColor=colors.HexColor('#6b7280')
    )
    
    # 添加标题
    story.append(Paragraph("统计分析报告", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 报告信息
    story.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    story.append(Paragraph(f"分析模块：stat-IDE 经典统计模块（V1）", info_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 数据描述
    story.append(Paragraph("<b>一、数据描述</b>", chinese_heading2_style))
    story.append(Spacer(1, 0.1*inch))
    
    if task in ["两组比较（t 检验 / Mann–Whitney）", "多组比较（单因素 ANOVA）"]:
        value_col = params.get('value_col', '')
        group_col = params.get('group_col', '')
        story.append(Paragraph(f"• 因变量：{value_col}", chinese_normal_style))
        story.append(Paragraph(f"• 分组变量：{group_col}", chinese_normal_style))
        story.append(Paragraph(f"• 数据规模：{df.shape[0]} 行 × {df.shape[1]} 列", chinese_normal_style))
    elif task == "相关性分析（Pearson / Spearman）":
        col_x = params.get('col_x', '')
        col_y = params.get('col_y', '')
        story.append(Paragraph(f"• 变量X：{col_x}", chinese_normal_style))
        story.append(Paragraph(f"• 变量Y：{col_y}", chinese_normal_style))
        story.append(Paragraph(f"• 数据规模：{df.shape[0]} 行 × {df.shape[1]} 列", chinese_normal_style))
    elif task == "简单线性回归":
        x_col = params.get('x_col', '')
        y_col = params.get('y_col', '')
        story.append(Paragraph(f"• 自变量X：{x_col}", chinese_normal_style))
        story.append(Paragraph(f"• 因变量Y：{y_col}", chinese_normal_style))
        story.append(Paragraph(f"• 数据规模：{df.shape[0]} 行 × {df.shape[1]} 列", chinese_normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # 统计方法
    story.append(Paragraph("<b>二、统计方法</b>", chinese_heading2_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"• 分析方法：{result.get('method_name', '未知方法')}", chinese_normal_style))
    story.append(Paragraph(f"• 显著性水平：α = {params.get('alpha', 0.05)}", chinese_normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 统计结果
    story.append(Paragraph("<b>三、统计结果</b>", chinese_heading2_style))
    story.append(Spacer(1, 0.1*inch))
    
    p_val = result.get('p_value', 0)
    p_display = f"{p_val:.4e}" if p_val < 0.001 else f"{p_val:.4f}"
    alpha_val = params.get('alpha', 0.05)
    
    result_data = [
        ['项目', '数值'],
        ['检验统计量', f"{result.get('stat', 0):.4f}"],
        ['p值', p_display],
        ['显著性水平', f"α = {alpha_val}"],
        ['结论', '有统计学意义' if p_val < alpha_val else '无统计学意义']
    ]
    
    result_table = Table(result_data, colWidths=[2*inch, 3*inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), chinese_font if chinese_font != 'Helvetica' else 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 0.2*inch))
    
    # 结果摘要
    story.append(Paragraph("<b>四、结果摘要</b>", chinese_heading2_style))
    story.append(Spacer(1, 0.1*inch))
    
    # 将摘要文本分段添加
    summary_lines = summary_text.split('\n')
    for line in summary_lines:
        if line.strip():
            if line.startswith('【'):
                story.append(Paragraph(f"<b>{line}</b>", chinese_heading3_style))
            else:
                story.append(Paragraph(line, chinese_normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # 如果有图形，添加图形
    if fig is not None:
        story.append(Paragraph("<b>五、统计图形</b>", chinese_heading2_style))
        story.append(Spacer(1, 0.1*inch))
        try:
            # 保存图形到BytesIO
            img_buffer = BytesIO()
            fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img = Image(img_buffer, width=5*inch, height=3.75*inch)
            story.append(img)
        except:
            story.append(Paragraph("（图形生成失败）", chinese_normal_style))
    
    # 页脚
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("---", info_style))
    story.append(Paragraph("本报告由 stat-IDE 经典统计模块（V1）自动生成", info_style))
    story.append(Paragraph("🎓 Shawn · InSynBio", info_style))
    
    # 生成PDF
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), None
    except Exception as e:
        return None, f"PDF生成失败：{str(e)}"

# ==================== 顶部顶栏 ====================
top_bar = st.container()
with top_bar:
    col_title, col_tabs, col_actions, col_info = st.columns([2.5, 4, 2.5, 1])
    
    with col_title:
        # 标题样式与侧边栏模块选择一致
        st.markdown("### 📊 stat-IDE 经典统计模块（V1）")
    
    with col_tabs:
        # 使用 tabs 显示模块，但只有第一个可用
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 经典统计",
            "🧬 组学分析",
            "💊 PK/PD & 毒理",
            "⏱️ 生存分析",
            "📚 Meta分析"
        ])
        
        # 只有经典统计（tab1）可用
        if tab2 or tab3 or tab4 or tab5:
            st.info("⚠️ 该模块正在开发中，敬请期待！")
    
    with col_actions:
        # 功能按钮区域 - 始终显示按钮
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            # 生成PDF报告
            if st.session_state.current_df is not None and st.session_state.current_task and st.session_state.current_results:
                result = st.session_state.current_results
                task = st.session_state.current_task
                params = st.session_state.current_params
                df = st.session_state.current_df
                
                # 获取结果摘要文本
                summary_text = ""
                try:
                        # 这里需要获取summary_text，但由于它在后面的代码中生成，我们需要重新生成
                        p_val = result.get('p_value', 0)
                        p_display = f"{p_val:.4e}" if p_val < 0.001 else f"{p_val:.4f}"
                        alpha_val = params.get('alpha', 0.05)
                        
                        if task == "两组比较（t 检验 / Mann–Whitney）":
                            value_col = params.get('value_col')
                            group_col = params.get('group_col')
                            if value_col and group_col:
                                groups = df[group_col].unique()
                                group1_data = df[df[group_col] == groups[0]][value_col].dropna()
                                group2_data = df[df[group_col] == groups[1]][value_col].dropna()
                                n1 = len(group1_data)
                                n2 = len(group2_data)
                                mean1 = group1_data.mean()
                                mean2 = group2_data.mean()
                                std1 = group1_data.std()
                                std2 = group2_data.std()
                                method_reason = ""
                                if "t 检验" in result['method_name']:
                                    method_reason = "数据满足正态分布和方差齐性假设，因此选择独立样本t检验。"
                                elif "Mann-Whitney" in result['method_name'] or "Mann–Whitney" in result['method_name']:
                                    method_reason = "数据不满足正态分布或方差齐性假设，因此选择非参数Mann-Whitney U检验。"
                                summary_text = f"""【数据描述】
本研究分析了{value_col}变量在{groups[0]}组和{groups[1]}组之间的差异。
- 因变量：{value_col}（数值型变量）
- 分组变量：{group_col}（{groups[0]}组 vs {groups[1]}组）
- 样本量：{groups[0]}组 n={n1}，{groups[1]}组 n={n2}，总计 n={n1+n2}
- 描述性统计：{groups[0]}组 均值={mean1:.2f}±{std1:.2f}，{groups[1]}组 均值={mean2:.2f}±{std2:.2f}

【方法选择】
使用{result['method_name']}进行两组比较。{method_reason}
该方法适用于比较两个独立组别的均值差异，能够有效控制第一类错误率。

【统计结果】
检验统计量 = {result['stat']:.4f}，p值 = {p_display}（显著性水平 α = {alpha_val}）。
在 α = {alpha_val} 水平下，两组间差异{'具有' if p_val < alpha_val else '不具有'}统计学意义（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结论】
{groups[0]}组与{groups[1]}组在{value_col}变量上{'存在' if p_val < alpha_val else '不存在'}显著差异。
{'均值差异为' + f'{abs(mean1-mean2):.2f}' if p_val < alpha_val else '两组均值差异无统计学意义'}。"""
                        elif task == "多组比较（单因素 ANOVA）":
                            value_col = params.get('value_col')
                            group_col = params.get('group_col')
                            if value_col and group_col:
                                groups = sorted(df[group_col].unique())
                                group_data_list = [df[df[group_col] == g][value_col].dropna() for g in groups]
                                group_ns = [len(data) for data in group_data_list]
                                group_means = [data.mean() for data in group_data_list]
                                group_stds = [data.std() for data in group_data_list]
                                groups_str = "、".join([f"{g}（n={n}）" for g, n in zip(groups, group_ns)])
                                means_str = "、".join([f"{g}={mean:.2f}±{std:.2f}" for g, mean, std in zip(groups, group_means, group_stds)])
                                summary_text = f"""【数据描述】
本研究分析了{value_col}变量在多个组别之间的差异。
- 因变量：{value_col}（数值型变量）
- 分组变量：{group_col}（共{len(groups)}个组：{groups_str}）
- 总样本量：n={sum(group_ns)}
- 描述性统计：{means_str}

【方法选择】
使用{result['method_name']}进行多组比较。
单因素方差分析适用于比较三个或更多组间的均值差异，能够同时检验所有组间是否存在显著差异，避免多次两两比较带来的多重比较问题。

【统计结果】
F统计量 = {result['stat']:.4f}，p值 = {p_display}（显著性水平 α = {alpha_val}）。
在 α = {alpha_val} 水平下，各组间差异{'具有' if p_val < alpha_val else '不具有'}统计学意义（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结论】
各组在{value_col}变量上{'存在' if p_val < alpha_val else '不存在'}显著差异。
{'建议进行事后检验以确定具体哪些组间存在差异。' if p_val < alpha_val else '各组均值差异无统计学意义。'}"""
                        elif task == "相关性分析（Pearson / Spearman）":
                            col_x = params.get('col_x')
                            col_y = params.get('col_y')
                            if col_x and col_y:
                                valid_data = df[[col_x, col_y]].dropna()
                                n = len(valid_data)
                                x_mean = valid_data[col_x].mean()
                                y_mean = valid_data[col_y].mean()
                                x_std = valid_data[col_x].std()
                                y_std = valid_data[col_y].std()
                                corr_coef = result['stat']
                                method_reason = ""
                                if "Pearson" in result['method_name']:
                                    method_reason = "数据满足正态分布假设，因此选择Pearson相关系数分析线性相关关系。"
                                elif "Spearman" in result['method_name']:
                                    method_reason = "数据不满足正态分布假设，因此选择Spearman等级相关系数分析单调相关关系。"
                                abs_corr = abs(corr_coef)
                                if abs_corr >= 0.7:
                                    strength = "强相关"
                                elif abs_corr >= 0.4:
                                    strength = "中等相关"
                                elif abs_corr >= 0.2:
                                    strength = "弱相关"
                                else:
                                    strength = "几乎无相关"
                                direction = "正相关" if corr_coef > 0 else "负相关"
                                summary_text = f"""【数据描述】
本研究分析了{col_x}与{col_y}两个变量之间的相关关系。
- 变量X：{col_x}（均值={x_mean:.2f}±{x_std:.2f}）
- 变量Y：{col_y}（均值={y_mean:.2f}±{y_std:.2f}）
- 有效样本量：n={n}（去除缺失值后）
- 数据特征：两个连续型数值变量

【方法选择】
使用{result['method_name']}进行相关性分析。{method_reason}
该方法能够量化两个变量之间的相关程度和方向。

【统计结果】
相关系数 r = {corr_coef:.4f}，p值 = {p_display}（显著性水平 α = {alpha_val}）。
在 α = {alpha_val} 水平下，两变量间{'存在' if p_val < alpha_val else '不存在'}统计学意义的相关关系（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结果解释】
相关系数 r = {corr_coef:.4f} 表示{col_x}与{col_y}之间存在{strength}的{direction}关系。
{'根据Cohen（1988）的标准：' + strength + '（|r| ' + ('≥0.7' if abs_corr >= 0.7 else '≥0.4' if abs_corr >= 0.4 else '≥0.2' if abs_corr >= 0.2 else '<0.2') + '）。' if p_val < alpha_val else ''}

【结论】
{col_x}与{col_y}之间{'存在' if p_val < alpha_val else '不存在'}统计学意义的相关关系。
{'两变量间存在' + strength + '的' + direction + '关系，' + ('随着' if corr_coef > 0 else '随着') + col_x + '的增加，' + col_y + ('也增加' if corr_coef > 0 else '减少') + '。' if p_val < alpha_val else '两变量间无显著相关关系。'}"""
                        elif task == "简单线性回归":
                            x_col = params.get('x_col')
                            y_col = params.get('y_col')
                            if x_col and y_col:
                                valid_data = df[[x_col, y_col]].dropna()
                                n = len(valid_data)
                                x_mean = valid_data[x_col].mean()
                                y_mean = valid_data[y_col].mean()
                                slope = result['extra_info'].get('slope', 0)
                                intercept = result['extra_info'].get('intercept', 0)
                                r_squared = result['extra_info'].get('r_squared', 0)
                                summary_text = f"""【数据描述】
本研究分析了{x_col}对{y_col}的预测作用，建立简单线性回归模型。
- 自变量X：{x_col}（均值={x_mean:.2f}）
- 因变量Y：{y_col}（均值={y_mean:.2f}）
- 有效样本量：n={n}（去除缺失值后）
- 模型类型：简单线性回归（Y = a + bX）

【方法选择】
使用简单线性回归分析{x_col}对{y_col}的影响。
线性回归能够建立两个变量间的线性关系模型，用于预测和解释变量间的关系，同时可以评估模型的拟合优度和预测变量的显著性。

【统计结果】
回归方程：{y_col} = {intercept:.4f} + {slope:.4f} × {x_col}
- 截距（a）= {intercept:.4f}：当{x_col} = 0时，{y_col}的预测值
- 斜率（b）= {slope:.4f}：{x_col}每增加1个单位，{y_col}平均{'增加' if slope > 0 else '减少'} {abs(slope):.4f}个单位
- 决定系数 R² = {r_squared:.4f}：模型解释了{y_col}总变异的{r_squared*100:.1f}%
- 斜率检验：p值 = {p_display}（显著性水平 α = {alpha_val}）

在 α = {alpha_val} 水平下，{x_col}对{y_col}{'具有' if p_val < alpha_val else '不具有'}统计学意义的预测作用（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结果解释】
R² = {r_squared:.4f} 表示{x_col}能够解释{y_col}总变异的{r_squared*100:.1f}%，{'模型拟合' + ('较好' if r_squared >= 0.5 else '一般' if r_squared >= 0.3 else '较差') + '。' if p_val < alpha_val else ''}

【结论】
{x_col}对{y_col}{'具有' if p_val < alpha_val else '不具有'}统计学意义的预测作用。
{'回归模型具有统计学意义，' + x_col + '能够显著预测' + y_col + '的变化。' if p_val < alpha_val else '回归模型无统计学意义，' + x_col + '不能有效预测' + y_col + '的变化。'}"""
                except Exception as e:
                    summary_text = f"结果摘要生成失败：{str(e)}"
                
                # 生成PDF（传递图形）
                current_fig = st.session_state.get('current_fig', None)
                pdf_bytes, error_msg = generate_pdf_report(task, df, params, result, summary_text, fig=current_fig)
                
                if pdf_bytes:
                    st.download_button(
                        label="📄 PDF",
                        data=pdf_bytes,
                        file_name=f"stat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        help="下载PDF统计报告",
                        use_container_width=True
                    )
                else:
                    if st.button("📄 PDF", help="生成PDF报告", use_container_width=True):
                        st.warning(f"⚠️ {error_msg}")
            elif st.session_state.current_df is not None and st.session_state.current_task:
                # 有数据和任务但没有结果
                if st.button("📄 PDF", help="生成PDF报告", use_container_width=True):
                    st.info("📄 请先完成统计分析后再生成PDF报告")
            else:
                # 没有数据或任务时显示提示按钮
                if st.button("📄 PDF", help="生成PDF报告", use_container_width=True, disabled=True):
                    pass
                st.caption("请先上传数据并执行分析")
        
        with col_btn2:
            # Python代码下载按钮
            if st.session_state.current_df is not None and st.session_state.current_task:
                python_code = generate_python_code(
                    st.session_state.current_task,
                    st.session_state.current_df,
                    st.session_state.current_params
                )
                st.download_button(
                    label="🐍 代码",
                    data=python_code,
                    file_name="stat_analysis.py",
                    mime="text/x-python",
                    help="下载Python代码文件",
                    use_container_width=True
                )
            else:
                # 没有数据或任务时显示禁用按钮
                if st.button("🐍 代码", help="下载Python代码文件", use_container_width=True, disabled=True):
                    pass
                st.caption("请先上传数据并执行分析")
    
    with col_info:
        st.markdown("**🎓 Shawn · InSynBio**")

st.divider()

# ==================== 左侧栏（紧凑布局） ====================
with st.sidebar:
    st.markdown("### 📋 模块选择")
    
    # 模块选择（单选）- 经典统计放在最前面（最常用）
    module = st.radio(
        "选择分析模块",
        ["📊 经典统计", "🧬 组学分析", "💊 PK/PD & 毒理", "⏱️ 生存分析", "📚 Meta分析"],
        index=0,  # 默认选择经典统计（当前唯一可用）
        help="选择要使用的统计分析模块。经典统计为通用方法，其他模块按药物研发流程顺序排列。"
    )
    
    # 为每个模块添加说明
    module_descriptions = {
        "📊 经典统计": "通用统计方法，适用于所有研究阶段。包含两组比较、多组比较、相关性分析、简单线性回归等基础方法。",
        "🧬 组学分析": "【开发中】靶点发现与验证阶段。包含差异表达分析、富集分析、聚类分析、多组学数据整合等。",
        "💊 PK/PD & 毒理": "【开发中】临床前研究阶段。包含药代动力学参数估计、剂量-效应曲线、毒理学分析等。",
        "⏱️ 生存分析": "【开发中】临床试验结果分析。包含Kaplan-Meier曲线、Cox回归、生存时间分析等。",
        "📚 Meta分析": "【开发中】证据综合阶段。包含固定/随机效应模型、森林图、漏斗图、异质性检验等。"
    }
    
    if module != "📊 经典统计":
        st.info(f"⚠️ {module} 模块正在开发中，敬请期待！")
        with st.expander("ℹ️ 模块说明", expanded=True):
            st.markdown(module_descriptions.get(module, ""))
        st.stop()
    else:
        # 经典统计模块可用，显示说明
        with st.expander("ℹ️ 模块说明", expanded=False):
            st.markdown(module_descriptions.get(module, ""))
    
    # 数据上传（expander）
    with st.expander("📁 数据上传", expanded=False):
        uploaded_file = st.file_uploader(
            "上传 CSV 文件",
            type=['csv'],
            help="请上传包含数值变量和分组变量的 CSV 文件",
            key="file_uploader"
        )
        
        df = None
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ {df.shape[0]} 行 × {df.shape[1]} 列")
                st.session_state.current_df = df
            except Exception as e:
                st.error(f"❌ 读取失败：{str(e)}")
                df = None
        else:
            st.session_state.current_df = None
    
    # 分析设置（expander）- 放在变量选择之前，确保任务改变时变量选择能响应
    with st.expander("⚙️ 分析设置", expanded=False):
        if df is not None:
            task = st.radio(
                "统计任务",
                [
                    "两组比较（t 检验 / Mann–Whitney）",
                    "多组比较（单因素 ANOVA）",
                    "相关性分析（Pearson / Spearman）",
                    "简单线性回归"
                ],
                key="task_radio",
                index=0 if not st.session_state.current_task else [
                    "两组比较（t 检验 / Mann–Whitney）",
                    "多组比较（单因素 ANOVA）",
                    "相关性分析（Pearson / Spearman）",
                    "简单线性回归"
                ].index(st.session_state.current_task) if st.session_state.current_task in [
                    "两组比较（t 检验 / Mann–Whitney）",
                    "多组比较（单因素 ANOVA）",
                    "相关性分析（Pearson / Spearman）",
                    "简单线性回归"
                ] else 0
            )
            
            # 当任务改变时，立即更新 session_state
            if task != st.session_state.get('current_task'):
                st.session_state.current_task = task
            
            # 显示当前选择任务的说明
            st.markdown("---")
            
            # 显示其他开发中的方法
            with st.expander("📋 其他统计方法（开发中）", expanded=False):
                st.markdown("""
                **单样本检验：**
                - 单样本t检验
                - 单样本Wilcoxon检验
                
                **配对样本检验：**
                - 配对样本t检验
                - 配对样本Wilcoxon检验
                
                **分类数据检验：**
                - 卡方检验
                - Fisher精确检验
                - McNemar检验
                
                **非参数多组比较：**
                - Kruskal-Wallis检验
                - Friedman检验
                
                **回归分析：**
                - 多元线性回归
                - 逻辑回归
                - 多项式回归
                
                **方差分析扩展：**
                - 双因素ANOVA
                - 重复测量ANOVA
                - 协方差分析（ANCOVA）
                - 混合效应模型
                
                **其他方法：**
                - 非参数相关性（Kendall's tau）
                - 偏相关分析
                - 中介效应分析
                """)
            
            with st.expander("ℹ️ 方法说明", expanded=False):
                if task == "两组比较（t 检验 / Mann–Whitney）":
                    st.markdown("""
**适用场景：**
• 比较两个独立组别的均值差异
• 需要恰好 2 个组（例如：对照组 vs 实验组）

**方法选择：**
• 系统会自动选择 t 检验（数据正态分布且方差齐性）或 Mann-Whitney U 检验（非正态分布或方差不齐）
• t 检验：适用于正态分布数据，检验效能更高
• Mann-Whitney U 检验：非参数方法，适用于偏态数据或小样本

**数据要求：**
• 分组变量：恰好 2 个组别
• 数值变量：连续型数值
• 样本量：每组至少 3 个观测值
                    """)
                elif task == "多组比较（单因素 ANOVA）":
                    st.markdown("""
**适用场景：**
• 比较三个或更多组别的均值差异
• 需要至少 2 个组（例如：对照组、低剂量组、中剂量组、高剂量组）

**方法说明：**
• 单因素方差分析（One-way ANOVA）
• 如果只有 2 个组，建议使用"两组比较"方法（更精确）

**数据要求：**
• 分组变量：至少 2 个组别（推荐 3 个或更多）
• 数值变量：连续型数值
• 样本量：每组至少 2 个观测值
• 如果 ANOVA 结果显示显著差异，系统会自动进行事后检验（Tukey HSD）以确定具体哪些组间存在差异
                    """)
                elif task == "相关性分析（Pearson / Spearman）":
                    st.markdown("""
**适用场景：**
• 分析两个连续变量之间的相关关系
• 探索变量间的关联强度（不涉及因果关系）

**方法选择：**
• Pearson 相关系数：适用于正态分布数据，衡量线性相关
• Spearman 等级相关系数：非参数方法，适用于非正态数据，衡量单调相关
• 系统会根据数据分布自动选择合适的方法

**数据要求：**
• 变量 X 和变量 Y：两个数值型变量
• 样本量：至少 3 对有效数据
• 数据类型：连续型数值变量
                    """)
                elif task == "简单线性回归":
                    st.markdown("""
**适用场景：**
• 建立因变量与自变量之间的线性关系模型
• 预测因变量的值
• 分析自变量对因变量的影响

**方法说明：**
• 简单线性回归（Simple Linear Regression）
• 建立方程：Y = a + bX（a 为截距，b 为斜率）
• 提供 R²（决定系数）评估模型拟合度

**数据要求：**
• 自变量 X：数值型变量，需要有变异（不能是常数）
• 因变量 Y：数值型变量
• 样本量：至少 3 对有效数据
• 数据类型：连续型数值变量
• 假设：变量间存在线性关系
                    """)
            
            alpha = st.slider("显著性水平 α", 0.01, 0.10, 0.05, 0.01, key="alpha_slider")
            
            if task in ["两组比较（t 检验 / Mann–Whitney）", "多组比较（单因素 ANOVA）"]:
                check_normality = st.checkbox("进行正态性检验", value=True, key="normality_check")
            
            if task == "相关性分析（Pearson / Spearman）":
                method = st.radio("相关性方法", ["auto", "pearson", "spearman"], index=0, key="corr_method")
                st.session_state.current_params['method'] = method
            
            st.session_state.current_params['alpha'] = alpha
            st.session_state.current_params['task'] = task
        else:
            st.info("👆 请先上传数据")
    
    # 变量选择（expander）
    with st.expander("🔧 变量选择", expanded=False):
        if df is not None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
            
            # 智能检测：如果数值列的唯一值较少（<=10），也可以作为潜在的分组变量
            potential_group_cols = cat_cols.copy()
            for col in numeric_cols:
                unique_count = df[col].nunique()
                if unique_count <= 10 and unique_count >= 2:
                    potential_group_cols.append(col)
            
            # 获取当前任务
            task_for_vars = st.session_state.current_task if st.session_state.current_task else "两组比较（t 检验 / Mann–Whitney）"
            
            if task_for_vars == "两组比较（t 检验 / Mann–Whitney）":
                if numeric_cols:
                    # 如果只有一个选项，自动选择并显示为只读
                    if len(numeric_cols) == 1:
                        value_col = numeric_cols[0]
                        st.info(f"📊 因变量（数值）：**{value_col}**（唯一选项，已自动选择）")
                    else:
                        value_col = st.selectbox(
                            "因变量（数值）", 
                            numeric_cols, 
                            key="value_col",
                            help="选择要分析的数值型变量（因变量）"
                        )
                else:
                    st.warning("⚠️ 未找到数值型列")
                    value_col = None
                
                if potential_group_cols:
                    # 如果只有一个选项，自动选择并显示为只读
                    if len(potential_group_cols) == 1:
                        group_col = potential_group_cols[0]
                        st.info(f"📊 分组变量：**{group_col}**（唯一选项，已自动选择）")
                    else:
                        # 优先显示分类列，然后是低唯一值的数值列
                        group_col = st.selectbox(
                            "分组变量", 
                            potential_group_cols, 
                            key="group_col",
                            help="选择包含组别信息的变量（分类变量或唯一值较少的数值变量）"
                        )
                elif cat_cols:
                    if len(cat_cols) == 1:
                        group_col = cat_cols[0]
                        st.info(f"📊 分组变量：**{group_col}**（唯一选项，已自动选择）")
                    else:
                        group_col = st.selectbox("分组变量（分类）", cat_cols, key="group_col")
                else:
                    st.warning("⚠️ 未找到合适的分组变量（分类列或唯一值≤10的数值列）")
                    group_col = None
                
                st.session_state.current_params['value_col'] = value_col
                st.session_state.current_params['group_col'] = group_col
                
            elif task_for_vars == "多组比较（单因素 ANOVA）":
                if numeric_cols:
                    # 如果只有一个选项，自动选择并显示为只读
                    if len(numeric_cols) == 1:
                        value_col = numeric_cols[0]
                        st.info(f"📊 因变量（数值）：**{value_col}**（唯一选项，已自动选择）")
                    else:
                        value_col = st.selectbox(
                            "因变量（数值）", 
                            numeric_cols, 
                            key="value_col_anova",
                            help="选择要分析的数值型变量（因变量）"
                        )
                else:
                    value_col = None
                
                if potential_group_cols:
                    # 如果只有一个选项，自动选择并显示为只读
                    if len(potential_group_cols) == 1:
                        group_col = potential_group_cols[0]
                        st.info(f"📊 分组变量：**{group_col}**（唯一选项，已自动选择）")
                    else:
                        # 优先显示分类列，然后是低唯一值的数值列
                        group_col = st.selectbox(
                            "分组变量", 
                            potential_group_cols, 
                            key="group_col_anova",
                            help="选择包含组别信息的变量（分类变量或唯一值较少的数值变量）"
                        )
                elif cat_cols:
                    if len(cat_cols) == 1:
                        group_col = cat_cols[0]
                        st.info(f"📊 分组变量：**{group_col}**（唯一选项，已自动选择）")
                    else:
                        group_col = st.selectbox("分组变量（分类）", cat_cols, key="group_col_anova")
                else:
                    st.warning("⚠️ 未找到合适的分组变量（分类列或唯一值≤10的数值列）")
                    group_col = None
                
                st.session_state.current_params['value_col'] = value_col
                st.session_state.current_params['group_col'] = group_col
                
            elif task_for_vars == "相关性分析（Pearson / Spearman）":
                if len(numeric_cols) >= 2:
                    col_x = st.selectbox(
                        "变量 X", 
                        numeric_cols, 
                        key="col_x",
                        help="选择第一个数值型变量（自变量）"
                    )
                    remaining_cols = [c for c in numeric_cols if c != col_x]
                    col_y = st.selectbox(
                        "变量 Y", 
                        remaining_cols, 
                        key="col_y",
                        help="选择第二个数值型变量（因变量）"
                    )
                else:
                    st.warning("⚠️ 需要至少 2 个数值型列")
                    col_x = None
                    col_y = None
                
                st.session_state.current_params['col_x'] = col_x
                st.session_state.current_params['col_y'] = col_y
                
            elif task_for_vars == "简单线性回归":
                if len(numeric_cols) >= 2:
                    x_col = st.selectbox(
                        "自变量 X", 
                        numeric_cols, 
                        key="x_col",
                        help="选择作为自变量的数值型变量（解释变量）"
                    )
                    remaining_cols = [c for c in numeric_cols if c != x_col]
                    y_col = st.selectbox(
                        "因变量 Y", 
                        remaining_cols, 
                        key="y_col",
                        help="选择作为因变量的数值型变量（被解释变量）"
                    )
                else:
                    st.warning("⚠️ 需要至少 2 个数值型列")
                    x_col = None
                    y_col = None
                
                st.session_state.current_params['x_col'] = x_col
                st.session_state.current_params['y_col'] = y_col
            
            # 执行分析按钮
            if st.button("🚀 执行分析", type="primary", use_container_width=True, key="run_analysis"):
                st.rerun()
        else:
            st.info("👆 请先上传数据")

# ==================== 主内容区（2:1 布局） ====================
if st.session_state.current_df is not None and st.session_state.current_task:
    df = st.session_state.current_df
    task = st.session_state.current_task
    params = st.session_state.current_params
    
    col_main, col_right = st.columns([2, 1])
    
    # ==================== 中间主区（图 + 结果） ====================
    with col_main:
        try:
            # 图形优化折叠面板（默认展开，方便查看图形）
            with st.expander("🎨 图形优化设置", expanded=True):
                # 使用更紧凑的布局，减少垂直空间
                col_style1, col_style2, col_style3 = st.columns(3)
                
                with col_style1:
                    st.session_state.plot_fontsize = st.slider(
                        "字体大小 (pt)", 
                        min_value=8, 
                        max_value=20, 
                        value=st.session_state.plot_fontsize,
                        step=1,
                        key="fontsize_slider",
                        help="控制图形中所有文字的大小"
                    )
                    st.session_state.plot_linewidth = st.slider(
                        "轴线宽度", 
                        min_value=0.5, 
                        max_value=3.0, 
                        value=st.session_state.plot_linewidth,
                        step=0.1,
                        key="linewidth_slider",
                        help="控制坐标轴和线条的粗细"
                    )
                    st.session_state.plot_pointsize = st.slider(
                        "点大小", 
                        min_value=20, 
                        max_value=200, 
                        value=st.session_state.plot_pointsize,
                        step=10,
                        key="pointsize_slider",
                        help="控制散点图中点的大小（数值越大点越大）"
                    )
                    
                    # 坐标轴设置（放在字体、数值、点大小下面，更紧凑）
                    st.markdown("---")
                    st.markdown("**坐标轴设置**")
                    col_axis1, col_axis2 = st.columns(2)
                    
                    with col_axis1:
                        st.session_state.x_scale = st.selectbox(
                            "X轴刻度",
                            ["线性", "对数", "科学计数法"],
                            index=["线性", "对数", "科学计数法"].index(
                                st.session_state.get('x_scale', "线性") if st.session_state.get('x_scale', "线性") in 
                                ["线性", "对数", "科学计数法"] else "线性"
                            ),
                            key="x_scale_selectbox",
                            help="X轴的数值表示方式"
                        )
                        # 初始化checkbox状态
                        if 'use_x_range_checkbox' not in st.session_state:
                            st.session_state.use_x_range_checkbox = False
                        
                        use_x_range = st.checkbox("设置X轴范围", value=st.session_state.use_x_range_checkbox, key="use_x_range_checkbox")
                        
                        # 如果checkbox状态改变，更新session_state
                        if use_x_range != st.session_state.get('_prev_x_range', False):
                            st.session_state._prev_x_range = use_x_range
                            if not use_x_range:
                                # 取消选中时自动清除数值
                                st.session_state.x_min = None
                                st.session_state.x_max = None
                        
                        if use_x_range:
                            col_x_min, col_x_max = st.columns(2)
                            with col_x_min:
                                x_min_val = st.session_state.get('x_min')
                                if x_min_val is None:
                                    x_min_val = 0.0
                                st.session_state.x_min = st.number_input(
                                    "X最小值", 
                                    value=float(x_min_val), 
                                    key="x_min_input", 
                                    format="%.3f",
                                    step=0.1,
                                    help="X轴的最小值"
                                )
                            with col_x_max:
                                x_max_val = st.session_state.get('x_max')
                                if x_max_val is None:
                                    x_max_val = 10.0
                                st.session_state.x_max = st.number_input(
                                    "X最大值",
                                    value=float(x_max_val),
                                    key="x_max_input",
                                    format="%.3f",
                                    step=0.1,
                                    help="X轴的最大值"
                                )
                        else:
                            # 确保数值被清除
                            st.session_state.x_min = None
                            st.session_state.x_max = None
                    
                    with col_axis2:
                        st.session_state.y_scale = st.selectbox(
                            "Y轴刻度",
                            ["线性", "对数", "科学计数法"],
                            index=["线性", "对数", "科学计数法"].index(
                                st.session_state.get('y_scale', "线性") if st.session_state.get('y_scale', "线性") in 
                                ["线性", "对数", "科学计数法"] else "线性"
                            ),
                            key="y_scale_selectbox",
                            help="Y轴的数值表示方式"
                        )
                        # 初始化checkbox状态
                        if 'use_y_range_checkbox' not in st.session_state:
                            st.session_state.use_y_range_checkbox = False
                        
                        use_y_range = st.checkbox("设置Y轴范围", value=st.session_state.use_y_range_checkbox, key="use_y_range_checkbox")
                        
                        # 如果checkbox状态改变，更新session_state
                        if use_y_range != st.session_state.get('_prev_y_range', False):
                            st.session_state._prev_y_range = use_y_range
                            if not use_y_range:
                                # 取消选中时自动清除数值
                                st.session_state.y_min = None
                                st.session_state.y_max = None
                        
                        if use_y_range:
                            col_y_min, col_y_max = st.columns(2)
                            with col_y_min:
                                y_min_val = st.session_state.get('y_min')
                                if y_min_val is None:
                                    y_min_val = 0.0
                                st.session_state.y_min = st.number_input(
                                    "Y最小值",
                                    value=float(y_min_val),
                                    key="y_min_input",
                                    format="%.3f",
                                    step=0.1,
                                    help="Y轴的最小值"
                                )
                            with col_y_max:
                                y_max_val = st.session_state.get('y_max')
                                if y_max_val is None:
                                    y_max_val = 10.0
                                st.session_state.y_max = st.number_input(
                                    "Y最大值",
                                    value=float(y_max_val),
                                    key="y_max_input",
                                    format="%.3f",
                                    step=0.1,
                                    help="Y轴的最大值"
                                )
                        else:
                            # 确保数值被清除
                            st.session_state.y_min = None
                            st.session_state.y_max = None
                    
                    # 坐标轴重置按钮（放在坐标轴设置区域下方）
                    st.markdown("---")
                    reset_axis_btn = st.button("🔄 重置坐标轴设置", key="reset_axis_btn", help="重置坐标轴设置为默认值（线性刻度，无范围限制）", use_container_width=True)
                    if reset_axis_btn:
                        # 重置所有坐标轴相关设置
                        st.session_state.x_scale = "线性"
                        st.session_state.y_scale = "线性"
                        st.session_state.x_min = None
                        st.session_state.x_max = None
                        st.session_state.y_min = None
                        st.session_state.y_max = None
                        # 使用删除key的方式来重置checkbox（在下次渲染时会使用默认值）
                        if 'use_x_range_checkbox' in st.session_state:
                            del st.session_state['use_x_range_checkbox']
                        if 'use_y_range_checkbox' in st.session_state:
                            del st.session_state['use_y_range_checkbox']
                        # 清除之前的checkbox状态记录
                        if '_prev_x_range' in st.session_state:
                            del st.session_state['_prev_x_range']
                        if '_prev_y_range' in st.session_state:
                            del st.session_state['_prev_y_range']
                        st.rerun()
                
                with col_style2:
                    st.session_state.plot_show_legend = st.checkbox(
                        "显示图例", 
                        value=st.session_state.plot_show_legend,
                        key="legend_checkbox",
                        help="是否在图形上显示图例说明"
                    )
                    st.session_state.plot_theme = st.selectbox(
                        "主题风格",
                        ["基础风格（Basic）", "自然风格（Nature-like）", "演示风格（Presentation）"],
                        index=["基础风格（Basic）", "自然风格（Nature-like）", "演示风格（Presentation）"].index(
                            st.session_state.plot_theme if st.session_state.plot_theme in 
                            ["基础风格（Basic）", "自然风格（Nature-like）", "演示风格（Presentation）"] 
                            else "自然风格（Nature-like）"
                        ),
                        key="theme_selectbox",
                        help="基础风格：经典配色；自然风格：适合学术发表；演示风格：更鲜艳醒目"
                    )
                    st.session_state.plot_color_scheme = st.selectbox(
                        "主色调",
                        ["蓝色系", "绿色系", "橙色系", "紫色系", "黑白灰系", "经典配色"],
                        index=["蓝色系", "绿色系", "橙色系", "紫色系", "黑白灰系", "经典配色"].index(
                            st.session_state.plot_color_scheme if st.session_state.plot_color_scheme in 
                            ["蓝色系", "绿色系", "橙色系", "紫色系", "黑白灰系", "经典配色"] else "蓝色系"
                        ),
                        key="color_scheme_selectbox",
                        help="选择图形的主要颜色方案（黑白灰系适合黑白打印）"
                    )
                    # 图形大小设置（带reset按钮）
                    st.markdown("**图形大小**")
                    st.session_state.plot_width = st.slider(
                        "图形宽度 (英寸)",
                        min_value=1.0,
                        max_value=15.0,
                        value=st.session_state.plot_width,
                        step=0.5,
                        key="plot_width_slider",
                        help="控制图形的宽度，单位：英寸（建议4-8英寸）"
                    )
                    st.session_state.plot_height = st.slider(
                        "图形高度 (英寸)",
                        min_value=1.0,
                        max_value=10.0,
                        value=st.session_state.plot_height,
                        step=0.5,
                        key="plot_height_slider",
                        help="控制图形的高度，单位：英寸（建议3-6英寸）"
                    )
                    # 重置按钮放在下面，横向
                    if st.button("重置大小", key="reset_size_btn", help="重置为默认大小（宽度6.0英寸，高度4.5英寸）", use_container_width=True):
                        st.session_state.plot_width = 6.0
                        st.session_state.plot_height = 4.5
                        st.rerun()
                
                with col_style3:
                    # 图形比例选择
                    st.session_state.plot_aspect = st.selectbox(
                        "图形比例",
                        ["宽（横向）", "正方形", "高（纵向）"],
                        index=["宽（横向）", "正方形", "高（纵向）"].index(
                            st.session_state.plot_aspect if st.session_state.plot_aspect in 
                            ["宽（横向）", "正方形", "高（纵向）"] else "正方形"
                        ),
                        key="plot_aspect_selectbox",
                        help="选择图形的宽高比例"
                    )
                    
                    # 根据任务类型显示不同的图形选择（只显示单一图形，不显示组合）
                    # 可以加误差线的图形默认都加误差线
                    if task in ["两组比较（t 检验 / Mann–Whitney）", "多组比较（单因素 ANOVA）"]:
                        plot_options = [
                            "箱线图", "小提琴图", "条形图+误差线", 
                            "直方图", "密度曲线图", "点图+误差线"
                        ]
                    elif task == "相关性分析（Pearson / Spearman）":
                        plot_options = [
                            "散点图+趋势线", "散点图", "密度图", 
                            "散点图+置信区间", "六边形密度图"
                        ]
                    else:  # 线性回归
                        plot_options = [
                            "散点图+回归线", "散点图", "残差图",
                            "散点图+置信区间", "Q-Q图"
                        ]
                    
                    # 如果当前选择的图形类型不在当前任务的选项中，重置为默认值
                    if st.session_state.plot_type not in plot_options:
                        st.session_state.plot_type = plot_options[0]
                    
                    st.session_state.plot_type = st.selectbox(
                        "图形类型",
                        plot_options,
                        index=plot_options.index(st.session_state.plot_type) if st.session_state.plot_type in plot_options else 0,
                        key="plot_type_selectbox",
                        help="选择要显示的图形类型（一次只显示一张图）"
                    )
                    
                    # 图形宽度和间距控制（所有图形类型）
                    if "条形图" in st.session_state.plot_type:
                        st.session_state.bar_width = st.slider(
                            "柱子宽度",
                            min_value=0.3,
                            max_value=0.95,
                            value=st.session_state.bar_width,
                            step=0.05,
                            key="bar_width_slider",
                            help="控制每个柱子的宽度（0.3-0.95，建议0.6-0.8，符合出版要求）"
                        )
                        st.session_state.bar_spacing = st.slider(
                            "组间间距",
                            min_value=0.1,
                            max_value=1.0,
                            value=st.session_state.bar_spacing,
                            step=0.1,
                            key="bar_spacing_slider",
                            help="控制不同组之间的间距（0.1-1.0，建议0.2-0.5，数值越大间距越大）"
                        )
                    elif "箱线图" in st.session_state.plot_type:
                        st.session_state.box_width = st.slider(
                            "箱线宽度",
                            min_value=0.3,
                            max_value=0.9,
                            value=st.session_state.box_width,
                            step=0.05,
                            key="box_width_slider",
                            help="控制箱线图的宽度（0.3-0.9，建议0.5-0.7）"
                        )
                        st.session_state.box_spacing = st.slider(
                            "组间间距",
                            min_value=0.1,
                            max_value=1.0,
                            value=st.session_state.box_spacing,
                            step=0.1,
                            key="box_spacing_slider",
                            help="控制不同组之间的间距（0.1-1.0，建议0.2-0.5）"
                        )
                    elif "小提琴图" in st.session_state.plot_type:
                        st.session_state.violin_width = st.slider(
                            "小提琴宽度",
                            min_value=0.3,
                            max_value=1.0,
                            value=st.session_state.violin_width,
                            step=0.05,
                            key="violin_width_slider",
                            help="控制小提琴图的宽度（0.3-1.0，建议0.6-0.8）"
                        )
                        st.session_state.violin_spacing = st.slider(
                            "组间间距",
                            min_value=0.1,
                            max_value=1.0,
                            value=st.session_state.violin_spacing,
                            step=0.1,
                            key="violin_spacing_slider",
                            help="控制不同组之间的间距（0.1-1.0，建议0.2-0.5）"
                        )
                    elif "点图" in st.session_state.plot_type:
                        st.session_state.dot_width = st.slider(
                            "点大小",
                            min_value=0.3,
                            max_value=1.0,
                            value=st.session_state.dot_width,
                            step=0.1,
                            key="dot_width_slider",
                            help="控制点图标记的大小（0.3-1.0）"
                        )
                        st.session_state.dot_spacing = st.slider(
                            "组间间距",
                            min_value=0.1,
                            max_value=1.0,
                            value=st.session_state.dot_spacing,
                            step=0.1,
                            key="dot_spacing_slider",
                            help="控制不同组之间的间距（0.1-1.0，建议0.2-0.5）"
                        )
                    
                    # P值显示选项（放在组间距下面）
                    st.session_state.show_pvalue = st.checkbox(
                        "显示P值",
                        value=st.session_state.show_pvalue,
                        key="show_pvalue_checkbox",
                        help="是否在图形上显示P值（符合发表要求的位置和样式）"
                    )
            
            # 获取美化参数
            fontsize = st.session_state.plot_fontsize
            linewidth = st.session_state.plot_linewidth
            pointsize = st.session_state.plot_pointsize
            show_legend = st.session_state.plot_show_legend
            theme = st.session_state.plot_theme
            color_scheme = st.session_state.plot_color_scheme
            plot_type = st.session_state.plot_type
            plot_aspect = st.session_state.plot_aspect
            base_width = st.session_state.plot_width
            base_height = st.session_state.plot_height
            show_pvalue = st.session_state.show_pvalue
            show_stats = st.session_state.show_stats
            bar_width = st.session_state.bar_width
            bar_spacing = st.session_state.bar_spacing
            box_width = st.session_state.box_width
            box_spacing = st.session_state.box_spacing
            violin_width = st.session_state.violin_width
            violin_spacing = st.session_state.violin_spacing
            dot_width = st.session_state.dot_width
            dot_spacing = st.session_state.dot_spacing
            
            # 根据图形比例调整实际尺寸
            if "宽" in plot_aspect or "横向" in plot_aspect:
                # 横向：宽高比约 4:3 或 16:9
                plot_width = base_width * 1.3
                plot_height = base_height * 0.9
            elif "高" in plot_aspect or "纵向" in plot_aspect:
                # 纵向：宽高比约 3:4
                plot_width = base_width * 0.9
                plot_height = base_height * 1.3
            else:  # 正方形
                # 正方形：宽高相等
                plot_width = base_width
                plot_height = base_height  # 使用实际高度，而不是强制使用宽度
            
            # 根据图形尺寸比例动态调整字体大小
            # 基准尺寸：6.0 x 4.5 英寸，基准字体：10pt
            base_size = 6.0 * 4.5  # 基准面积
            current_size = plot_width * plot_height  # 当前面积
            size_ratio = np.sqrt(current_size / base_size)  # 使用平方根，使字体变化更平滑
            # 确保字体大小随图形大小变化，最小不小于基准字体的0.5倍，最大不超过2倍
            adjusted_fontsize = max(fontsize * 0.5, min(fontsize * 2.0, fontsize * size_ratio))
            
            # 根据任务执行分析和绘图
            if task == "两组比较（t 检验 / Mann–Whitney）":
                value_col = params.get('value_col')
                group_col = params.get('group_col')
                alpha = params.get('alpha', 0.05)
                
                # 检查数据是否有足够的列
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
                
                if not numeric_cols:
                    suggestion = f"""
数据缺少数值型变量

当前数据没有数值型列，而两组比较需要至少 1 个数值型变量作为因变量。

当前数值型列：无
当前分类列：{', '.join(cat_cols) if cat_cols else '无'}

建议：
• 检查数据文件是否包含数值型变量
• 如果变量是文本格式的数值，请先在数据中转换为数值型
• 确认数据文件格式是否正确

操作步骤：
1. 检查上传的 CSV 文件是否包含数值型列
2. 如果变量是文本格式，请在 Excel 或其他工具中转换为数值
3. 重新上传数据文件
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                # 检查是否有潜在的分组变量（数值型但唯一值较少的列）
                potential_group_cols = []
                for col in numeric_cols:
                    if df[col].nunique() <= 10 and df[col].nunique() >= 2:
                        potential_group_cols.append(col)
                
                if not cat_cols and not potential_group_cols:
                    # 如果只有数值型列，推荐使用相关性分析或线性回归
                    suggestion = f"""
数据特征不匹配

当前数据包含 {len(numeric_cols)} 个数值型变量，没有分类变量，不适合进行"两组比较"分析。

推荐分析方法：
• **相关性分析（Pearson / Spearman）** - 适合分析两个数值变量之间的关系
• **简单线性回归** - 适合分析一个变量对另一个变量的预测关系

当前数值型变量：{', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''}

操作步骤：
1. 在左侧边栏的"分析设置"中，将"统计任务"改为"相关性分析（Pearson / Spearman）"或"简单线性回归"
2. 重新执行分析
                    """
                    st.info("💡 " + suggestion)
                    st.stop()
                
                # 检查变量是否已选择
                if not value_col or not group_col:
                    suggestion = """
变量未选择

请先在左侧边栏的"变量选择"中选择：
• 因变量（数值）：选择要分析的数值型变量
• 分组变量（分类）：选择包含组别信息的分类变量

操作步骤：
1. 在左侧边栏展开"变量选择"
2. 从下拉菜单中选择"因变量（数值）"
3. 从下拉菜单中选择"分组变量（分类）"
4. 点击"执行分析"按钮
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                if value_col and group_col:
                    # 数据验证和建议
                    is_valid, suggestion = validate_data_and_suggest(task, df, value_col, group_col)
                    if suggestion:
                        # 如果is_valid为True，说明是建议；如果为False，说明是错误
                        if is_valid:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                            st.stop()
                    
                    try:
                        result = two_group_compare(df, value_col, group_col, alpha)
                        st.session_state.current_results = result
                    except (ValueError, KeyError, TypeError) as e:
                        # 捕获统计函数内部的错误，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, value_col=value_col, group_col=group_col
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    except Exception as e:
                        # 捕获其他异常，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, value_col=value_col, group_col=group_col
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    
                    # 图形标题（根据选择的图形类型动态显示）
                    plot_title_map = {
                        "箱线图": "📈 箱线图",
                        "小提琴图": "📈 小提琴图",
                        "条形图": "📈 条形图",
                        "条形图+误差线": "📈 条形图（带误差线）",
                        "直方图": "📈 直方图",
                        "密度曲线图": "📈 密度曲线图",
                        "点图+误差线": "📈 点图（带误差线）"
                    }
                    st.subheader(plot_title_map.get(plot_type, "📈 统计图形"))
                    
                    # 只显示一张图
                    fig, ax = plt.subplots(1, 1, figsize=(plot_width, plot_height))
                    
                    groups = df[group_col].unique()
                    data_list = [df[df[group_col] == g][value_col].dropna() for g in groups]
                    
                    colors = apply_plot_style(fig, ax, adjusted_fontsize, linewidth, pointsize, show_legend, theme, color_scheme)
                    
                    # 根据选择的图形类型绘图
                    if "箱线图" in plot_type:
                        # 箱线图（使用box_width和box_spacing）
                        x_pos = np.arange(len(groups)) * (1 + box_spacing)
                        bp = ax.boxplot(data_list, positions=x_pos, widths=box_width, patch_artist=True)
                        for patch, color in zip(bp['boxes'], colors[:len(groups)]):
                            patch.set_facecolor(color)
                            patch.set_alpha(0.7)
                            patch.set_edgecolor('black')
                            patch.set_linewidth(linewidth)
                        # 设置中位数线
                        for median in bp['medians']:
                            median.set_color('black')
                            median.set_linewidth(linewidth*1.5)
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("箱线图", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = max([data.max() for data in data_list])
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "小提琴图" in plot_type:
                        # 小提琴图（使用violin_width和violin_spacing）
                        # 手动设置位置以控制间距
                        x_pos = np.arange(len(groups)) * (1 + violin_spacing)
                        # 使用positions参数控制位置
                        violin_data = []
                        violin_positions = []
                        for i, g in enumerate(groups):
                            group_data = df[df[group_col] == g][value_col].dropna()
                            violin_data.append(group_data)
                            violin_positions.append(x_pos[i])
                        
                        # 手动绘制小提琴图以控制位置和宽度
                        parts = ax.violinplot(violin_data, positions=x_pos, widths=violin_width*0.8, 
                                            showmeans=True, showmedians=True)
                        # 设置颜色
                        for i, pc in enumerate(parts['bodies']):
                            pc.set_facecolor(colors[i % len(colors)])
                            pc.set_alpha(0.7)
                            pc.set_edgecolor('black')
                            pc.set_linewidth(linewidth)
                        # 设置其他元素颜色
                        for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians', 'cmeans'):
                            if partname in parts:
                                parts[partname].set_color('black')
                                parts[partname].set_linewidth(linewidth)
                        
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("小提琴图", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = df[value_col].max()
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "条形图" in plot_type:
                        # 条形图（优化宽度和间距）
                        means = [data.mean() for data in data_list]
                        # 根据选择的统计量决定误差线
                        if "误差线" in plot_type:
                            if "标准差" in show_stats:
                                errs = [data.std() for data in data_list]
                            elif "标准误" in show_stats:
                                errs = [data.std() / np.sqrt(len(data)) for data in data_list]
                            else:
                                errs = [data.std() for data in data_list]  # 默认使用标准差
                        else:
                            errs = None
                        
                        # 使用 bar_spacing 控制组间距离
                        x_pos = np.arange(len(groups)) * (1 + bar_spacing)
                        
                        if errs is not None:
                            bars = ax.bar(x_pos, means, width=bar_width, yerr=errs, 
                                         color=colors[:len(groups)], alpha=0.8, capsize=5, 
                                         edgecolor='black', linewidth=linewidth,
                                         error_kw={'elinewidth': linewidth*1.5, 'capthick': linewidth*1.5})
                        else:
                            bars = ax.bar(x_pos, means, width=bar_width, 
                                         color=colors[:len(groups)], alpha=0.8, 
                                         edgecolor='black', linewidth=linewidth)
                        
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("条形图" + ("（带误差线）" if errs is not None else ""), fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = max(means) + (max(errs) if errs else 0) * 1.2
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "直方图" in plot_type:
                        # 直方图
                        for i, (g, data) in enumerate(zip(groups, data_list)):
                            ax.hist(data, alpha=0.6, label=str(g), color=colors[i % len(colors)], bins=15)
                        ax.set_xlabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel("频数", fontsize=adjusted_fontsize)
                        ax.set_title("直方图", fontsize=adjusted_fontsize+1)
                        if show_legend:
                            ax.legend(fontsize=adjusted_fontsize-1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = ax.get_ylim()[1]
                        x_pos = np.arange(len(groups))
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "密度曲线" in plot_type:
                        # 密度曲线图
                        for i, (g, data) in enumerate(zip(groups, data_list)):
                            sns.kdeplot(data=data, ax=ax, label=str(g), color=colors[i % len(colors)], linewidth=linewidth*1.5)
                        ax.set_xlabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel("密度", fontsize=adjusted_fontsize)
                        ax.set_title("密度曲线图", fontsize=adjusted_fontsize+1)
                        if show_legend:
                            ax.legend(fontsize=adjusted_fontsize-1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = ax.get_ylim()[1]
                        x_pos = np.arange(len(groups))
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "点图" in plot_type:
                        # 点图+误差线（使用dot_width和dot_spacing）
                        means = [data.mean() for data in data_list]
                        # 根据选择的统计量决定误差线
                        if "标准差" in show_stats:
                            errs = [data.std() for data in data_list]
                        elif "标准误" in show_stats:
                            errs = [data.std() / np.sqrt(len(data)) for data in data_list]
                        else:
                            errs = [data.std() for data in data_list]  # 默认使用标准差
                        x_pos = np.arange(len(groups)) * (1 + dot_spacing)
                        ax.errorbar(x_pos, means, yerr=errs, fmt='o', capsize=5, 
                                   capthick=linewidth*1.5, markersize=pointsize*0.3*dot_width,
                                   color=colors[0], linewidth=linewidth*1.5)
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("点图" + ("（带误差线）" if errs is not None else ""), fontsize=adjusted_fontsize+1)
                        
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = max(means) + max(errs) * 1.2
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    # 保存图形用于PDF生成
                    st.session_state.current_fig = fig
                    plt.close()
                    
            elif task == "多组比较（单因素 ANOVA）":
                value_col = params.get('value_col')
                group_col = params.get('group_col')
                alpha = params.get('alpha', 0.05)
                
                # 检查数据是否有足够的列
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
                
                if not numeric_cols:
                    suggestion = f"""
数据缺少数值型变量

当前数据没有数值型列，而多组比较需要至少 1 个数值型变量作为因变量。

当前数值型列：无
当前分类列：{', '.join(cat_cols) if cat_cols else '无'}

建议：
• 检查数据文件是否包含数值型变量
• 如果变量是文本格式的数值，请先在数据中转换为数值型
• 确认数据文件格式是否正确

操作步骤：
1. 检查上传的 CSV 文件是否包含数值型列
2. 如果变量是文本格式，请在 Excel 或其他工具中转换为数值
3. 重新上传数据文件
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                # 检查是否有潜在的分组变量（数值型但唯一值较少的列）
                potential_group_cols = []
                for col in numeric_cols:
                    if df[col].nunique() <= 10 and df[col].nunique() >= 2:
                        potential_group_cols.append(col)
                
                if not cat_cols and not potential_group_cols:
                    # 如果只有数值型列，推荐使用相关性分析或线性回归
                    suggestion = f"""
数据特征不匹配

当前数据包含 {len(numeric_cols)} 个数值型变量，没有分类变量，不适合进行"多组比较"分析。

推荐分析方法：
• **相关性分析（Pearson / Spearman）** - 适合分析两个数值变量之间的关系
• **简单线性回归** - 适合分析一个变量对另一个变量的预测关系

当前数值型变量：{', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''}

操作步骤：
1. 在左侧边栏的"分析设置"中，将"统计任务"改为"相关性分析（Pearson / Spearman）"或"简单线性回归"
2. 重新执行分析
                    """
                    st.info("💡 " + suggestion)
                    st.stop()
                
                # 检查变量是否已选择
                if not value_col or not group_col:
                    suggestion = """
变量未选择

请先在左侧边栏的"变量选择"中选择：
• 因变量（数值）：选择要分析的数值型变量
• 分组变量（分类）：选择包含组别信息的分类变量

操作步骤：
1. 在左侧边栏展开"变量选择"
2. 从下拉菜单中选择"因变量（数值）"
3. 从下拉菜单中选择"分组变量（分类）"
4. 点击"执行分析"按钮
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                if value_col and group_col:
                    # 数据验证和建议
                    is_valid, suggestion = validate_data_and_suggest(task, df, value_col, group_col)
                    if suggestion:
                        # 如果is_valid为True，说明是建议；如果为False，说明是错误
                        if is_valid:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                            st.stop()
                    
                    try:
                        result = anova_oneway(df, value_col, group_col, alpha)
                        st.session_state.current_results = result
                    except (ValueError, KeyError, TypeError) as e:
                        # 捕获统计函数内部的错误，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, value_col=value_col, group_col=group_col
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    except Exception as e:
                        # 捕获其他异常，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, value_col=value_col, group_col=group_col
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    
                    # 图形标题（根据选择的图形类型动态显示）
                    plot_title_map = {
                        "箱线图": "📈 多组箱线图",
                        "小提琴图": "📈 多组小提琴图",
                        "条形图": "📈 多组条形图",
                        "条形图+误差线": "📈 多组条形图（带误差线）",
                        "直方图": "📈 多组直方图",
                        "密度曲线图": "📈 多组密度曲线图",
                        "点图+误差线": "📈 多组点图（带误差线）"
                    }
                    st.markdown(f"#### {plot_title_map.get(plot_type, '📈 多组统计图形')}")
                    
                    # 只显示一张图
                    fig, ax = plt.subplots(1, 1, figsize=(plot_width, plot_height))
                    
                    groups = sorted(df[group_col].unique())
                    data_list = [df[df[group_col] == g][value_col].dropna() for g in groups]
                    
                    colors = apply_plot_style(fig, ax, adjusted_fontsize, linewidth, pointsize, show_legend, theme, color_scheme)
                    
                    # 根据选择的图形类型绘图（与两组比较相同的逻辑）
                    if "箱线图" in plot_type:
                        # 箱线图（使用box_width和box_spacing）
                        x_pos = np.arange(len(groups)) * (1 + box_spacing)
                        bp = ax.boxplot(data_list, positions=x_pos, widths=box_width, patch_artist=True)
                        for patch, color in zip(bp['boxes'], colors[:len(groups)]):
                            patch.set_facecolor(color)
                            patch.set_alpha(0.7)
                            patch.set_edgecolor('black')
                            patch.set_linewidth(linewidth)
                        for median in bp['medians']:
                            median.set_color('black')
                            median.set_linewidth(linewidth*1.5)
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups, rotation=45)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("多组箱线图", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = max([data.max() for data in data_list])
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "小提琴图" in plot_type:
                        # 小提琴图（使用violin_width和violin_spacing）
                        # 手动设置位置以控制间距
                        x_pos = np.arange(len(groups)) * (1 + violin_spacing)
                        # 使用positions参数控制位置
                        violin_data = []
                        violin_positions = []
                        for i, g in enumerate(groups):
                            group_data = df[df[group_col] == g][value_col].dropna()
                            violin_data.append(group_data)
                            violin_positions.append(x_pos[i])
                        
                        # 手动绘制小提琴图以控制位置和宽度
                        parts = ax.violinplot(violin_data, positions=x_pos, widths=violin_width*0.8, 
                                            showmeans=True, showmedians=True)
                        # 设置颜色
                        for i, pc in enumerate(parts['bodies']):
                            pc.set_facecolor(colors[i % len(colors)])
                            pc.set_alpha(0.7)
                            pc.set_edgecolor('black')
                            pc.set_linewidth(linewidth)
                        # 设置其他元素颜色
                        for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians', 'cmeans'):
                            if partname in parts:
                                parts[partname].set_color('black')
                                parts[partname].set_linewidth(linewidth)
                        
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups, rotation=45)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("多组小提琴图", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = df[value_col].max()
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "条形图" in plot_type:
                        # 条形图（优化宽度和间距）
                        means = [data.mean() for data in data_list]
                        # 根据选择的统计量决定误差线
                        if "误差线" in plot_type:
                            if "标准差" in show_stats:
                                errs = [data.std() for data in data_list]
                            elif "标准误" in show_stats:
                                errs = [data.std() / np.sqrt(len(data)) for data in data_list]
                            else:
                                errs = [data.std() for data in data_list]  # 默认使用标准差
                        else:
                            errs = None
                        x_pos = np.arange(len(groups)) * (1 + bar_spacing)
                        
                        if errs is not None:
                            bars = ax.bar(x_pos, means, width=bar_width, yerr=errs, 
                                         color=colors[:len(groups)], alpha=0.8, capsize=5, 
                                         edgecolor='black', linewidth=linewidth,
                                         error_kw={'elinewidth': linewidth*1.5, 'capthick': linewidth*1.5})
                        else:
                            bars = ax.bar(x_pos, means, width=bar_width, 
                                         color=colors[:len(groups)], alpha=0.8, 
                                         edgecolor='black', linewidth=linewidth)
                        
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups, rotation=45)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("多组条形图" + ("（带误差线）" if errs is not None else ""), fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = max(means) + (max(errs) if errs else 0) * 1.2
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "直方图" in plot_type:
                        # 直方图
                        for i, (g, data) in enumerate(zip(groups, data_list)):
                            ax.hist(data, alpha=0.6, label=str(g), color=colors[i % len(colors)], bins=15)
                        ax.set_xlabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel("频数", fontsize=adjusted_fontsize)
                        ax.set_title("多组直方图", fontsize=adjusted_fontsize+1)
                        if show_legend:
                            ax.legend(fontsize=adjusted_fontsize-1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = ax.get_ylim()[1]
                        x_pos = np.arange(len(groups))
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "密度曲线" in plot_type:
                        # 密度曲线图
                        for i, (g, data) in enumerate(zip(groups, data_list)):
                            sns.kdeplot(data=data, ax=ax, label=str(g), color=colors[i % len(colors)], linewidth=linewidth*1.5)
                        ax.set_xlabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel("密度", fontsize=adjusted_fontsize)
                        ax.set_title("多组密度曲线图", fontsize=adjusted_fontsize+1)
                        if show_legend:
                            ax.legend(fontsize=adjusted_fontsize-1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = ax.get_ylim()[1]
                        x_pos = np.arange(len(groups))
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    elif "点图" in plot_type:
                        # 点图+误差线（使用dot_width和dot_spacing）
                        means = [data.mean() for data in data_list]
                        # 根据选择的统计量决定误差线
                        if "标准差" in show_stats:
                            errs = [data.std() for data in data_list]
                        elif "标准误" in show_stats:
                            errs = [data.std() / np.sqrt(len(data)) for data in data_list]
                        else:
                            errs = [data.std() for data in data_list]  # 默认使用标准差
                        x_pos = np.arange(len(groups)) * (1 + dot_spacing)
                        ax.errorbar(x_pos, means, yerr=errs, fmt='o', capsize=5, 
                                   capthick=linewidth*1.5, markersize=pointsize*0.3*dot_width,
                                   color=colors[0], linewidth=linewidth*1.5)
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(groups, rotation=45)
                        ax.set_xlabel(group_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(value_col, fontsize=adjusted_fontsize)
                        ax.set_title("多组点图（带误差线）", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        # 添加P值
                        p_val = result['p_value']
                        y_max = max(means) + max(errs) * 1.2
                        add_pvalue_text(ax, p_val, np.mean(x_pos), y_max, adjusted_fontsize, show_pvalue, groups=groups, group_names=group_col)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    # 保存图形用于PDF生成
                    st.session_state.current_fig = fig
                    plt.close()
                    
            elif task == "相关性分析（Pearson / Spearman）":
                col_x = params.get('col_x')
                col_y = params.get('col_y')
                method = params.get('method', 'auto')
                alpha = params.get('alpha', 0.05)
                
                # 检查数据是否有足够的数值型列
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) < 2:
                    suggestion = f"""
数据缺少数值型变量

当前数据只有 {len(numeric_cols)} 个数值型列，而相关性分析需要至少 2 个数值型变量。

当前数值型列：{', '.join(numeric_cols) if numeric_cols else '无'}

建议：
• 检查数据文件是否包含足够的数值型变量
• 如果变量是文本格式的数值，请先在数据中转换为数值型
• 如果数据确实只有 1 个数值型变量，可以考虑：
  - 使用"两组比较"或"多组比较"方法（如果有分组变量）
  - 添加更多数值型变量到数据中

操作步骤：
1. 检查上传的 CSV 文件是否包含至少 2 个数值型列
2. 如果变量是文本格式，请在 Excel 或其他工具中转换为数值
3. 重新上传数据文件
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                # 检查变量是否已选择
                if not col_x or not col_y:
                    suggestion = """
变量未选择

请先在左侧边栏的"变量选择"中选择：
• 变量 X：选择第一个数值型变量
• 变量 Y：选择第二个数值型变量

操作步骤：
1. 在左侧边栏展开"变量选择"
2. 从下拉菜单中选择"变量 X"
3. 从下拉菜单中选择"变量 Y"
4. 点击"执行分析"按钮
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                if col_x and col_y:
                    # 数据验证和建议
                    is_valid, suggestion = validate_data_and_suggest(task, df, col_x=col_x, col_y=col_y)
                    if suggestion:
                        # 如果is_valid为True，说明是建议；如果为False，说明是错误
                        if is_valid:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                            st.stop()
                    
                    try:
                        result = correlation(df, col_x, col_y, method, alpha)
                        st.session_state.current_results = result
                    except (ValueError, KeyError, TypeError) as e:
                        # 捕获统计函数内部的错误，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, col_x=col_x, col_y=col_y
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    except Exception as e:
                        # 捕获其他异常，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, col_x=col_x, col_y=col_y
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    
                    st.markdown("#### 📈 散点图与趋势线")
                    
                    # 单图时使用完整尺寸，并居中显示
                    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                    colors = apply_plot_style(fig, ax, adjusted_fontsize, linewidth, pointsize, show_legend, theme, color_scheme)
                    
                    # 根据选择的图形类型绘图
                    if "散点图" in plot_type:
                        ax.scatter(df[col_x], df[col_y], alpha=0.6, s=pointsize, color=colors[0], edgecolors='black', linewidths=0.5)
                        ax.set_xlabel(col_x, fontsize=adjusted_fontsize)
                        ax.set_ylabel(col_y, fontsize=adjusted_fontsize)
                        ax.set_title(f"散点图（{result['method_name']}）", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        
                        if "趋势线" in plot_type or "回归线" in plot_type:
                            z = np.polyfit(df[col_x].dropna(), df[col_y].dropna(), 1)
                            p = np.poly1d(z)
                            ax.plot(df[col_x], p(df[col_x]), color=colors[1], linestyle='--', 
                                   linewidth=linewidth*1.5, alpha=0.8, label="趋势线")
                            if show_legend:
                                ax.legend(fontsize=fontsize-1)
                        
                        if "置信区间" in plot_type:
                            # 添加置信区间
                            from scipy import stats
                            z = np.polyfit(df[col_x].dropna(), df[col_y].dropna(), 1)
                            x_line = np.linspace(df[col_x].min(), df[col_x].max(), 100)
                            y_line = z[0] * x_line + z[1]
                            # 计算置信区间（简化版）
                            n = len(df[[col_x, col_y]].dropna())
                            se = np.sqrt(np.sum((df[col_y] - (z[0]*df[col_x] + z[1]))**2) / (n-2))
                            t_val = stats.t.ppf(0.975, n-2)
                            ci = t_val * se * np.sqrt(1/n + (x_line - df[col_x].mean())**2 / np.sum((df[col_x] - df[col_x].mean())**2))
                            ax.fill_between(x_line, y_line - ci, y_line + ci, alpha=0.2, color=colors[1], label="95%置信区间")
                            if show_legend:
                                ax.legend(fontsize=fontsize-1)
                        
                        # 添加P值和相关系数标注
                        p_val = result['p_value']
                        r_val = result['stat']
                        p_text = f"r = {r_val:.4f}\np = {p_val:.4f}" if p_val >= 0.0001 else f"r = {r_val:.4f}\np < 0.0001"
                        ax.text(0.05, 0.95, p_text, transform=ax.transAxes, 
                               fontsize=fontsize, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                    elif "密度图" in plot_type:
                        if "六边形" in plot_type:
                            # 六边形密度图
                            ax.hexbin(df[col_x], df[col_y], gridsize=20, cmap='Blues', mincnt=1)
                            ax.set_xlabel(col_x, fontsize=adjusted_fontsize)
                            ax.set_ylabel(col_y, fontsize=adjusted_fontsize)
                            ax.set_title("六边形密度图", fontsize=adjusted_fontsize+1)
                            plt.colorbar(ax.collections[0], ax=ax)
                            # 应用坐标轴设置
                            apply_axis_settings(ax, 
                                               x_scale=st.session_state.get('x_scale', "线性"),
                                               y_scale=st.session_state.get('y_scale', "线性"),
                                               x_min=st.session_state.get('x_min'),
                                               x_max=st.session_state.get('x_max'),
                                               y_min=st.session_state.get('y_min'),
                                               y_max=st.session_state.get('y_max'))
                        else:
                            # 密度图
                            for i, col in enumerate([col_x, col_y]):
                                data = df[col].dropna()
                                ax.hist(data, alpha=0.6, label=col, color=colors[i], bins=20, density=True)
                            ax.set_xlabel("数值", fontsize=fontsize)
                            ax.set_ylabel("密度", fontsize=fontsize)
                            ax.set_title("密度分布图", fontsize=fontsize+1)
                            if show_legend:
                                ax.legend(fontsize=fontsize-1)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    # 保存图形用于PDF生成
                    st.session_state.current_fig = fig
                    plt.close()
                    
            elif task == "简单线性回归":
                x_col = params.get('x_col')
                y_col = params.get('y_col')
                alpha = params.get('alpha', 0.05)
                
                # 检查数据是否有足够的数值型列
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) < 2:
                    suggestion = f"""
数据缺少数值型变量

当前数据只有 {len(numeric_cols)} 个数值型列，而线性回归需要至少 2 个数值型变量（自变量和因变量）。

当前数值型列：{', '.join(numeric_cols) if numeric_cols else '无'}

建议：
• 检查数据文件是否包含足够的数值型变量
• 如果变量是文本格式的数值，请先在数据中转换为数值型
• 如果数据确实只有 1 个数值型变量，可以考虑：
  - 使用"两组比较"或"多组比较"方法（如果有分组变量）
  - 添加更多数值型变量到数据中

操作步骤：
1. 检查上传的 CSV 文件是否包含至少 2 个数值型列
2. 如果变量是文本格式，请在 Excel 或其他工具中转换为数值
3. 重新上传数据文件
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                # 检查变量是否已选择
                if not x_col or not y_col:
                    suggestion = """
变量未选择

请先在左侧边栏的"变量选择"中选择：
• 自变量 X：选择作为自变量的数值型变量
• 因变量 Y：选择作为因变量的数值型变量

操作步骤：
1. 在左侧边栏展开"变量选择"
2. 从下拉菜单中选择"自变量 X"
3. 从下拉菜单中选择"因变量 Y"
4. 点击"执行分析"按钮
                    """
                    st.error("❌ " + suggestion)
                    st.stop()
                
                if x_col and y_col:
                    # 数据验证和建议
                    is_valid, suggestion = validate_data_and_suggest(task, df, x_col=x_col, y_col=y_col)
                    if suggestion:
                        # 如果is_valid为True，说明是建议；如果为False，说明是错误
                        if is_valid:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                            st.stop()
                    
                    try:
                        result = linear_regression_simple(df, x_col, y_col, alpha)
                        st.session_state.current_results = result
                    except (ValueError, KeyError, TypeError) as e:
                        # 捕获统计函数内部的错误，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, x_col=x_col, y_col=y_col
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    except Exception as e:
                        # 捕获其他异常，并智能推荐方法
                        error_msg = str(e)
                        recommended_method, suggestion, is_suggestion = suggest_alternative_method(
                            error_msg, task, df, x_col=x_col, y_col=y_col
                        )
                        if is_suggestion:
                            st.info("💡 " + suggestion)
                        else:
                            st.error("❌ " + suggestion)
                        st.stop()
                    
                    st.markdown("#### 📈 回归散点图与拟合直线")
                    
                    # 单图时使用完整尺寸，并居中显示
                    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                    colors = apply_plot_style(fig, ax, adjusted_fontsize, linewidth, pointsize, show_legend, theme, color_scheme)
                    
                    if "散点图" in plot_type:
                        ax.scatter(df[x_col], df[y_col], alpha=0.6, s=pointsize, color=colors[0], 
                                 edgecolors='black', linewidths=0.5, label="数据点")
                        ax.set_xlabel(x_col, fontsize=adjusted_fontsize)
                        ax.set_ylabel(y_col, fontsize=adjusted_fontsize)
                        ax.set_title("简单线性回归", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                        
                        if "回归线" in plot_type:
                            x_line = np.linspace(df[x_col].min(), df[x_col].max(), 100)
                            slope = result['extra_info'].get('slope', 0)
                            intercept = result['extra_info'].get('intercept', 0)
                            y_line = slope * x_line + intercept
                            ax.plot(x_line, y_line, color=colors[1], linewidth=linewidth*2, label="回归线")
                            if show_legend:
                                ax.legend(fontsize=fontsize-1)
                        
                        if "置信区间" in plot_type:
                            # 添加置信区间
                            from statsmodels.api import OLS, add_constant
                            X = add_constant(df[x_col])
                            y = df[y_col]
                            model = OLS(y, X).fit()
                            x_line = np.linspace(df[x_col].min(), df[x_col].max(), 100)
                            X_pred = add_constant(x_line)
                            pred = model.get_prediction(X_pred)
                            ci = pred.conf_int()
                            y_line = model.predict(X_pred)
                            ax.fill_between(x_line, ci[:, 0], ci[:, 1], alpha=0.2, color=colors[1], label="95%置信区间")
                            if show_legend:
                                ax.legend(fontsize=fontsize-1)
                        
                        # 添加P值、R²和回归方程标注
                        p_val = result['p_value']
                        r_squared = result['extra_info'].get('r_squared', 0)
                        slope = result['extra_info'].get('slope', 0)
                        intercept = result['extra_info'].get('intercept', 0)
                        p_text = f"R² = {r_squared:.4f}\np = {p_val:.4f}" if p_val >= 0.0001 else f"R² = {r_squared:.4f}\np < 0.0001"
                        eq_text = f"y = {intercept:.3f} + {slope:.3f}x"
                        ax.text(0.05, 0.95, p_text + "\n" + eq_text, transform=ax.transAxes, 
                               fontsize=fontsize, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                    elif "残差图" in plot_type:
                        # 残差图
                        from statsmodels.api import OLS, add_constant
                        X = add_constant(df[x_col])
                        y = df[y_col]
                        model = OLS(y, X).fit()
                        residuals = model.resid
                        fitted = model.fittedvalues
                        ax.scatter(fitted, residuals, alpha=0.6, s=pointsize, color=colors[0], 
                                 edgecolors='black', linewidths=0.5)
                        ax.axhline(y=0, color=colors[1], linestyle='--', linewidth=linewidth*1.5)
                        ax.set_xlabel("拟合值", fontsize=adjusted_fontsize)
                        ax.set_ylabel("残差", fontsize=adjusted_fontsize)
                        ax.set_title("残差图", fontsize=adjusted_fontsize+1)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                    elif "Q-Q图" in plot_type:
                        # Q-Q图（正态性检验）
                        from statsmodels.api import OLS, add_constant
                        from scipy import stats
                        X = add_constant(df[x_col])
                        y = df[y_col]
                        model = OLS(y, X).fit()
                        residuals = model.resid
                        stats.probplot(residuals, dist="norm", plot=ax)
                        ax.set_xlabel("理论分位数", fontsize=adjusted_fontsize)
                        ax.set_ylabel("样本分位数", fontsize=adjusted_fontsize)
                        ax.set_title("Q-Q图（残差正态性检验）", fontsize=adjusted_fontsize+1)
                        ax.grid(True, alpha=0.3)
                        # 应用坐标轴设置
                        apply_axis_settings(ax, 
                                           x_scale=st.session_state.get('x_scale', "线性"),
                                           y_scale=st.session_state.get('y_scale', "线性"),
                                           x_min=st.session_state.get('x_min'),
                                           x_max=st.session_state.get('x_max'),
                                           y_min=st.session_state.get('y_min'),
                                           y_max=st.session_state.get('y_max'))
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    # 保存图形用于PDF生成
                    st.session_state.current_fig = fig
                    plt.close()
            
            # 统计结果展示
            if st.session_state.current_results:
                result = st.session_state.current_results
                
                st.divider()
                st.subheader("📊 统计结果")
                
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    # 方法名称（带解释）
                    method_name = result['method_name']
                    method_help = ""
                    if "t 检验" in method_name:
                        method_help = "独立样本t检验：用于比较两组独立样本的均值差异，要求数据近似正态分布且方差齐性。"
                    elif "Mann-Whitney" in method_name or "Mann–Whitney" in method_name:
                        method_help = "Mann-Whitney U检验：非参数检验方法，用于比较两组独立样本，不要求正态分布，适用于偏态数据或小样本。"
                    elif "Welch" in method_name:
                        method_help = "Welch's t检验：用于比较两组独立样本的均值，适用于方差不齐的情况。"
                    elif "ANOVA" in method_name or "方差分析" in method_name:
                        method_help = "单因素方差分析（ANOVA）：用于比较三个或更多组间的均值差异，要求数据近似正态分布且方差齐性。"
                    elif "Pearson" in method_name:
                        method_help = "Pearson相关系数：衡量两个连续变量间的线性相关程度，要求数据近似正态分布。"
                    elif "Spearman" in method_name:
                        method_help = "Spearman等级相关系数：非参数方法，衡量两个变量间的单调相关关系，不要求正态分布。"
                    elif "线性回归" in method_name or "OLS" in method_name:
                        method_help = "简单线性回归：建立因变量与自变量间的线性关系模型，用于预测和解释变量间的关系。"
                    
                    st.markdown(f"**方法：** {method_name}")
                    if method_help:
                        with st.expander("ℹ️ 方法说明", expanded=False):
                            st.write(method_help)
                    
                    # 检验统计量（带解释）
                    stat_help = "检验统计量：根据样本数据计算出的统计量值，用于判断是否拒绝原假设。数值越大通常表示差异越明显。"
                    st.markdown(f"**检验统计量：** {result['stat']:.4f}")
                    with st.expander("ℹ️ 检验统计量说明", expanded=False):
                        st.write(stat_help)
                
                with col_stat2:
                    p_val = result['p_value']
                    p_display = f"{p_val:.4e}" if p_val < 0.001 else f"{p_val:.4f}"
                    
                    # p值（带解释）
                    p_help = "p值：在原假设为真的前提下，观察到当前结果或更极端结果的概率。p < α 时拒绝原假设，认为差异有统计学意义。"
                    st.markdown(f"**p 值：** {p_display}")
                    with st.expander("ℹ️ p值说明", expanded=False):
                        st.write(p_help)
                    
                    alpha_val = params.get('alpha', 0.05)
                    significance = "有统计学意义" if p_val < alpha_val else "无统计学意义"
                    
                    # 结论（带解释）
                    sig_help = f"结论：基于显著性水平 α = {alpha_val} 的判断。p < {alpha_val} 表示差异有统计学意义；p ≥ {alpha_val} 表示差异无统计学意义。"
                    st.markdown(f"**结论：** {significance}")
                    with st.expander("ℹ️ 结论说明", expanded=False):
                        st.write(sig_help)
                
                st.info(f"💡 {result['explanation_zh']}")
                
                # 多组比较的事后检验（Post-hoc test）
                if task == "多组比较（单因素 ANOVA）":
                    p_val = result['p_value']
                    alpha_val = params.get('alpha', 0.05)
                    if p_val < alpha_val:
                        st.markdown("---")
                        st.markdown("**🔍 事后检验（Post-hoc Test）**")
                        st.info("💡 ANOVA结果显示各组间存在显著差异。建议进行事后检验以确定具体哪些组间存在差异。")
                        
                        value_col = params.get('value_col')
                        group_col = params.get('group_col')
                        if value_col and group_col:
                            try:
                                from scipy.stats import tukey_hsd
                                
                                groups = sorted(df[group_col].unique())
                                group_data = [df[df[group_col] == g][value_col].dropna() for g in groups]
                                
                                # 使用Tukey HSD检验
                                tukey_result = tukey_hsd(*group_data)
                                
                                # 创建成对比较结果表格
                                posthoc_data = []
                                for i in range(len(groups)):
                                    for j in range(i+1, len(groups)):
                                        p_adj = tukey_result.pvalue[i, j]
                                        p_display = f"{p_adj:.4e}" if p_adj < 0.001 else f"{p_adj:.4f}"
                                        significant = "是" if p_adj < alpha_val else "否"
                                        posthoc_data.append({
                                            "组1": str(groups[i]),
                                            "组2": str(groups[j]),
                                            "p值（调整后）": p_display,
                                            f"显著（α={alpha_val}）": significant
                                        })
                                
                                if posthoc_data:
                                    import pandas as pd
                                    posthoc_df = pd.DataFrame(posthoc_data)
                                    st.dataframe(posthoc_df, use_container_width=True, hide_index=True)
                                    
                                    # 显示显著差异的组对
                                    significant_pairs = [row for row in posthoc_data if row[f"显著（α={alpha_val}）"] == "是"]
                                    if significant_pairs:
                                        st.success(f"✅ 发现 {len(significant_pairs)} 对组间存在显著差异：")
                                        for pair in significant_pairs:
                                            st.write(f"  - {pair['组1']} vs {pair['组2']}: p = {pair['p值（调整后）']}")
                                    else:
                                        st.info("ℹ️ 虽然ANOVA显示各组间存在显著差异，但Tukey HSD检验未发现任何组对间存在显著差异（可能由于多重比较校正）。")
                                        
                            except Exception as e:
                                st.warning(f"⚠️ 无法执行Tukey HSD检验：{str(e)}。可能原因：样本量不足或数据不符合要求。")
                
                # 统计量显示选项和表格（仅在统计结果区域显示）
                st.markdown("---")
                st.markdown("**📊 描述性统计量**")
                
                # 统计量选择
                st.session_state.show_stats = st.multiselect(
                    "选择要显示的统计量",
                    ["平均值", "中位数", "置信区间", "标准差", "标准误"],
                    default=st.session_state.show_stats if st.session_state.show_stats else [],
                    key="show_stats_multiselect",
                    help="选择要在结果表格中显示的统计量"
                )
                
                # 根据任务类型计算并显示统计量表格
                if task in ["两组比较（t 检验 / Mann–Whitney）", "多组比较（单因素 ANOVA）"]:
                    value_col = params.get('value_col')
                    group_col = params.get('group_col')
                    if value_col and group_col and st.session_state.show_stats:
                        groups = sorted(df[group_col].unique()) if task == "多组比较（单因素 ANOVA）" else df[group_col].unique()
                        data_list = [df[df[group_col] == g][value_col].dropna() for g in groups]
                        
                        # 计算统计量
                        from scipy import stats
                        stats_data = []
                        for i, (g, data) in enumerate(zip(groups, data_list)):
                            row = {"组别": str(g), "样本量": len(data)}
                            if "平均值" in st.session_state.show_stats:
                                row["平均值"] = f"{data.mean():.4f}"
                            if "中位数" in st.session_state.show_stats:
                                row["中位数"] = f"{data.median():.4f}"
                            if "标准差" in st.session_state.show_stats:
                                row["标准差（SD）"] = f"{data.std():.4f}"
                            if "标准误" in st.session_state.show_stats:
                                row["标准误（SE）"] = f"{data.std() / np.sqrt(len(data)):.4f}"
                            if "置信区间" in st.session_state.show_stats and len(data) > 1:
                                ci = stats.t.interval(0.95, len(data)-1, loc=data.mean(), scale=stats.sem(data))
                                row["95%置信区间"] = f"[{ci[0]:.4f}, {ci[1]:.4f}]"
                            stats_data.append(row)
                        
                        if stats_data:
                            import pandas as pd
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(stats_df, use_container_width=True, hide_index=True)
                    elif not st.session_state.show_stats:
                        st.info("💡 请在上方选择要显示的统计量")
                
                # 统计量定义和使用指南
                st.markdown("---")
                with st.expander("ℹ️ 描述性统计量定义和使用指南", expanded=False):
                    st.markdown("""
                    **平均值（Mean）**
                    - **定义**：所有观测值的算术平均数，计算公式为：Mean = Σx/n
                    - **使用场合**：
                      - 数据近似正态分布时，平均值是描述集中趋势的最佳指标
                      - 用于参数检验（如t检验、ANOVA）的前提条件
                      - 适合用于：对称分布数据、大样本数据、连续变量
                    - **注意事项**：对异常值敏感，偏态分布时可能不具有代表性
                    
                    **中位数（Median）**
                    - **定义**：将数据从小到大排列后，位于中间位置的数值
                    - **使用场合**：
                      - 数据呈偏态分布时，中位数比平均值更能代表数据的中心位置
                      - 存在异常值时，中位数比平均值更稳健
                      - 适合用于：偏态分布数据、小样本数据、有序分类变量
                    - **注意事项**：不适用于参数检验，但可用于非参数检验（如Mann-Whitney U检验）
                    
                    **标准差（SD）**
                    - **定义**：描述数据离散程度的指标，计算公式为：SD = √[Σ(x-μ)²/n]
                    - **使用场合**：
                      - 描述样本数据的实际变异范围
                      - 在条形图、点图中显示误差线时，使用SD可以展示数据的实际变异程度
                      - 适合用于：描述性统计、数据可视化、比较组间变异程度
                    - **注意事项**：与平均值在同一量纲，便于理解数据的实际变异
                    
                    **标准误（SE）**
                    - **定义**：样本均值的抽样误差，计算公式为：SE = SD/√n
                    - **使用场合**：
                      - 描述样本均值估计总体均值的精度
                      - 用于推断总体均值的置信区间
                      - 在条形图、点图中显示误差线时，使用SE可以展示均值的估计精度
                      - 适合用于：统计推断、假设检验、置信区间估计、发表论文
                    - **注意事项**：SE会随样本量增大而减小，反映的是均值的可靠性
                    
                    **置信区间（95% CI）**
                    - **定义**：在95%的置信水平下，总体参数可能落入的区间范围
                    - **使用场合**：
                      - 估计总体参数（如总体均值）的可能范围
                      - 判断两组差异是否有统计学意义（置信区间不重叠通常表示有显著差异）
                      - 适合用于：统计推断、假设检验、发表论文、报告研究结果
                    - **注意事项**：置信区间不包含0（或无效值）通常表示有统计学意义
                    
                    **选择建议总结：**
                    - **描述数据特征**：平均值 + 标准差（SD）
                    - **偏态数据或异常值**：中位数 + 四分位距（IQR）
                    - **统计推断**：平均值 + 标准误（SE）或置信区间
                    - **发表论文**：通常报告平均值 ± 标准误（SE）或平均值（95% CI）
                    - **数据可视化**：条形图/点图误差线通常使用SE（统计推断）或SD（描述变异）
                    """)
                
                # 生成详细的结果摘要（包含数据描述、方法选择理由、详细结果）
                if task == "两组比较（t 检验 / Mann–Whitney）":
                    value_col = params.get('value_col')
                    group_col = params.get('group_col')
                    groups = df[group_col].unique()
                    group1_data = df[df[group_col] == groups[0]][value_col].dropna()
                    group2_data = df[df[group_col] == groups[1]][value_col].dropna()
                    n1 = len(group1_data)
                    n2 = len(group2_data)
                    mean1 = group1_data.mean()
                    mean2 = group2_data.mean()
                    std1 = group1_data.std()
                    std2 = group2_data.std()
                    
                    # 方法选择理由
                    method_reason = ""
                    if "t 检验" in result['method_name']:
                        method_reason = "数据满足正态分布和方差齐性假设，因此选择独立样本t检验。"
                    elif "Mann-Whitney" in result['method_name'] or "Mann–Whitney" in result['method_name']:
                        method_reason = "数据不满足正态分布或方差齐性假设，因此选择非参数Mann-Whitney U检验。"
                    
                    summary_text = f"""【数据描述】
本研究分析了{value_col}变量在{groups[0]}组和{groups[1]}组之间的差异。
- 因变量：{value_col}（数值型变量）
- 分组变量：{group_col}（{groups[0]}组 vs {groups[1]}组）
- 样本量：{groups[0]}组 n={n1}，{groups[1]}组 n={n2}，总计 n={n1+n2}
- 描述性统计：{groups[0]}组 均值={mean1:.2f}±{std1:.2f}，{groups[1]}组 均值={mean2:.2f}±{std2:.2f}

【方法选择】
使用{result['method_name']}进行两组比较。{method_reason}
该方法适用于比较两个独立组别的均值差异，能够有效控制第一类错误率。

【统计结果】
检验统计量 = {result['stat']:.4f}，p值 = {p_display}（显著性水平 α = {alpha_val}）。
在 α = {alpha_val} 水平下，两组间差异{'具有' if p_val < alpha_val else '不具有'}统计学意义（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结论】
{groups[0]}组与{groups[1]}组在{value_col}变量上{'存在' if p_val < alpha_val else '不存在'}显著差异。
{'均值差异为' + f'{abs(mean1-mean2):.2f}' if p_val < alpha_val else '两组均值差异无统计学意义'}。"""
                    
                elif task == "多组比较（单因素 ANOVA）":
                    value_col = params.get('value_col')
                    group_col = params.get('group_col')
                    groups = sorted(df[group_col].unique())
                    group_data_list = [df[df[group_col] == g][value_col].dropna() for g in groups]
                    group_ns = [len(data) for data in group_data_list]
                    group_means = [data.mean() for data in group_data_list]
                    group_stds = [data.std() for data in group_data_list]
                    groups_str = "、".join([f"{g}（n={n}）" for g, n in zip(groups, group_ns)])
                    means_str = "、".join([f"{g}={mean:.2f}±{std:.2f}" for g, mean, std in zip(groups, group_means, group_stds)])
                    
                    summary_text = f"""【数据描述】
本研究分析了{value_col}变量在多个组别之间的差异。
- 因变量：{value_col}（数值型变量）
- 分组变量：{group_col}（共{len(groups)}个组：{groups_str}）
- 总样本量：n={sum(group_ns)}
- 描述性统计：{means_str}

【方法选择】
使用{result['method_name']}进行多组比较。
单因素方差分析适用于比较三个或更多组间的均值差异，能够同时检验所有组间是否存在显著差异，避免多次两两比较带来的多重比较问题。

【统计结果】
F统计量 = {result['stat']:.4f}，p值 = {p_display}（显著性水平 α = {alpha_val}）。
在 α = {alpha_val} 水平下，各组间差异{'具有' if p_val < alpha_val else '不具有'}统计学意义（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。"""
                    
                    if p_val < alpha_val and 'posthoc' in result.get('extra_info', {}):
                        posthoc_info = result['extra_info'].get('posthoc', {})
                        if posthoc_info:
                            summary_text += f"\n\n【事后检验（Tukey HSD）】\n"
                            summary_text += "ANOVA结果显示各组间存在显著差异，进一步进行Tukey HSD事后检验："
                            # 这里可以添加事后检验的详细结果
                    
                    summary_text += f"""

【结论】
各组在{value_col}变量上{'存在' if p_val < alpha_val else '不存在'}显著差异。
{'建议进行事后检验以确定具体哪些组间存在差异。' if p_val < alpha_val else '各组均值差异无统计学意义。'}"""
                    
                elif task == "相关性分析（Pearson / Spearman）":
                    col_x = params.get('col_x')
                    col_y = params.get('col_y')
                    valid_data = df[[col_x, col_y]].dropna()
                    n = len(valid_data)
                    x_mean = valid_data[col_x].mean()
                    y_mean = valid_data[col_y].mean()
                    x_std = valid_data[col_x].std()
                    y_std = valid_data[col_y].std()
                    corr_coef = result['stat']
                    
                    # 方法选择理由
                    method_reason = ""
                    if "Pearson" in result['method_name']:
                        method_reason = "数据满足正态分布假设，因此选择Pearson相关系数分析线性相关关系。"
                    elif "Spearman" in result['method_name']:
                        method_reason = "数据不满足正态分布假设，因此选择Spearman等级相关系数分析单调相关关系。"
                    
                    # 相关性强度解释
                    abs_corr = abs(corr_coef)
                    if abs_corr >= 0.7:
                        strength = "强相关"
                    elif abs_corr >= 0.4:
                        strength = "中等相关"
                    elif abs_corr >= 0.2:
                        strength = "弱相关"
                    else:
                        strength = "几乎无相关"
                    
                    direction = "正相关" if corr_coef > 0 else "负相关"
                    
                    summary_text = f"""【数据描述】
本研究分析了{col_x}与{col_y}两个变量之间的相关关系。
- 变量X：{col_x}（均值={x_mean:.2f}±{x_std:.2f}）
- 变量Y：{col_y}（均值={y_mean:.2f}±{y_std:.2f}）
- 有效样本量：n={n}（去除缺失值后）
- 数据特征：两个连续型数值变量

【方法选择】
使用{result['method_name']}进行相关性分析。{method_reason}
该方法能够量化两个变量之间的相关程度和方向。

【统计结果】
相关系数 r = {corr_coef:.4f}，p值 = {p_display}（显著性水平 α = {alpha_val}）。
在 α = {alpha_val} 水平下，两变量间{'存在' if p_val < alpha_val else '不存在'}统计学意义的相关关系（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结果解释】
相关系数 r = {corr_coef:.4f} 表示{col_x}与{col_y}之间存在{strength}的{direction}关系。
{'根据Cohen（1988）的标准：' + strength + '（|r| ' + ('≥0.7' if abs_corr >= 0.7 else '≥0.4' if abs_corr >= 0.4 else '≥0.2' if abs_corr >= 0.2 else '<0.2') + '）。' if p_val < alpha_val else ''}

【结论】
{col_x}与{col_y}之间{'存在' if p_val < alpha_val else '不存在'}统计学意义的相关关系。
{'两变量间存在' + strength + '的' + direction + '关系，' + ('随着' if corr_coef > 0 else '随着') + col_x + '的增加，' + col_y + ('也增加' if corr_coef > 0 else '减少') + '。' if p_val < alpha_val else '两变量间无显著相关关系。'}"""
                    
                elif task == "简单线性回归":
                    x_col = params.get('x_col')
                    y_col = params.get('y_col')
                    valid_data = df[[x_col, y_col]].dropna()
                    n = len(valid_data)
                    x_mean = valid_data[x_col].mean()
                    y_mean = valid_data[y_col].mean()
                    slope = result['extra_info'].get('slope', 0)
                    intercept = result['extra_info'].get('intercept', 0)
                    r_squared = result['extra_info'].get('r_squared', 0)
                    
                    summary_text = f"""【数据描述】
本研究分析了{x_col}对{y_col}的预测作用，建立简单线性回归模型。
- 自变量X：{x_col}（均值={x_mean:.2f}）
- 因变量Y：{y_col}（均值={y_mean:.2f}）
- 有效样本量：n={n}（去除缺失值后）
- 模型类型：简单线性回归（Y = a + bX）

【方法选择】
使用简单线性回归分析{x_col}对{y_col}的影响。
线性回归能够建立两个变量间的线性关系模型，用于预测和解释变量间的关系，同时可以评估模型的拟合优度和预测变量的显著性。

【统计结果】
回归方程：{y_col} = {intercept:.4f} + {slope:.4f} × {x_col}
- 截距（a）= {intercept:.4f}：当{x_col} = 0时，{y_col}的预测值
- 斜率（b）= {slope:.4f}：{x_col}每增加1个单位，{y_col}平均{'增加' if slope > 0 else '减少'} {abs(slope):.4f}个单位
- 决定系数 R² = {r_squared:.4f}：模型解释了{y_col}总变异的{r_squared*100:.1f}%
- 斜率检验：p值 = {p_display}（显著性水平 α = {alpha_val}）

在 α = {alpha_val} 水平下，{x_col}对{y_col}{'具有' if p_val < alpha_val else '不具有'}统计学意义的预测作用（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结果解释】
R² = {r_squared:.4f} 表示{x_col}能够解释{y_col}总变异的{r_squared*100:.1f}%，{'模型拟合' + ('较好' if r_squared >= 0.5 else '一般' if r_squared >= 0.3 else '较差') + '。' if p_val < alpha_val else ''}

【结论】
{x_col}对{y_col}{'具有' if p_val < alpha_val else '不具有'}统计学意义的预测作用。
{'回归模型具有统计学意义，' + x_col + '能够显著预测' + y_col + '的变化。' if p_val < alpha_val else '回归模型无统计学意义，' + x_col + '不能有效预测' + y_col + '的变化。'}"""
                    
                else:
                    summary_text = f"""【数据描述】
本研究进行了{result['method_name']}统计分析。

【统计结果】
检验统计量 = {result['stat']:.4f}，p值 = {p_display}（显著性水平 α = {alpha_val}）。
在 α = {alpha_val} 水平下，{'差异具有' if p_val < alpha_val else '差异无'}统计学意义（p {'<' if p_val < alpha_val else '≥'} {alpha_val}）。

【结论】
{'结果具有统计学意义。' if p_val < alpha_val else '结果无统计学意义。'}"""
                
                st.text_area(
                    "📋 结果摘要（可复制）",
                    summary_text,
                    height=250,
                    key="summary_text",
                    help="详细的结果摘要，包含数据描述、方法选择理由和统计结果，可直接复制用于报告或论文"
                )
        
        except Exception as e:
            st.error(f"❌ 分析过程出错：{str(e)}")
            import traceback
            with st.expander("错误详情"):
                st.code(traceback.format_exc())
    
    # ==================== 右侧区域（AI 辅导 + Python 代码 Tabs） ====================
    with col_right:
        tab_ai, tab_code = st.tabs(["🤖 AI 辅导", "🐍 Python 代码"])
        
        # Tab 1: AI 辅导
        with tab_ai:
            st.caption("🎓 Shawn · InSynBio")
            
            # 检查 Ollama 连接状态（仅在首次加载时）
            if 'ollama_checked' not in st.session_state:
                try:
                    from ollama_client import get_ollama_url
                    ollama_url = get_ollama_url()
                    if ollama_url == 'http://localhost:11434':
                        # 尝试连接本地服务
                        import requests
                        requests.get(f"{ollama_url}/api/tags", timeout=2)
                        st.session_state.ollama_available = True
                    else:
                        # 远程服务，假设可用（实际会在使用时检测）
                        st.session_state.ollama_available = True
                except:
                    st.session_state.ollama_available = False
                st.session_state.ollama_checked = True
            
            # 如果 Ollama 不可用，显示提示
            if not st.session_state.get('ollama_available', True):
                st.info("""
                **InSynBio 正在建设制作中**
                
                AI 功能正在开发中，敬请期待！
                """)
            
            # 对话历史区域
            chat_container = st.container(height=300)
            with chat_container:
                if st.session_state.chat_history:
                    for msg in st.session_state.chat_history[-5:]:  # 只显示最近5条
                        if msg['role'] == 'user':
                            st.markdown(f"**👤 用户：** {msg['content']}")
                        else:
                            st.markdown(f"**🤖 AI：** {msg['content']}")
                        st.divider()
                else:
                    if st.session_state.get('ollama_available', True):
                        st.info("👋 你好！我是统计辅导助手，可以回答统计分析相关问题。")
                    else:
                        st.info("👋 InSynBio 正在建设制作中，AI 功能敬请期待！")
            
            # 用户输入区
            ollama_available = st.session_state.get('ollama_available', True)
            user_input = st.text_area(
                "输入您的问题",
                placeholder="例如：这个 t 检验的结果如何解释？" if ollama_available else "AI 功能暂时不可用，请先配置远程 Ollama 服务器",
                height=80,
                key="user_input_ai",
                disabled=not ollama_available
            )
            
            col_send, col_clear = st.columns([2, 1])
            with col_send:
                if st.button("📤 发送", type="primary", use_container_width=True, key="send_ai", disabled=not ollama_available):
                    if user_input.strip():
                        # 添加到对话历史
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': user_input
                        })
                        
                        # 构建上下文
                        context = f"当前统计任务：{st.session_state.current_task}\n"
                        if st.session_state.current_results:
                            result = st.session_state.current_results
                            context += f"统计方法：{result['method_name']}\n"
                            context += f"检验统计量：{result['stat']:.4f}\n"
                            context += f"p 值：{result['p_value']:.4e}\n"
                            context += f"解释：{result['explanation_zh']}\n"
                        
                        # 使用 spinner 显示加载状态
                        with st.spinner("🤖 AI 正在思考中，请稍候..."):
                            try:
                                full_prompt = f"{context}\n\n用户问题：{user_input}"
                                ai_response = ask_model(full_prompt, max_retries=2, timeout=120)
                                
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': ai_response
                                })
                                
                                st.rerun()
                            except TimeoutError as e:
                                friendly_msg = "**InSynBio 正在建设制作中**\n\nAI 功能正在开发中，敬请期待！"
                                st.info(friendly_msg)
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': friendly_msg
                                })
                                st.rerun()
                            except ConnectionError as e:
                                friendly_msg = "**InSynBio 正在建设制作中**\n\nAI 功能正在开发中，敬请期待！"
                                st.info(friendly_msg)
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': friendly_msg
                                })
                                st.rerun()
                            except Exception as e:
                                # 检查是否是连接相关错误
                                error_str = str(e).lower()
                                if 'connection' in error_str or '连接' in error_str or 'ollama' in error_str:
                                    friendly_msg = "**InSynBio 正在建设制作中**\n\nAI 功能正在开发中，敬请期待！"
                                    st.info(friendly_msg)
                                    st.session_state.chat_history.append({
                                        'role': 'assistant',
                                        'content': friendly_msg
                                    })
                                else:
                                    error_msg = f"❌ AI 调用失败：{str(e)}\n\n请稍后重试，或检查 Ollama 服务状态。"
                                    st.error(error_msg)
                                    st.session_state.chat_history.append({
                                        'role': 'assistant',
                                        'content': error_msg
                                    })
                                st.rerun()
            
            with col_clear:
                if st.button("🗑️ 清空", use_container_width=True, key="clear_ai"):
                    st.session_state.chat_history = []
                    st.rerun()
        
        # Tab 2: Python 代码
        with tab_code:
            st.caption("当前分析的 Python 代码示例")
            
            # 根据当前任务生成 Python 代码
            if st.session_state.current_task and st.session_state.current_results:
                task = st.session_state.current_task
                result = st.session_state.current_results
                params = st.session_state.current_params
                
                python_code = "# 读取数据\n"
                python_code += "import pandas as pd\n"
                python_code += "import numpy as np\n"
                python_code += "from scipy import stats\n"
                python_code += "import matplotlib.pyplot as plt\n"
                python_code += "import seaborn as sns\n\n"
                python_code += f"# 读取 CSV 文件\n"
                python_code += f"df = pd.read_csv('your_data.csv')\n\n"
                
                if task == "两组比较（t 检验 / Mann–Whitney）":
                    value_col = params.get('value_col', 'value')
                    group_col = params.get('group_col', 'group')
                    alpha = params.get('alpha', 0.05)
                    
                    python_code += f"# 两组比较\n"
                    python_code += f"group1 = df[df['{group_col}'] == df['{group_col}'].unique()[0]]['{value_col}'].dropna()\n"
                    python_code += f"group2 = df[df['{group_col}'] == df['{group_col}'].unique()[1]]['{value_col}'].dropna()\n\n"
                    python_code += f"# 正态性检验\n"
                    python_code += f"from scipy.stats import shapiro, levene\n"
                    python_code += f"_, p_norm1 = shapiro(group1)\n"
                    python_code += f"_, p_norm2 = shapiro(group2)\n"
                    python_code += f"_, p_var = levene(group1, group2)\n\n"
                    python_code += f"# 选择检验方法\n"
                    python_code += f"if p_norm1 > 0.05 and p_norm2 > 0.05 and p_var > 0.05:\n"
                    python_code += f"    stat, p_value = stats.ttest_ind(group1, group2, equal_var=True)\n"
                    python_code += f"    method = '独立样本 t 检验'\n"
                    python_code += f"else:\n"
                    python_code += f"    stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')\n"
                    python_code += f"    method = 'Mann-Whitney U 检验'\n\n"
                    python_code += f"print(f'方法: {{method}}')\n"
                    python_code += f"print(f'统计量: {{stat:.4f}}, p 值: {{p_value:.4f}}')\n\n"
                    python_code += f"# 绘图\n"
                    python_code += f"fig, axes = plt.subplots(1, 2, figsize=(10, 4))\n"
                    python_code += f"axes[0].boxplot([group1, group2], labels=df['{group_col}'].unique())\n"
                    python_code += f"sns.violinplot(data=df, x='{group_col}', y='{value_col}', ax=axes[1])\n"
                    python_code += f"plt.tight_layout()\n"
                    python_code += f"plt.show()\n"
                    
                elif task == "多组比较（单因素 ANOVA）":
                    value_col = params.get('value_col', 'value')
                    group_col = params.get('group_col', 'group')
                    
                    python_code += f"# 单因素方差分析\n"
                    python_code += f"groups = df['{group_col}'].unique()\n"
                    python_code += f"group_data = [df[df['{group_col}'] == g]['{value_col}'].dropna() for g in groups]\n\n"
                    python_code += f"f_stat, p_value = stats.f_oneway(*group_data)\n\n"
                    python_code += f"print(f'F 统计量: {{f_stat:.4f}}, p 值: {{p_value:.4f}}')\n\n"
                    python_code += f"# 绘图\n"
                    python_code += f"fig, axes = plt.subplots(1, 2, figsize=(10, 4))\n"
                    python_code += f"axes[0].boxplot(group_data, labels=groups)\n"
                    python_code += f"sns.violinplot(data=df, x='{group_col}', y='{value_col}', ax=axes[1])\n"
                    python_code += f"plt.tight_layout()\n"
                    python_code += f"plt.show()\n"
                    
                elif task == "相关性分析（Pearson / Spearman）":
                    col_x = params.get('col_x', 'x')
                    col_y = params.get('col_y', 'y')
                    method = params.get('method', 'auto')
                    
                    python_code += f"# 相关性分析\n"
                    python_code += f"x = df['{col_x}'].dropna()\n"
                    python_code += f"y = df['{col_y}'].dropna()\n\n"
                    if method == 'auto' or method == 'pearson':
                        python_code += f"stat, p_value = stats.pearsonr(x, y)\n"
                        python_code += f"method_name = 'Pearson 相关系数'\n"
                    else:
                        python_code += f"stat, p_value = stats.spearmanr(x, y)\n"
                        python_code += f"method_name = 'Spearman 等级相关系数'\n"
                    python_code += f"print(f'方法: {{method_name}}')\n"
                    python_code += f"print(f'相关系数: {{stat:.4f}}, p 值: {{p_value:.4f}}')\n\n"
                    python_code += f"# 绘图\n"
                    python_code += f"fig, ax = plt.subplots(figsize=(7, 5))\n"
                    python_code += f"ax.scatter(x, y, alpha=0.6)\n"
                    python_code += f"z = np.polyfit(x, y, 1)\n"
                    python_code += f"p = np.poly1d(z)\n"
                    python_code += f"ax.plot(x, p(x), 'r--', alpha=0.8, label='趋势线')\n"
                    python_code += f"ax.set_xlabel('{col_x}')\n"
                    python_code += f"ax.set_ylabel('{col_y}')\n"
                    python_code += f"ax.legend()\n"
                    python_code += f"plt.show()\n"
                    
                elif task == "简单线性回归":
                    x_col = params.get('x_col', 'x')
                    y_col = params.get('y_col', 'y')
                    
                    python_code += f"# 简单线性回归\n"
                    python_code += f"import statsmodels.api as sm\n\n"
                    python_code += f"x = df['{x_col}']\n"
                    python_code += f"y = df['{y_col}']\n"
                    python_code += f"X = sm.add_constant(x)\n"
                    python_code += f"model = sm.OLS(y, X).fit()\n\n"
                    python_code += f"print(model.summary())\n\n"
                    python_code += f"# 绘图\n"
                    python_code += f"fig, ax = plt.subplots(figsize=(7, 5))\n"
                    python_code += f"ax.scatter(x, y, alpha=0.6, label='数据点')\n"
                    python_code += f"x_line = np.linspace(x.min(), x.max(), 100)\n"
                    python_code += f"y_line = model.params['{x_col}'] * x_line + model.params['const']\n"
                    python_code += f"ax.plot(x_line, y_line, 'r-', linewidth=2, label='回归线')\n"
                    python_code += f"ax.set_xlabel('{x_col}')\n"
                    python_code += f"ax.set_ylabel('{y_col}')\n"
                    python_code += f"ax.legend()\n"
                    python_code += f"plt.show()\n"
                
                st.code(python_code, language="python")
            else:
                st.info("👆 请先执行分析以生成代码")

else:
    # 未上传数据或未选择任务时的提示
    st.info("👈 请在左侧栏上传 CSV 文件并选择统计任务")
