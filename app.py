import streamlit as st
import sqlite3
import pandas as pd

# 配置页面
st.set_page_config(page_title="语言政策检索系统", layout="wide")

# 数据库文件名
DB_FILE = "Immigration Language Policy Documents.db"

# 获取数据
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_FILE)
    # 注意：这里的 policy_table 必须是你之前在 DB Browser 导入时起的表名
    df = pd.read_sql("SELECT * FROM policies", conn)
    conn.close()
    return df

st.title("🌍 世界典型移民国家移民语言政策检索系统")

try:
    df = load_data()
    
    # 侧边栏搜索
    st.sidebar.header("🔍 检索与筛选")
    countries = df['国别'].unique().tolist()
    selected_countries = st.sidebar.multiselect("选择国家", countries, default=countries)
    search_term = st.sidebar.text_input("搜索关键词（核心内容/政策对象）")

    # 过滤数据
    mask = df['国别'].isin(selected_countries)
    if search_term:
        mask = mask & (df['核心内容'].str.contains(search_term, case=False, na=False) | 
                       df['政策对象'].str.contains(search_term, case=False, na=False))
    
    filtered_df = df[mask]

    # 显示结果
    st.subheader(f"找到 {len(filtered_df)} 条政策记录")
    st.dataframe(filtered_df, use_container_width=True)

    # 原文详情查看
    if not filtered_df.empty:
        st.markdown("---")
        st.subheader("📄 核心内容原文详情")
        idx = st.selectbox("选择记录编号查看完整原文", filtered_df.index)
        st.info(filtered_df.loc[idx, '核心内容原文'])

except Exception as e:
    st.error(f"出错啦：{e}")
    st.info("如果是 'no such table'，说明你的表名不是 policy_table，请在代码中修改它。")