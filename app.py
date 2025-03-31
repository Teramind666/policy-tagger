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
    "adult sexual solicitation": ["adult sexual solicitation", "solicitation", "explicit content"],
    "adult sexual activity": ["adult sexual activity", "sexual activity", "sexual content"],
    "adult sexual behavior": ["adult sexual behavior", "sexual behavior", "explicit material"],
    "general body exposure": ["general body exposure", "nudity", "body exposure"],
}

# Reverse map: keyword -> tag
keyword_to_tag = {kw.lower(): tag for tag, kws in tag_rules.items() for kw in kws}

# Priority system: Define priority levels (1 is highest, n is lowest)
tier_levels = list(range(1, 21))  # Example: tiers from 1 to 20 (you can extend this)

# Session state to store tagged policies and their tags
if "tagged_policies" not in st.session_state:
    st.session_state["tagged_policies"] = []

if "tags_in_use" not in st.session_state:
    st.session_state["tags_in_use"] = []

# Category of interest: Nudity and Sexual Activity
category_name = "Nudity and Sexual Activity"

# Session state for specific category policies (you can modify this structure if needed)
if "nudity_sexual_activity_policies" not in st.session_state:
    st.session_state["nudity_sexual_activity_policies"] = [
        {"title": "Adult sexual solicitation", "priority": 1},
        {"title": "Adult sexual activity", "priority": 2},
        {"title": "Adult sexual behavior", "priority": 3},
        {"title": "General body exposure", "priority": 4}
    ]

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

def extract_tags(title):
    tags = set()
    for word in title.lower().split():
        for keyword, tag in keyword_to_tag.items():
            if keyword in word:
                tags.add(tag)
    return list(tags)

# Function to check if policy priority is valid when adding or modifying
def validate_priority(new_priority, category_policies):
    for policy in category_policies:
        if policy["priority"] == new_priority:
            return False  # Priority already exists
    return True

# Add or modify policy
def add_or_modify_policy(title, new_priority):
    # Check if priority is valid
    if not validate_priority(new_priority, st.session_state["nudity_sexual_activity_policies"]):
        st.error(f"Priority {new_priority} is already assigned to another policy. Please choose a different priority.")
        return
    
    # Check if policy exists (modify if exists, otherwise add)
    existing_policy = next((p for p in st.session_state["nudity_sexual_activity_policies"] if p["title"] == title), None)
    
    if existing_policy:
        existing_policy["priority"] = new_priority
        st.success(f"Policy '{title}' updated to priority {new_priority}.")
    else:
        st.session_state["nudity_sexual_activity_policies"].append({"title": title, "priority": new_priority})
        st.success(f"Policy '{title}' added with priority {new_priority}.")

# Display current policies
st.markdown("### Current Policies in 'Nudity and Sexual Activity' Category")
df_out = pd.DataFrame(st.session_state["nudity_sexual_activity_policies"])
st.dataframe(df_out)

# Add or modify policies
st.markdown("### Add or Modify a Policy")
new_title = st.text_input("Enter the policy title (e.g., 'Adult sexual solicitation')")
new_priority = st.selectbox("Select the priority for this policy (1 is highest)", list(range(1, len(st.session_state["nudity_sexual_activity_policies"]) + 2)))

if st.button(f"Add or Modify '{new_title}'"):
    add_or_modify_policy(new_title, new_priority)

# Export the results
csv = df_out.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "tagged_policies.csv", "text/csv")
