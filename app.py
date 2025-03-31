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

# Priority system: Define priority levels (High > Medium > Low)
priority_levels = ["High", "Medium", "Low"]

# Session state to store tagged policies and their tags
if "tagged_policies" not in st.session_state:
    st.session_state["tagged_policies"] = []

if "tags_in_use" not in st.session_state:
    st.session_state["tags_in_use"] = []

st.title("Policy Tagger (Keyword-Based with Priority)")

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

def tag_policy(title, priority):
    # Extract tags from title
    tags = extract_tags(title)

    # Check for overlapping tags with already tagged policies
    conflicting_tags = [tag for tag in tags if tag in st.session_state["tags_in_use"]]
    
    if conflicting_tags:
        st.warning(f"Cannot tag '{title}' because the following tags are already in use by higher priority policies: {', '.join(conflicting_tags)}.")
        return None

    # If no conflict, add tags to the global tags_in_use list and tagged_policies
    st.session_state["tags_in_use"].extend(tags)
    st.session_state["tagged_policies"].append({"title": title, "tags": tags, "priority": priority})
    return {"title": title, "tags": tags, "priority": priority}

def modify_policy(index, new_title):
    st.session_state["tagged_policies"][index]["title"] = new_title

def remove_policy(index):
    policy_to_remove = st.session_state["tagged_policies"][index]
    # Remove associated tags from the tags_in_use list
    for tag in policy_to_remove["tags"]:
        st.session_state["tags_in_use"].remove(tag)
    st.session_state["tagged_policies"].pop(index)

# Display existing policies
if st.session_state["tagged_policies"]:
    st.markdown("### Existing Policies")
    df_existing = pd.DataFrame(st.session_state["tagged_policies"])
    st.dataframe(df_existing)

    # Modify or remove existing policies
    st.markdown("### Modify or Remove Policies")
    policy_to_modify = st.selectbox("Select policy to modify", options=range(len(st.session_state["tagged_policies"])), format_func=lambda x: st.session_state["tagged_policies"][x]["title"])
    
    new_title = st.text_input("New title for the selected policy", value=st.session_state["tagged_policies"][policy_to_modify]["title"])
    if st.button("Modify Policy"):
        modify_policy(policy_to_modify, new_title)
        st.success(f"Policy '{new_title}' updated successfully.")
    
    if st.button("Remove Policy"):
        remove_policy(policy_to_modify)
        st.success("Policy removed successfully.")

# Tagging Policies: Allow user to specify priority
if titles:
    st.markdown("### Tag New Policies")
    
    # Allow tagging with priority
    for title in titles:
        priority = st.selectbox(f"Priority for '{title}'", priority_levels, key=f"{title}_priority")
        
        if st.button(f"Tag '{title}'", key=f"{title}_tag"):
            result = tag_policy(title, priority)
            if result:
                st.success(f"Policy '{title}' tagged successfully with {', '.join(result['tags'])}.")
    
    # Display tagged policies
    if st.session_state["tagged_policies"]:
        df_out = pd.DataFrame(st.session_state["tagged_policies"])
        st.dataframe(df_out)

    # Export the results
    csv = df_out.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "tagged_policies.csv", "text/csv")
