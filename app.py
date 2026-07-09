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

st.markdown("""
<style>
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.7rem;
            padding: 0.4rem 0.3rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
        }
        h1 {
            font-size: 1.4rem !important;
        }
        .stSubheader {
            font-size: 1rem !important;
        }
        .stMetric label {
            font-size: 0.7rem !important;
        }
        .stMetric div[data-testid="metric-value"] {
            font-size: 1.1rem !important;
        }
        div[data-testid="column"] {
            min-width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📊 Overview", "📈 Trends", "🗺️ Stations", "🔬 Analysis", "🏥 WHO Guidelines", "📋 Data"]
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

    st.subheader("Explore by Year")
    st.caption("Drag the slider to see station rankings for each year.")
    yr_pollutant = st.selectbox(
        "Select Pollutant", df["pollutant"].unique(), key="yr_pollutant",
        label_visibility="collapsed",
    )
    valid_years = sorted(df[df["pollutant"] == yr_pollutant]["year"].unique())
    selected_year = st.select_slider(
        "Year",
        options=valid_years,
        value=valid_years[-1] if valid_years else 2020,
    )
    yr_data = df[(df["pollutant"] == yr_pollutant) & (df["year"] == selected_year)]
    yr_avg = yr_data.groupby("station")["value"].mean().reset_index()
    yr_avg = yr_avg.sort_values("value", ascending=True)

    if not yr_avg.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(
                yr_avg.tail(15),
                x="value",
                y="station",
                orientation="h",
                color="value",
                text=yr_avg["value"].round(1).tail(15),
                color_continuous_scale="YlOrRd",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=450,
                xaxis_title=f"{yr_pollutant} (µg/m³)",
                yaxis_title=None,
                margin=dict(l=0, r=30, t=10, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            best = yr_avg.iloc[0]
            worst = yr_avg.iloc[-1]
            st.metric("Cleanest Station", best["station"], f"{best['value']:.1f} µg/m³")
            st.metric("Most Polluted", worst["station"], f"{worst['value']:.1f} µg/m³")
            mid = len(yr_avg) // 2
            st.metric("Median Station", yr_avg.iloc[mid]["station"], f"{yr_avg.iloc[mid]['value']:.1f} µg/m³")
            st.metric("Stations Reported", yr_data["station"].nunique())
    else:
        st.info(f"No {yr_pollutant} data recorded for {selected_year}.")

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
    st.header("WHO Air Quality Guideline Compliance")

    WHO_LIMITS = {
        "PM2.5": {"annual": 5, "daily": 15, "unit": "µg/m³"},
        "PM10": {"annual": 15, "daily": 45, "unit": "µg/m³"},
    }

    who_pollutant = st.selectbox(
        "Select Pollutant",
        [p for p in ["PM2.5", "PM10"]],
        key="who_pollutant",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.info(f"**WHO 2021 Guideline — {who_pollutant}**\n\n"
                f"- Annual mean: **{WHO_LIMITS[who_pollutant]['annual']}** µg/m³\n"
                f"- 24-hour mean: **{WHO_LIMITS[who_pollutant]['daily']}** µg/m³")
    with col2:
        st.info("**Health implications:**\n\n"
                "Exceeding these limits increases risk of cardiovascular and respiratory diseases. "
                "No safe threshold has been identified — reducing exposure always improves health.")

    who_data = df[df["pollutant"] == who_pollutant].copy()
    who_data["date"] = pd.to_datetime(who_data["date"])

    daily_limit = WHO_LIMITS[who_pollutant]["daily"]
    annual_limit = WHO_LIMITS[who_pollutant]["annual"]

    who_data["exceeds_daily"] = who_data["value"] > daily_limit

    daily_exceed = (
        who_data.groupby(["station", "year"])
        .agg(total_days=("value", "count"), exceed_days=("exceeds_daily", "sum"))
        .reset_index()
    )
    daily_exceed["exceed_rate"] = (daily_exceed["exceed_days"] / daily_exceed["total_days"] * 100).round(1)

    annual_avg = who_data.groupby(["station", "year"])["value"].mean().reset_index()
    annual_avg["exceeds_annual"] = annual_avg["value"] > annual_limit

    st.subheader("Daily Exceedance Rate by Station")
    st.caption(f"% of days where {who_pollutant} exceeded the 24h guideline ({daily_limit} µg/m³)")

    exceed_year = st.select_slider(
        "Year", options=sorted(daily_exceed["year"].unique()),
        value=sorted(daily_exceed["year"].unique())[-1],
        key="exceed_year",
    )
    exceed_yr = daily_exceed[daily_exceed["year"] == exceed_year].sort_values("exceed_rate")
    if not exceed_yr.empty:
        fig = px.bar(
            exceed_yr,
            x="exceed_rate",
            y="station",
            orientation="h",
            color="exceed_rate",
            text=exceed_yr["exceed_rate"].astype(str) + "%",
            color_continuous_scale="RdYlGn_r",
            range_color=[0, 100],
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=max(350, len(exceed_yr) * 20),
            xaxis_title="Days exceeding 24h limit (%)",
            yaxis_title=None,
            xaxis=dict(range=[0, 105]),
            margin=dict(l=0, r=30, t=10, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Annual Average vs WHO Annual Guideline")
    st.caption(f"Red line shows the WHO annual limit ({annual_limit} µg/m³)")

    ann_year = st.select_slider(
        "Year", options=sorted(annual_avg["year"].unique()),
        value=sorted(annual_avg["year"].unique())[-1],
        key="ann_year",
    )
    ann_yr = annual_avg[annual_avg["year"] == ann_year].sort_values("value", ascending=True)
    if not ann_yr.empty:
        ann_yr["color"] = ann_yr["value"].apply(
            lambda v: "red" if v > annual_limit else "green"
        )
        fig = px.bar(
            ann_yr,
            x="value",
            y="station",
            orientation="h",
            color="color",
            text=ann_yr["value"].round(1),
        )
        fig.add_vline(x=annual_limit, line_dash="dash", line_color="red",
                      annotation_text=f"WHO limit: {annual_limit} µg/m³")
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=max(350, len(ann_yr) * 20),
            xaxis_title=f"{who_pollutant} (µg/m³)",
            yaxis_title=None,
            showlegend=False,
            margin=dict(l=0, r=30, t=10, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Exceedance Trend Over Years")
    exceed_trend = daily_exceed.groupby("year")["exceed_rate"].mean().reset_index()
    fig = px.line(
        exceed_trend,
        x="year",
        y="exceed_rate",
        markers=True,
        text=exceed_trend["exceed_rate"].round(1),
    )
    fig.update_traces(
        textposition="top center",
        textfont=dict(size=11),
    )
    fig.update_layout(
        height=350,
        yaxis_title="Days exceeding 24h limit (%)",
        xaxis=dict(tickmode="linear", dtick=1),
        margin=dict(l=20, r=20, t=10, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Yearly Compliance Summary")
    summary = (
        annual_avg.groupby("year")
        .agg(
            total_stations=("station", "count"),
            compliant=("exceeds_annual", lambda x: (~x).sum()),
        )
        .reset_index()
    )
    summary["compliance_rate"] = (summary["compliant"] / summary["total_stations"] * 100).round(1)
    summary.columns = ["Year", "Total Stations", "Compliant with Annual Limit", "Compliance Rate (%)"]
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.divider()
    st.header("Health Impact Estimates")

    if who_pollutant != "PM2.5":
        st.info("Health risk categories are defined for PM₂.₅. Switch to PM2.5 to see this section.")
    else:
        RISK_BANDS = [
            (0, 5, "Good", "#00E400"),
            (5, 15, "Moderate", "#FFFF00"),
            (15, 25, "Unhealthy (Sensitive)", "#FF7E00"),
            (25, 50, "Unhealthy", "#FF0000"),
            (50, 100, "Very Unhealthy", "#8F3F97"),
            (100, float("inf"), "Hazardous", "#7E0023"),
        ]

        def risk_label(val):
            for lo, hi, label, _ in RISK_BANDS:
                if lo <= val < hi:
                    return label
            return "Unknown"

        def risk_color(val):
            for lo, hi, _, color in RISK_BANDS:
                if lo <= val < hi:
                    return color
            return "#999999"

        hi_data = who_data.copy()
        hi_data["risk_label"] = hi_data["value"].apply(risk_label)
        hi_data["risk_color"] = hi_data["value"].apply(risk_color)

        st.markdown("""
        Long-term exposure to PM₂.₅ is linked to cardiovascular and respiratory diseases, lung cancer, and premature mortality.
        Below is the breakdown of daily air quality by **health risk category**.
        """)

        col1, col2 = st.columns(2)
        with col1:
            hi_station = st.selectbox("Station", sorted(hi_data["station"].unique()), key="hi_station")
        with col2:
            hi_year = st.selectbox("Year", sorted(hi_data["year"].unique(), reverse=True), key="hi_year")

        hi_subset = hi_data[(hi_data["station"] == hi_station) & (hi_data["year"] == hi_year)]
        if not hi_subset.empty:
            risk_dist = hi_subset["risk_label"].value_counts().reset_index()
            risk_dist.columns = ["risk", "days"]
            risk_order = [b[2] for b in RISK_BANDS]
            risk_dist["risk"] = pd.Categorical(risk_dist["risk"], categories=risk_order, ordered=True)
            risk_dist = risk_dist.sort_values("risk").dropna()

            color_map = {b[2]: b[3] for b in RISK_BANDS}

            col_a, col_b = st.columns([1.5, 1])
            with col_a:
                fig = px.bar(
                    risk_dist,
                    x="days",
                    y="risk",
                    orientation="h",
                    color="risk",
                    color_discrete_map=color_map,
                    text="days",
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    height=300,
                    xaxis_title="Number of days",
                    yaxis_title=None,
                    showlegend=False,
                    margin=dict(l=0, r=30, t=10, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                avg_pm = hi_subset["value"].mean()
                worst_pm = hi_subset["value"].max()
                unhealth_days = hi_subset[hi_subset["risk_label"].isin(
                    ["Unhealthy", "Very Unhealthy", "Hazardous"]
                )].shape[0]
                pct_unhealth = unhealth_days / len(hi_subset) * 100

                st.metric("Average PM₂.₅", f"{avg_pm:.1f} µg/m³")
                st.metric("Peak PM₂.₅", f"{worst_pm:.1f} µg/m³")
                st.metric("Unhealthy+ Days", f"{unhealth_days} ({pct_unhealth:.0f}%)")

        st.subheader("Risk Category Heatmap Across Stations")
        risk_pivot = hi_data.groupby(["station", "year"])["value"].mean().reset_index()
        risk_pivot["risk_label"] = risk_pivot["value"].apply(risk_label)

        label_to_code = {b[2]: i for i, b in enumerate(RISK_BANDS)}
        risk_pivot["risk_code"] = risk_pivot["risk_label"].map(label_to_code)

        risk_heat = risk_pivot.pivot_table(
            index="station", columns="year", values="risk_code", aggfunc="first"
        )

        fig = px.imshow(
            risk_heat,
            text_auto=False,
            color_continuous_scale=[b[3] for b in RISK_BANDS],
            aspect="auto",
            height=max(400, len(risk_heat) * 15),
            labels=dict(x="Year", y="Station", color="Risk Level"),
        )
        fig.update_layout(margin=dict(l=0, r=20, t=10, b=20))
        st.plotly_chart(fig, use_container_width=True)

        st.caption("Based on annual average PM₂.₅. Colors follow the US EPA AQI health breakpoints.")

with tab6:
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
