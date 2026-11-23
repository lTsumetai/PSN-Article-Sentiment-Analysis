import streamlit as st

st.set_page_config(page_title="PSN News & Public Interest", page_icon= "🛰️", layout="wide")

pages = [
    st.Page("Streamlit/overview.py", title="Overview", default=True),
    st.Page("Streamlit/media_analysis.py", title="Media Analysis"),
    st.Page("Streamlit/public_interest.py", title="Public Interest")
]

st.sidebar.title("🛰️ PSN Dashboard")
st.sidebar.caption("News Coverage, sentiment and Google Trends for Pasifik Satelit Nusantara")
page = st.navigation(pages)
page.run()