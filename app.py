import streamlit as st
import pandas as pd

# Define keyword-to-tag mapping (example)
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

# Session state to store tagged policies and their tags
if "tagged_policies" not in st.session_state:
    st.session_state["tagged_policies"] = []

if "tags_in_use" not in st.session_state:
    st.session_state["tags_in_use"] = []

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

# Function to extract tags from policy title
def extract_tags(title):
    tags = set()
    for word in title.lower().split():
        for keyword, tag in keyword_to_tag.items():
            if keyword in word:
                tags.add(tag)
    return list(tags)

# Function to validate priority and multitagging logic
def validate_priority_and_multitagging(new_title, new_priority):
    # Check if the new policy can be multitagged
    tags = extract_tags(new_title)

    # Check if tags of the new policy conflict with existing policies' tags
    conflicting_tags = [tag for tag in tags if tag in st.session_state["tags_in_use"]]
    if conflicting_tags:
        st.warning(f"Cannot add policy '{new_title}' because it shares the following tags with existing policies: {', '.join(conflicting_tags)}.")
        return False

    # Check for priority conflicts
    for policy in st.session_state["tagged_policies"]:
        if policy["priority"] > new_priority:
            st.warning(f"Policy '{new_title}' has a higher priority than '{policy['title']}' (priority {policy['priority']}), removing the lower priority policy.")
            st.session_state["tagged_policies"].remove(policy)
            st.session_state["tags_in_use"] = [tag for tag in st.session_state["tags_in_use"] if tag not in policy["tags"]]
            break

    # Add new policy's tags to global tags_in_use
    st.session_state["tags_in_use"].extend(tags)
    return True

# Function to add a new policy
def add_policy(title, priority):
    # Validate and process the policy
    if validate_priority_and_multitagging(title, priority):
        tags = extract_tags(title)
        st.session_state["tagged_policies"].append({"title": title, "priority": priority, "tags": tags})
        st.success(f"Policy '{title}' added with priority {priority}.")

# Display current policies
st.markdown("### Current Policies")
df_out = pd.DataFrame(st.session_state["tagged_policies"])
st.dataframe(df_out)

# Add new policy
st.markdown("### Add a New Policy")
new_title = st.text_input("Enter the policy title (e.g., 'Adult sexual solicitation')")
new_priority = st.selectbox("Select the priority for this policy (1 is highest)", list(range(1, len(st.session_state["tagged_policies"]) + 2)))

if st.button(f"Add Policy '{new_title}'"):
    add_policy(new_title, new_priority)

# Export the results
csv = df_out.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "tagged_policies.csv", "text/csv")
