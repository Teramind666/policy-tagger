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
    "hate speech": ["hate speech", "racism", "discrimination", "offensive language"],
}

# Reverse map: keyword -> tag
keyword_to_tag = {kw.lower(): tag for tag, kws in tag_rules.items() for kw in kws}

# Priority system: Define priority levels (High > Medium > Low)
priority_levels = ["High", "Medium", "Low"]

# Tier options: 5-level or 7-level tier system
tier_levels = [5, 7]

# Initialize session state variables if not already done
if "tagged_policies" not in st.session_state:
    st.session_state["tagged_policies"] = []

if "tags_in_use" not in st.session_state:
    st.session_state["tags_in_use"] = []

if "categories" not in st.session_state:
    st.session_state["categories"] = ["Privacy", "Trust and Safety", "AI", "Ethics", "Government", "HR", "Social Media", "Hate Speech"]

st.title("Policy Tagger (Keyword-Based with Categories, Tiers, and Multitagging Option)")

# Input: Upload CSV or paste titles
upload_option = st.radio("How would you like to input policies?", ["Paste titles", "Upload CSV", "Add Manually"])

titles = []
if upload_option == "Paste titles":
    text = st.text_area("Paste policy titles (one per line)", height=200)
    if text:
        titles = [line.strip() for line in text.strip().split("\n") if line.strip()]
elif upload_option == "Add Manually":
    manual_title = st.text_input("Enter a policy title")
    if manual_title:
        titles.append(manual_title)
else:
    uploaded_file = st.file_uploader("Upload a CSV with a 'title' column", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "title" in df.columns:
            titles = df["title"].dropna().tolist()
        else:
            st.error("CSV must have a 'title' column.")

# Allow custom categories to be added
st.sidebar.header("Add Custom Categories")
new_category = st.sidebar.text_input("Enter new category")
if new_category and new_category not in st.session_state["categories"]:
    st.session_state["categories"].append(new_category)
    st.sidebar.success(f"Category '{new_category}' added!")

# Select category for each policy
def extract_tags(title):
    tags = set()
    for word in title.lower().split():
        for keyword, tag in keyword_to_tag.items():
            if keyword in word:
                tags.add(tag)
    return list(tags)

def tag_policy(title, category, tier, allow_multitagging):
    # Extract tags from title
    tags = extract_tags(title)

    # Check if the policy should allow multitagging
    if not allow_multitagging:
        # Check for overlapping tags with already tagged policies
        conflicting_tags = [tag for tag in tags if tag in st.session_state["tags_in_use"]]
        if conflicting_tags:
            st.warning(f"Cannot tag '{title}' because the following tags are already in use by other policies: {', '.join(conflicting_tags)}.")
            return None

    # If no conflict, add tags to the global tags_in_use list and tagged_policies
    st.session_state["tags_in_use"].extend(tags)
    st.session_state["tagged_policies"].append({"title": title, "category": category, "tier": tier, "tags": tags, "allow_multitagging": allow_multitagging})
    return {"title": title, "category": category, "tier": tier, "tags": tags, "allow_multitagging": allow_multitagging}

# Add Policies: Allow user to specify category, tier, multitagging option, and rename policies
if titles:
    st.markdown("### Add New Policies")
    
    for title in titles:
        renamed_title = st.text_input(f"Rename policy '{title}' (optional)", value=title, key=f"{title}_rename")
        category = st.selectbox(f"Select category for '{renamed_title}'", st.session_state["categories"], key=f"{renamed_title}_category")
        tier = st.selectbox(f"Select tier for '{renamed_title}'", tier_levels, key=f"{renamed_title}_tier")
        allow_multitagging = st.checkbox(f"Allow multitagging for '{renamed_title}'", value=True, key=f"{renamed_title}_multitag")

        if st.button(f"Tag '{renamed_title}'", key=f"{renamed_title}_tag"):
            result = tag_policy(renamed_title, category, tier, allow_multitagging)
            if result:
                st.success(f"Policy '{renamed_title}' tagged successfully under category '{category}' with tier '{tier}'.")

    # Display tagged policies
    if st.session_state["tagged_policies"]:
        df_out = pd.DataFrame(st.session_state["tagged_policies"])
        st.dataframe(df_out)

    # Export the results
    csv = df_out.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "tagged_policies.csv", "text/csv")
