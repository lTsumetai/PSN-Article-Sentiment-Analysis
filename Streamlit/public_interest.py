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

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=per_month.index, y=per_month.values, name="Articles", marker_color="lightgrey"),
              secondary_y=False)
fig.add_trace(go.Scatter(x=trends["month"], y=trends[key + "_interest"], name="Search interest",
                         line=dict(color="#C44E52")), secondary_y=True)
fig.update_yaxes(title_text="Articles per month", secondary_y=False)
fig.update_yaxes(title_text="Search interest (0-100)", secondary_y=True)
fig.update_layout(title=f"{group_name} (keyword: {row['keyword']})", legend=dict(orientation="h", y=-0.15))
st.plotly_chart(fig, width="stretch")

info = summary[summary["key"] == key].iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Search peak", info["Peak month"].strftime("%b %Y"))
c2.metric("Articles in the peak month", info["Articles in peak month"])
c3.metric("All articles of the group", info["Articles in group"])

with st.expander("Peak month and sentiment tables for every group"):
    st.dataframe(data["event_table"], hide_index=True, width="stretch")
    st.dataframe(data["event_drivers"], hide_index=True, width="stretch")

st.divider()

# Regional search interest
st.subheader("Regional search interest")

map_key = st.selectbox("Keyword", list(keyword_of.keys()), format_func=lambda k:keyword_of[k], key="map_key")
column = map_key +"_score"

map_names = [f["properties"]["Propinsi"] for f in geojson["features"]]
scored = region.dropna(subset=[column, "map_name"])

fig = go.Figure()
fig.add_trace(go.Choropleth(
    geojson=geojson, featureidkey="properties.Propinsi", locations=scored["map_name"],
    z=scored[column], text=scored["region"], zmin=0, zmax=100, colorscale="yLOrRd",
    colorbar_title="Score", marker_line_color="white", marker_line_width=0.5,
    hovertemplate="<b>%{text}</b><br>Score: %{z}<extra></extra>",
))
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, width="stretch")
st.caption(f"{len(scored)} provinces have a score. Google hides provinces without enough searches "
           "(grey = no data), so keywords with few searches show only a few provinces.")

heat = region.set_index("region")[[k + "_score" for k in keyword_of]]
heat.columns = list(keyword_of.values())
heat = heat.loc[heat.mean(axis=1).sort_values(ascending=False).index]
fig = px.imshow(heat, text_auto=".0f", color_continuous_scale="YlOrRd", zmin=0, zmax=100,
                aspect="auto", height=max(400, 22 * len(heat)), title="Score by province and keyword")
fig.update_layout(coloraxis_colorbar_title="Score")
st.plotly_chart(fig, width="stretch")

st.divider()