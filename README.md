# Nepal Air Quality Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://airqualitynp.streamlit.app/)

Interactive dashboard for visualizing air quality data across Nepal (2016–2025).  
**Live**: [airqualitynp.streamlit.app](https://airqualitynp.streamlit.app/)

## Data

The dataset contains **~95,000 measurements** from **31 monitoring stations** across Nepal, covering four pollutants:

- **PM1** — Particulate Matter < 1 µm
- **PM2.5** — Particulate Matter < 2.5 µm
- **PM10** — Particulate Matter < 10 µm
- **TSP** — Total Suspended Particulates

## Features

- **Overview** — Dataset statistics, records per pollutant/year, top stations
- **Trends** — Time series (monthly/yearly), seasonality analysis, year-over-year comparison
- **Stations** — Station ranking, multi-station time series comparison, pollutant correlation matrix
- **Analysis** — PM2.5 distribution, monthly heatmap, YoY change, pollutant composition pie charts
- **Data** — Filterable raw data viewer

## Tech Stack

- [Streamlit](https://streamlit.io/) — Web dashboard framework
- [Plotly](https://plotly.com/) — Interactive visualizations
- [Pandas](https://pandas.pydata.org/) — Data processing
- [Matplotlib](https://matplotlib.org/) / [Seaborn](https://seaborn.pydata.org/) — Static plots

## Local Development

```bash
git clone https://github.com/surazgyawali/nepal-aqi-dashboard.git
cd nepal-aqi-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Live at [**airqualitynp.streamlit.app**](https://airqualitynp.streamlit.app/).  
Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud) — auto-deploys on push to `main`.

## License

MIT
