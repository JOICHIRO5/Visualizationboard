import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ダッシュボードアプリ", layout="wide")
st.title("Visualizationボード")

uploaded_file = st.file_uploader("CSVまたはExcelファイルをアップロード", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    for col in df.columns:
        if "date" in col.lower() or "日" in col:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    # ======== タブ構成 ========
    tab1, tab2, tab3 = st.tabs(["📄 データ確認", "🔎 フィルター設定", "📈 グラフ可視化"])

    # ======== データ確認 ========
    with tab1:
        st.dataframe(df)

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            st.markdown("#### 📊 統計を表示する列を選択")
            selected_stat_col = st.selectbox("列を選択して統計を確認", options=numeric_cols)
            if selected_stat_col:
                col_data = df[selected_stat_col]
                st.write(f"✅ **{selected_stat_col} の統計情報**")
                st.metric("合計", f"{col_data.sum():,.2f}")
                st.metric("平均", f"{col_data.mean():,.2f}")
                st.metric("最小", f"{col_data.min():,.2f}")
                st.metric("最大", f"{col_data.max():,.2f}")

    # ======== フィルター設定 ========
    with tab2:
        st.markdown("#### 条件を選んでデータを絞り込みましょう")
        filtered_df = df.copy()

        for col in df.columns:
            col_data = df[col]
            if pd.api.types.is_datetime64_any_dtype(col_data):
                min_val, max_val = col_data.min(), col_data.max()
                from_date, to_date = st.date_input(f"📅 {col} の期間", [min_val.date(), max_val.date()])
                filtered_df = filtered_df[(col_data >= pd.to_datetime(from_date)) & (col_data <= pd.to_datetime(to_date))]

            elif pd.api.types.is_numeric_dtype(col_data):
                min_val, max_val = float(col_data.min()), float(col_data.max())
                slider = st.slider(f"🔢 {col} の範囲", min_val, max_val, (min_val, max_val))
                filtered_df = filtered_df[(col_data >= slider[0]) & (col_data <= slider[1])]

            elif pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
                unique_vals = col_data.dropna().unique().tolist()
                if len(unique_vals) <= 50:
                    selected = st.multiselect(f"🧩 {col} の選択", unique_vals, default=unique_vals)
                    filtered_df = filtered_df[filtered_df[col].isin(selected)]

    # ======== グラフ可視化 ========
    with tab3:
        st.markdown("#### 絞り込み後のデータでグラフを表示")

        x_options = [""] + list(filtered_df.columns)
        x_col = st.selectbox("X軸を選択", options=x_options)

        y_options = [""] + list(filtered_df.select_dtypes(include=["number", "datetime64[ns]", "object", "category"]).columns)
        y_col = st.selectbox("Y軸を選択", options=y_options)

        color_options = [""] + list(filtered_df.select_dtypes(include=["object", "category"]).columns)
        color_col = st.selectbox("カテゴリ（色分け）を選択（任意）", options=color_options)

        chart_type = st.selectbox("グラフの種類を選択", options=["ヒストグラム", "棒グラフ", "折れ線グラフ", "散布図", "箱ひげ図"])

        fig = None
        kwargs = {}
        if x_col:
            kwargs["x"] = x_col
        if y_col:
            kwargs["y"] = y_col
        if color_col:
            kwargs["color"] = color_col

        if chart_type == "ヒストグラム":
            if "x" in kwargs:
                fig = px.histogram(filtered_df, **kwargs)
            else:
                st.warning("ヒストグラムはX軸を選択してください。")
        elif chart_type == "棒グラフ":
            if "x" in kwargs and "y" in kwargs:
                fig = px.bar(filtered_df, **kwargs)
            else:
                st.warning("棒グラフはX軸とY軸の両方を選択してください。")
        elif chart_type == "折れ線グラフ":
            if "x" in kwargs and "y" in kwargs:
                fig = px.line(filtered_df, **kwargs)
            else:
                st.warning("折れ線グラフはX軸とY軸の両方を選択してください。")
        elif chart_type == "散布図":
            if "x" in kwargs and "y" in kwargs:
                fig = px.scatter(filtered_df, **kwargs)
            else:
                st.warning("散布図はX軸とY軸の両方を選択してください。")
        elif chart_type == "箱ひげ図":
            if "x" in kwargs and "y" in kwargs:
                fig = px.box(filtered_df, **kwargs)
            else:
                st.warning("箱ひげ図はX軸とY軸の両方を選択してください。")

        if fig:
            st.plotly_chart(fig, use_container_width=True)