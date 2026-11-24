import pandas as pd
import plotly.express as px
import streamlit as st

from common import sentiment_colors, group_summary, load_data

data = load_data()
articles = data["articles"]
trends = data["trends"]
groups = data["groups"]

st.title("Overview")
st.caption("PSN (Pasifik Satelit Nusantara) news coverage and public search interest")

# key numbers
c1, c2, c3, c4 = st.columns(4)
c1.metric("Articles analyzed", len(articles))
for column, sentiment in zip([c2, c3, c4], ["positive", "neutral", "negative"]):
    count = int((articles["sentiment"] == sentiment).sum())
    column.metric(f"{sentiment.capitalize()}", f"{count / len(articles) * 100:.0f}%", f"{count} articles",
                  delta_color="off")
st.caption(f"Articles from {articles['date'].min().date()} to {articles['date'].max().date()}")

st.divider()

# Main page topics and Coverage
left, right = st.columns([1, 2])

with left:
    st.subheader("Most discussed topics")
    topic_counts = articles[articles["topic"] != -1]["topic_label"].value_counts().head(0).sort_values()
    topic_counts = topic_counts.reset_index()
    topic_counts.columns = ["topic", "articles"]
    fig = px.bar(topic_counts, x="articles", y="topic", orientation="h", text="articles")
    fig.update_layout(yaxis_title="", xaxis_title="Articles", margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("News coverage overtime")
    all_months = pd.date_range(articles["month"].min(), articles["month"].max(), freq="MS")
    per_month = articles.groupby("month").size().reindex(all_months, fill_value=0).reset_index()
    per_month.columns = ["month", "articles"]
    fig = px.bar(per_month, x="month", y="articles")
    fig.update_layout(xaxis_title="", yaxis_title="Articles per month", margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")

st.divider()

# Public Search Summary
st.subheader("Public search interest summary")

summary = group_summary(articles, groups, trends)

left, right = st.columns([2, 1])

with left:
    search = trends[["month"] + [k + "_interest" for k in summary["key"]]].copy()
    search.columns = ["month"] + list(summary["keyword"])
    search = search.melt(id_vars="month", var_name="keyword", value_name="Search interest")
    fig = px.line(search, x="month", y="Search interest", color="keyword")
    fig.update_layout(xaxis_title="", legend=dict(orientation="h", y=-0.2, title_text=""), margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")

with right:
    table = summary.copy()
    table["Peak month"] = table["peak month"].dt.strftime("%b %Y")
    st.dataframe(table[["keyword", "peak month", "months with searches"]], hide_index=True, width="stretch")
    st.caption("Each keyword has its own 0-100 scale, so compare the timing of the peaks, not the heights.")

st.info("People search for PSN satellites when there is a big event, such as a launch or a failure, "
        "and the news coverage of that event lands in the same month.")
