import streamlit as st
import sqlite3
import pandas as pd

# =========================
# 页面配置
# =========================
st.set_page_config(page_title="语言政策检索系统", layout="wide")

# 数据库文件名
DB_FILE = "Immigration Language Policy Documents.db"


# =========================
# 读取数据
# =========================
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM policies", conn)
    conn.close()
    return df


# =========================
# 主页面
# =========================
st.title("🌍 世界典型移民国家移民语言政策检索系统")

try:
    df = load_data()

    # 将空值统一处理，避免 contains 或展示时报错
    df = df.fillna("")

    # =========================
    # 侧边栏检索
    # =========================
    st.sidebar.header("🔍 检索与筛选")

    countries = sorted(df["国别"].unique().tolist()) if "国别" in df.columns else []
    selected_countries = st.sidebar.multiselect("选择国家", countries, default=countries)

    search_term = st.sidebar.text_input("搜索关键词（核心内容 / 核心内容原文 / 政策对象）")

    # =========================
    # 数据过滤
    # =========================
    mask = pd.Series([True] * len(df), index=df.index)

    if "国别" in df.columns and selected_countries:
        mask = mask & df["国别"].isin(selected_countries)

    if search_term:
        content_match = df["核心内容"].str.contains(search_term, case=False, na=False) if "核心内容" in df.columns else False
        original_match = df["核心内容原文"].str.contains(search_term, case=False, na=False) if "核心内容原文" in df.columns else False
        target_match = df["政策对象"].str.contains(search_term, case=False, na=False) if "政策对象" in df.columns else False

        mask = mask & (content_match | original_match | target_match)

    filtered_df = df[mask].copy()

    # =========================
    # 显示检索结果
    # =========================
    st.subheader(f"找到 {len(filtered_df)} 条政策记录")

    if not filtered_df.empty:
        display_df = filtered_df.reset_index(drop=False).rename(columns={"index": "原始编号"})
        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("没有找到符合条件的政策记录。")

    # =========================
    # 详情查看区域
    # =========================
    if not filtered_df.empty:
        st.markdown("---")
        st.subheader("📄 政策详情")

        # 为选择框准备更直观的标签
        option_map = {}
        for idx in filtered_df.index:
            row = filtered_df.loc[idx]

            if "政策名称" in filtered_df.columns and str(row["政策名称"]).strip():
                label = f"{idx} - {row['政策名称']}"
            elif "政策题目" in filtered_df.columns and str(row["政策题目"]).strip():
                label = f"{idx} - {row['政策题目']}"
            else:
                country_part = row["国别"] if "国别" in filtered_df.columns else "未知国家"
                year_part = row["年份/版本"] if "年份/版本" in filtered_df.columns else ""
                label = f"{idx} - {country_part} {year_part}"

            option_map[label] = idx

        selected_label = st.selectbox("选择一条记录查看详细内容", list(option_map.keys()))
        idx = option_map[selected_label]
        record = filtered_df.loc[idx]

        # 标题
        if "政策名称" in filtered_df.columns and str(record["政策名称"]).strip():
            st.markdown(f"### {record['政策名称']}")
        elif "政策题目" in filtered_df.columns and str(record["政策题目"]).strip():
            st.markdown(f"### {record['政策题目']}")
        else:
            st.markdown("### 当前政策记录")

        # 基本信息
        col1, col2 = st.columns(2)

        with col1:
            if "国别" in filtered_df.columns:
                st.markdown(f"**国别：** {record['国别']}")
            if "政策对象" in filtered_df.columns:
                st.markdown(f"**政策对象：** {record['政策对象']}")
            if "出台机构" in filtered_df.columns:
                st.markdown(f"**出台机构：** {record['出台机构']}")

        with col2:
            if "年份/版本" in filtered_df.columns:
                st.markdown(f"**年份/版本：** {record['年份/版本']}")
            if "文本类型" in filtered_df.columns:
                st.markdown(f"**文本类型：** {record['文本类型']}")
            if "政策来源" in filtered_df.columns:
                st.markdown(f"**政策来源：** {record['政策来源']}")

        st.markdown("---")

        # 核心内容
        if "核心内容" in filtered_df.columns:
            st.markdown("### 核心内容")
            core_content = record["核心内容"] if str(record["核心内容"]).strip() else "暂无内容"
            st.write(core_content)

        # 核心内容原文
        if "核心内容原文" in filtered_df.columns:
            st.markdown("### 核心内容原文")
            original_text = record["核心内容原文"] if str(record["核心内容原文"]).strip() else "暂无原文"
            st.info(original_text)

except Exception as e:
    st.error(f"出错啦：{e}")
    st.info("如果提示 'no such table'，请检查数据库中的表名是否确实为 policies。")