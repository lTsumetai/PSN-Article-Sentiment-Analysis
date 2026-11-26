import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import group_summary, load_data

data = load_data()
articles = data["articles"]
trends = data["trends"]
groups = data["groups"]
region = data["region"]
geojson = data["geojson"]

keyword_of = dict(zip(groups["key"], groups["keyword"]))
summary = group_summary(articles, groups, trends)


st.title("Public Interest")
st.caption("Google Trends search interest for PSN satellites and related topics")

# search interest over time
st.subheader("search interest over time")

chosen = st.multiselect("Keywords", list(keyword_of.keys()), default=list(keyword_of.keys()),
                        format_func=lambda k: keyword_of[k])

if chosen: 
    search = trends[["month"] + [k + "_interest" for k in chosen]].copy()
    search.columns = ["month"] + [keyword_of[k] for k in chosen]
    search = search.melt(id_vars="month", var_name="Keyword", value_name="Search interest")
    fig = px.line(search, x="month", y="Search interest", color="Keyword")
    fig.update_layout(xaxis_title="", legend=dict(orientation="h", y=-0.2, title_text=""))
    st.plotly_chart(fig, width="stretch")
    st.caption("Each keyword has its own 0 to 100 scale.")
else:
    st.info("Pick atleast one keyword")

st.divider()

# Coverage vs search interest
st.subheader("News coverage vs search interest")

group_name = st.selectbox("Topic group", groups["group"])
row = groups[groups["group"] == group_name].iloc[0]
key = row["key"]

group_articles = articles[articles["group"] == group_name]
per_month = group_articles.groupby("month").size().reindex(trends["month"], fill_value=0)

fig = make_subplots()