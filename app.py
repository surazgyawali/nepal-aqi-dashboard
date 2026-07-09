import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

st.set_page_config(page_title="Nepal AQI Dashboard", layout="wide", page_icon="🌍")

DATA_PATH = Path("master_long.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

st.title("🌍 Nepal Air Quality Dashboard")
st.markdown(
    "Comprehensive analysis of air quality data across Nepal (2016–2025) "
    "covering **{}** stations and **{}** measurements.".format(
        df["station"].nunique(), len(df)
    )
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "📈 Trends", "🗺️ Stations", "🔬 Analysis", "📋 Data"]
)

with tab1:
    st.header("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stations", df["station"].nunique())
    col2.metric("Pollutants", df["pollutant"].nunique())
    col3.metric("Date Range", f"{df['date'].dt.year.min()}–{df['date'].dt.year.max()}")
    col4.metric("Total Records", f"{len(df):,}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Records per Pollutant")
        poll_counts = df["pollutant"].value_counts().reset_index()
        poll_counts.columns = ["pollutant", "count"]
        fig = px.bar(
            poll_counts,
            x="pollutant",
            y="count",
            color="pollutant",
            text="count",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Records per Year")
        year_counts = df["year"].value_counts().sort_index().reset_index()
        year_counts.columns = ["year", "count"]
        fig = px.bar(
            year_counts,
            x="year",
            y="count",
            color="year",
            text="count",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Stations by Data Availability")
    station_counts = df["station"].value_counts().head(10).reset_index()
    station_counts.columns = ["station", "count"]
    fig = px.bar(
        station_counts,
        x="count",
        y="station",
        orientation="h",
        color="count",
        text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=400, xaxis_title="Number of Records")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Pollution Trends Over Time")

    pollutant_choice = st.selectbox("Select Pollutant", df["pollutant"].unique(), key="trend_pollutant")
    agg_level = st.radio("Aggregation Level", ["Monthly", "Yearly"], horizontal=True, key="trend_agg")

    filtered = df[df["pollutant"] == pollutant_choice]

    if agg_level == "Monthly":
        trend = filtered.groupby(["year", "month"])["value"].mean().reset_index()
        trend["period"] = pd.to_datetime(
            trend["year"].astype(str) + "-" + trend["month"].astype(str) + "-01"
        )
        trend = trend.sort_values("period")
        x_col = "period"
        x_title = "Date"
    else:
        trend = filtered.groupby("year")["value"].mean().reset_index()
        x_col = "year"
        x_title = "Year"

    fig = px.line(
        trend,
        x=x_col,
        y="value",
        markers=True,
        title=f"{pollutant_choice} — {agg_level} Average Trend",
    )
    fig.update_layout(height=450, xaxis_title=x_title, yaxis_title=f"{pollutant_choice} (µg/m³)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Seasonality — Monthly Averages")
    monthly = filtered.groupby("month")["value"].mean().reset_index()
    fig = px.bar(
        monthly,
        x="month",
        y="value",
        color="value",
        text=monthly["value"].round(1),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=400,
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13))),
        yaxis_title=f"{pollutant_choice} (µg/m³)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Year-over-Year Comparison")
    years = sorted(filtered["year"].unique())
    selected_years = st.multiselect(
        "Select Years", years, default=years[-3:], key="trend_years"
    )
    if selected_years:
        yoy = filtered[filtered["year"].isin(selected_years)]
        monthly_yoy = yoy.groupby(["year", "month"])["value"].mean().reset_index()
        fig = px.line(
            monthly_yoy,
            x="month",
            y="value",
            color="year",
            markers=True,
        )
        fig.update_layout(
            height=450,
            xaxis=dict(tickmode="array", tickvals=list(range(1, 13))),
            yaxis_title=f"{pollutant_choice} (µg/m³)",
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Station Comparison")

    pollutant_s = st.selectbox("Select Pollutant", df["pollutant"].unique(), key="station_pollutant")
    agg_method = st.radio("Aggregation", ["Mean", "Median", "Max"], horizontal=True, key="station_agg")

    agg_map = {"Mean": "mean", "Median": "median", "Max": "max"}
    filtered_s = df[df["pollutant"] == pollutant_s]
    station_avg = (
        filtered_s.groupby("station")["value"]
        .agg(agg_map[agg_method])
        .reset_index()
        .sort_values("value", ascending=False)
    )

    fig = px.bar(
        station_avg,
        x="value",
        y="station",
        orientation="h",
        color="value",
        text=station_avg["value"].round(1),
        title=f"{pollutant_s} {agg_method} by Station",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=max(400, len(station_avg) * 20), xaxis_title=f"{pollutant_s} (µg/m³)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Station Time Series Comparison")
    selected_stations = st.multiselect(
        "Select Stations to Compare",
        sorted(df["station"].unique()),
        default=["Ratnapark", "Pulchowk", "Dhulikhel"],
        key="ts_stations",
    )
    if selected_stations:
        ts_data = filtered_s[filtered_s["station"].isin(selected_stations)]
        ts_monthly = (
            ts_data.groupby(["station", "year", "month"])["value"]
            .mean()
            .reset_index()
        )
        ts_monthly["period"] = pd.to_datetime(
            ts_monthly["year"].astype(str)
            + "-"
            + ts_monthly["month"].astype(str)
            + "-01"
        )
        fig = px.line(
            ts_monthly,
            x="period",
            y="value",
            color="station",
            title=f"{pollutant_s} Monthly Averages by Station",
        )
        fig.update_layout(height=450, yaxis_title=f"{pollutant_s} (µg/m³)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Pollutant Correlation Matrix")
    corr_stations = st.multiselect(
        "Select Stations for Correlation",
        sorted(df["station"].unique()),
        default=["Ratnapark", "Pulchowk", "Dhulikhel"],
        key="corr_stations",
    )
    if corr_stations:
        pivot = df[df["station"].isin(corr_stations)].pivot_table(
            index=["date", "station"],
            columns="pollutant",
            values="value",
        ).reset_index()
        if not pivot.empty:
            corr = pivot.select_dtypes(include=[np.number]).corr()
            fig = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale="RdBu_r",
                aspect="auto",
                title="Pollutant Correlation",
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Deep Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("PM2.5 Distribution by Station")
        pm25 = df[df["pollutant"] == "PM2.5"]
        fig = px.box(
            pm25,
            x="station",
            y="value",
            title="PM2.5 Distribution (Top 15 Stations)",
        )
        fig.update_layout(height=450, xaxis={"categoryorder": "total descending"})
        # limit to 15 stations for readability
        top15 = pm25.groupby("station")["value"].mean().sort_values(ascending=False).head(15).index
        fig.update_xaxes(categoryorder="array", categoryarray=top15.tolist())
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Monthly Heatmap (PM2.5)")
        pm25_monthly = (
            pm25.groupby(["year", "month"])["value"].mean().reset_index()
        )
        pivot_h = pm25_monthly.pivot(index="year", columns="month", values="value")
        fig = px.imshow(
            pivot_h,
            text_auto=".0f",
            color_continuous_scale="YlOrRd",
            aspect="auto",
            labels=dict(x="Month", y="Year", color="PM2.5"),
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Year-over-Year Change (%)")
    pollutant_yoy = st.selectbox(
        "Select Pollutant", df["pollutant"].unique(), key="yoy_pollutant"
    )
    yearly = df[df["pollutant"] == pollutant_yoy].groupby("year")["value"].mean()
    yoy_change = yearly.pct_change() * 100
    yoy_df = yoy_change.reset_index().dropna()
    yoy_df.columns = ["year", "change"]
    yoy_df["color"] = yoy_df["change"].apply(lambda x: "red" if x > 0 else "green")

    fig = px.bar(
        yoy_df,
        x="year",
        y="change",
        color="color",
        text=yoy_df["change"].round(1),
        title=f"{pollutant_yoy} Year-over-Year Change",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis_title="Change (%)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Pollutant Composition by Station")
    station_comp = st.selectbox(
        "Select Station",
        sorted(df["station"].unique()),
        key="comp_station",
    )
    if station_comp:
        comp = df[df["station"] == station_comp].groupby("pollutant")["value"].mean().reset_index()
        fig = px.pie(
            comp,
            names="pollutant",
            values="value",
            title=f"Average Pollutant Composition — {station_comp}",
            hole=0.4,
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.header("Raw Data Viewer")

    col1, col2, col3 = st.columns(3)
    with col1:
        station_filter = st.multiselect(
            "Filter by Station",
            sorted(df["station"].unique()),
            default=[],
            key="data_station",
        )
    with col2:
        pollutant_filter = st.multiselect(
            "Filter by Pollutant",
            sorted(df["pollutant"].unique()),
            default=[],
            key="data_pollutant",
        )
    with col3:
        year_range = st.slider(
            "Year Range",
            int(df["year"].min()),
            int(df["year"].max()),
            (int(df["year"].min()), int(df["year"].max())),
            key="data_year",
        )

    filtered_df = df.copy()
    if station_filter:
        filtered_df = filtered_df[filtered_df["station"].isin(station_filter)]
    if pollutant_filter:
        filtered_df = filtered_df[filtered_df["pollutant"].isin(pollutant_filter)]
    filtered_df = filtered_df[
        (filtered_df["year"] >= year_range[0])
        & (filtered_df["year"] <= year_range[1])
    ]

    st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
