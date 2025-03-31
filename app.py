import streamlit as st
import pandas as pd

# Define keyword-to-tag mapping (updated)
tag_rules = {
    "privacy": ["privacy", "data protection", "GDPR"],
    "trust and safety": ["trust", "safety", "harassment", "abuse", "moderation"],
    "AI": ["AI", "artificial intelligence", "machine learning"],
    "ethics": ["ethics", "moral", "responsibility"],
    "government": ["government", "state", "public sector"],
    "HR": ["employee", "HR", "conduct", "behavior"],
    "social media": ["social media", "Facebook", "Twitter", "Instagram"],
}

# Reverse map: keyword -> tag
keyword_to_tag = {kw.lower(): tag for tag, kws in tag_rules.items() for kw in kws}

st.title("Policy Tagger (Keyword-Based)")

# Input: Upload CSV or paste titles
upload_option = st.radio("How would you like to input policies?", ["Paste titles", "Upload CSV"])

titles = []
if upload_option == "Paste titles":
    text = st.text_area("Paste policy titles (one per line)", height=200)
    if text:
        titles = [line.strip() for line in text.strip().split("\n") if line.strip()]
else:
    uploaded_file = st.file_uploader("Upload a CSV with a 'title' column", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "title" in df.columns:
            titles = df["title"].dropna().tolist()
        else:
            st.error("CSV must have a 'title' column.")

def extract_tags(title):
    tags = set()
    for word in title.lower().split():
        for keyword, tag in keyword_to_tag.items():
            if keyword in word:
                tags.add(tag)
    return list(tags)

if titles:
    st.markdown("### Results")
    results = [{"title": t, "tags": extract_tags(t)} for t in titles]
    df_out = pd.DataFrame(results)
    st.dataframe(df_out)

    csv = df_out.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "tagged_policies.csv", "text/csv")
