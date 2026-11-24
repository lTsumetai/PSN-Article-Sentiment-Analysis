import json
from pathlib import Path

import pandas as pd
import streamlit as st

data = Path(__file__).parent / "dashboard_data"

sentiment_order = ["negative", "neutral", "positive"]
sentiment_colors = {"negative": "#C44E52", "neutral": "#8C8C8C", "positive": "#55A868"}
min_topic_n = 10

# map shapes
def ring_is_clockwise(ring):
    total = 0
    for i in range(len(ring) - 1):
        total += (ring[i + 1][0] - ring[i][0]) * (ring[i+1][1] + ring[i][1])
    return total > 0

def fix_winding(geojson):
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"]]
        else:
            polygons = geometry["coordinates"]

        for polygon in polygons:
            for number, ring in enumerate(polygon):
                is_outer = number == 0
                if ring_is_clockwise(ring) != is_outer:
                    ring.reverse()

    return geojson

# Load Data
@st.cache_data
def load_data():
    d = {}
    d["articles"] = pd.read_csv(data / "articles.csv", parse_dates=["date", "month"])
    d["topics"] = pd.read_csv(data / "topics.csv")
    d["groups"] = pd.read_csv(data / "groups.csv")
    d["trends"] = pd.read_csv(data / "trends.csv", parse_dates=["month"])
    d["region"] = pd.read_csv(data / "region.csv")
    d["event_table"] = pd.read_csv(data / "event_table.csv")
    d["event_drivers"] = pd.read_csv(data / "event_drivers.csv")
    with open(data / "indonesia_provinces.geojson", encoding="utf-8") as f:
        d["geojson"] = fix_winding(json.load(f))
    return d

def group_summary(articles, groups, trends):
    rows = []
    for _, g in groups.iterrows():
        score = trends[g["key"] + "_interest"]
        peak_month = trends.loc[score.idxmax(), "month"]
        group_articles = articles[articles["group"] == g["group"]]
        rows.append({
            "Topic group": g["group"],
            "keyword": g["keyword"],
            "key": g["key"],
            "Peak month": peak_month,
            "months with searches": int((score > 0).sum()),
            "Articles in group": len(group_articles),
            "Articles in peak month": int((group_articles["month"] == peak_month).sum())
        })
    return pd.DataFrame(rows)

