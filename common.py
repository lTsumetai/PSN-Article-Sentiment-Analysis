import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "dashboard_data"

SENTIMENT_ORDER = ["negative", "neutral", "positive"]
SENTIMENT_COLORS = {"negative": "#C44E52", "neutral": "#8C8C8C", "positive": "#55A868"}
MIN_TOPIC_N = 10    # same setting as the notebook


# ------------------------------------------------------- fix the map shapes
def ring_is_clockwise(ring):
    # shoelace formula: a positive total means the points go clockwise
    total = 0
    for i in range(len(ring) - 1):
        total += (ring[i + 1][0] - ring[i][0]) * (ring[i + 1][1] + ring[i][1])
    return total > 0


def fix_winding(geojson):
    """Plotly needs the outer edge of each shape to go clockwise (holes the other way).
    Some provinces in this GeoJSON go the wrong way, which makes Plotly colour the whole
    map instead of the province. This turns the wrong rings around."""
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


# ---------------------------------------------------------------- load data
@st.cache_data
def load_data():
    d = {}
    d["articles"] = pd.read_csv(DATA / "articles.csv", parse_dates=["date", "month"])
    d["topics"] = pd.read_csv(DATA / "topics.csv")
    d["groups"] = pd.read_csv(DATA / "groups.csv")
    d["trends"] = pd.read_csv(DATA / "trends.csv", parse_dates=["month"])
    d["region"] = pd.read_csv(DATA / "region.csv")
    d["event_table"] = pd.read_csv(DATA / "event_table.csv")
    d["event_drivers"] = pd.read_csv(DATA / "event_drivers.csv")
    with open(DATA / "indonesia_provinces.geojson", encoding="utf-8") as f:
        d["geojson"] = fix_winding(json.load(f))
    return d


def group_summary(articles, groups, trends):
    """One row per satellite / topic group: when searches peaked and how much news there was."""
    rows = []
    for _, g in groups.iterrows():
        score = trends[g["key"] + "_interest"]
        peak_month = trends.loc[score.idxmax(), "month"]
        group_articles = articles[articles["group"] == g["group"]]
        rows.append({
            "Topic group": g["group"],
            "Keyword": g["keyword"],
            "key": g["key"],
            "Peak month": peak_month,
            "Months with searches": int((score > 0).sum()),
            "Months in total": len(score),
            "Articles in group": len(group_articles),
            "Articles in peak month": int((group_articles["month"] == peak_month).sum()),
        })
    return pd.DataFrame(rows)
