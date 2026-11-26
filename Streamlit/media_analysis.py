import plotly.express as px
import streamlit as st

from common import MIN_TOPIC_N, SENTIMENT_COLORS, SENTIMENT_ORDER, load_data

data = load_data()
articles = data["articles"]
topic_keywords = data["topics"]

st.title("Media Analysis")
st.caption("How the news talks about PSN: topics, sentiment and coverage")

# ---------------------------------------------------------------- filters
year_min, year_max = int(articles["year"].min()), int(articles["year"].max())
all_topics = sorted(articles[articles["topic"] != -1]["topic_label"].unique())

f1, f2, f3 = st.columns(3)
years = f1.slider("Year", year_min, year_max, (year_min, year_max))
topics = f2.multiselect("Topic", all_topics, default=all_topics)
sentiments = f3.multiselect("Sentiment", SENTIMENT_ORDER, default=SENTIMENT_ORDER)

df = articles[
    articles["year"].between(years[0], years[1])
    & articles["topic_label"].isin(topics)
    & articles["sentiment"].isin(sentiments)
]

st.caption(f"{len(df)} of {len(articles)} articles selected. Outlier articles that fit no topic are left out of the topic charts.")

if df.empty:
    st.warning("No articles match the filters. Please widen the filters above.")
    st.stop()

st.divider()

# ------------------------------------------------------ sentiment distribution
st.subheader("Sentiment distribution")

left, right = st.columns(2)

counts = df["sentiment"].value_counts().reindex(SENTIMENT_ORDER).fillna(0).reset_index()
counts.columns = ["sentiment", "articles"]
fig = px.bar(counts, x="sentiment", y="articles", text="articles", color="sentiment",
             color_discrete_map=SENTIMENT_COLORS, title="Articles per sentiment")
fig.update_layout(showlegend=False, xaxis_title="")
left.plotly_chart(fig, width="stretch")

fig = px.histogram(df, x="sentiment_score", nbins=30, color="sentiment", color_discrete_map=SENTIMENT_COLORS,
                   category_orders={"sentiment": SENTIMENT_ORDER}, title="Sentiment score (-1 negative, +1 positive)")
fig.update_layout(xaxis_title="Sentiment score", yaxis_title="Articles", legend_title_text="")
right.plotly_chart(fig, width="stretch")

st.divider()

# ------------------------------------------------------------ sentiment by topic
st.subheader("Sentiment by topic")

topic_df = df[df["topic"] != -1]
topic_sizes = topic_df["topic_label"].value_counts()
big_topics = topic_sizes[topic_sizes >= MIN_TOPIC_N].index

if len(big_topics) == 0:
    st.info(f"No topic has at least {MIN_TOPIC_N} articles with the current filters.")
else:
    big_df = topic_df[topic_df["topic_label"].isin(big_topics)]
    share = (big_df.groupby(["topic_label", "sentiment"]).size() / big_df.groupby("topic_label").size() * 100)
    share = share.rename("percent").reset_index()
    fig = px.bar(share, x="percent", y="topic_label", color="sentiment", orientation="h",
                 color_discrete_map=SENTIMENT_COLORS, category_orders={"sentiment": SENTIMENT_ORDER})
    fig.update_layout(xaxis_title="% of articles", yaxis_title="", legend_title_text="")
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Only topics with at least {MIN_TOPIC_N} articles are shown.")

st.divider()

# ------------------------------------------------ topic frequency and keywords
st.subheader("Topic frequency and representation")

left, right = st.columns([1, 2])

topic_counts = topic_df["topic_label"].value_counts().sort_values().reset_index()
topic_counts.columns = ["topic", "articles"]
fig = px.bar(topic_counts, x="articles", y="topic", orientation="h", text="articles")
fig.update_layout(yaxis_title="", xaxis_title="Articles", margin=dict(t=10))
left.plotly_chart(fig, width="stretch")

keyword_table = topic_df.groupby("topic").agg(
    articles=("doc_id", "count"), avg_sentiment=("sentiment_score", "mean")
).reset_index()
keyword_table["share"] = keyword_table["articles"] / len(topic_df) * 100
keyword_table = keyword_table.merge(topic_keywords, on="topic", how="left").sort_values("articles", ascending=False)
right.dataframe(
    keyword_table[["topic_label", "articles", "share", "avg_sentiment", "keywords"]],
    hide_index=True,
    width="stretch",
    column_config={
        "topic_label": "Topic",
        "articles": "Articles",
        "share": st.column_config.NumberColumn("Share (%)", format="%.1f"),
        "avg_sentiment": st.column_config.NumberColumn("Avg sentiment", format="%+.2f"),
        "keywords": "Top keywords",
    },
)

st.divider()

# ---------------------------------------------------------- coverage trends
st.subheader("News coverage trends")

o1, o2 = st.columns(2)
period = o1.radio("Time period", ["Monthly", "Yearly"], horizontal=True)
stack_by = o2.radio("Split by", ["Topic", "Sentiment"], horizontal=True)

x_col = "month" if period == "Monthly" else "year"
color_col = "topic_label" if stack_by == "Topic" else "sentiment"
plot_df = df if stack_by == "Sentiment" else topic_df

trend = plot_df.groupby([x_col, color_col]).size().reset_index(name="articles")
if color_col == "sentiment":
    fig = px.bar(trend, x=x_col, y="articles", color=color_col, color_discrete_map=SENTIMENT_COLORS,
                 category_orders={"sentiment": SENTIMENT_ORDER})
else:
    fig = px.bar(trend, x=x_col, y="articles", color=color_col)
if x_col == "year":
    fig.update_xaxes(type="category")
fig.update_layout(xaxis_title="", yaxis_title="Articles", legend_title_text="")
st.plotly_chart(fig, width="stretch")

st.divider()

# --------------------------------------------------------- article explorer
st.subheader("Article explorer")

search = st.text_input("Search in title", "")
table = df
if search:
    table = table[table["title_clean"].str.contains(search, case=False, na=False)]
table = table.sort_values("date", ascending=False)

st.caption(f"{len(table)} articles. Click a column name to sort. Sentiment is the model prediction, "
           "or the hand label where the article was labelled by hand.")
st.dataframe(
    table[["title_clean", "source", "date", "topic_label", "sentiment", "label_source", "article_url"]],
    hide_index=True,
    width="stretch",
    column_config={
        "title_clean": "Title",
        "source": "Source",
        "date": st.column_config.DateColumn("Date"),
        "topic_label": "Topic",
        "sentiment": "Predicted sentiment",
        "label_source": "Label by",
        "article_url": st.column_config.LinkColumn("Original article", display_text="open"),
    },
)
