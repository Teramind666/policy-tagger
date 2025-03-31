import streamlit as st
import pandas as pd

# Initialize session state
if "policy_conflicts" not in st.session_state:
    st.session_state["policy_conflicts"] = {
        "Adult sexual solicitation": ["General body exposure", "Adult sexual behavior", "Adult sexual activity"],
        "Adult sexual behavior": ["Adult sexual solicitation", "General body exposure", "Adult sexual activity"],
        "Adult sexual activity": ["Adult sexual solicitation", "General body exposure", "Adult sexual behavior"],
        "General body exposure": ["Adult sexual solicitation", "Adult sexual behavior", "Adult sexual activity"],
    }

if "all_policies" not in st.session_state:
    st.session_state["all_policies"] = [
        "Adult sexual solicitation", 
        "Adult sexual behavior", 
        "Adult sexual activity", 
        "General body exposure"
    ]

if "tags_in_use" not in st.session_state:
    st.session_state["tags_in_use"] = []

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

# Function to extract tags from a policy title
def extract_tags(title):
    tags = set()
    for word in title.lower().split():
        for keyword, tag in keyword_to_tag.items():
            if keyword in word:
                tags.add(tag)
    return list(tags)

# Function to check for conflicts
def check_conflicts(selected_policies):
    conflicts = []
    # Loop through the selected policies and check for conflicts
    for policy in selected_policies:
        conflicting_policies = st.session_state["policy_conflicts"].get(policy, [])
        # Check if any conflicting policy is also selected
        for conflict in conflicting_policies:
            if conflict in selected_policies:
                conflicts.append(f"{policy} conflicts with {conflict}")
    return conflicts

# Add new policy function
def add_policy(new_title):
    if new_title not in st.session_state["all_policies"]:
        st.session_state["all_policies"].append(new_title)
        st.session_state["policy_conflicts"][new_title] = []  # Add empty conflict list
        st.success(f"Policy '{new_title}' added successfully.")
    else:
        st.warning(f"Policy '{new_title}' already exists.")

# Remove policy function
def remove_policy(policy_to_remove):
    if policy_to_remove in st.session_state["all_policies"]:
        st.session_state["all_policies"].remove(policy_to_remove)
        del st.session_state["policy_conflicts"][policy_to_remove]
        st.success(f"Policy '{policy_to_remove}' removed successfully.")
    else:
        st.warning(f"Policy '{policy_to_remove}' not found.")

# Rename policy function
def rename_policy(old_title, new_title):
    if old_title in st.session_state["all_policies"]:
        index = st.session_state["all_policies"].index(old_title)
        st.session_state["all_policies"][index] = new_title
        st.session_state["policy_conflicts"][new_title] = st.session_state["policy_conflicts"].pop(old_title)
        st.success(f"Policy '{old_title}' renamed to '{new_title}' successfully.")
    else:
        st.warning(f"Policy '{old_title}' not found.")

# Add or modify policy conflicts
def add_conflict(policy1, policy2):
    if policy1 in st.session_state["all_policies"] and policy2 in st.session_state["all_policies"]:
        if policy2 not in st.session_state["policy_conflicts"][policy1]:
            st.session_state["policy_conflicts"][policy1].append(policy2)
            st.session_state["policy_conflicts"][policy2].append(policy1)
            st.success(f"Conflict added between '{policy1}' and '{policy2}'.")
        else:
            st.warning(f"Conflict already exists between '{policy1}' and '{policy2}'.")
    else:
        st.warning("One or both policies do not exist.")

# Policy management interface
st.title("Policy Management & Multitagging Helper Tool")

st.markdown("### Add, Remove or Rename Policies")
action = st.radio("What would you like to do?", ["Add Policy", "Remove Policy", "Rename Policy", "Add Policy Conflict"])

if action == "Add Policy":
    new_policy = st.text_input("Enter the name of the new policy")
    if st.button("Add Policy"):
        add_policy(new_policy)

elif action == "Remove Policy":
    policy_to_remove = st.selectbox("Select a policy to remove", st.session_state["all_policies"])
    if st.button(f"Remove '{policy_to_remove}'"):
        remove_policy(policy_to_remove)

elif action == "Rename Policy":
    old_policy = st.selectbox("Select policy to rename", st.session_state["all_policies"])
    new_policy = st.text_input("Enter the new name for the policy")
    if st.button(f"Rename '{old_policy}'"):
        rename_policy(old_policy, new_policy)

elif action == "Add Policy Conflict":
    policy1 = st.selectbox("Select the first policy", st.session_state["all_policies"])
    policy2 = st.selectbox("Select the second policy", st.session_state["all_policies"])
    if st.button(f"Add conflict between '{policy1}' and '{policy2}'"):
        add_conflict(policy1, policy2)

# Display current policies
st.markdown("### Current Policies and Their Conflicts")
df_out = pd.DataFrame({
    "Policy": st.session_state["all_policies"],
    "Conflicting Policies": [", ".join(st.session_state["policy_conflicts"][p]) for p in st.session_state["all_policies"]]
})
st.dataframe(df_out)

# Display instructions
st.markdown("### Policy Conflict Instructions")
for policy, conflicts in st.session_state["policy_conflicts"].items():
    st.write(f"**{policy}** conflicts with: {', '.join(conflicts)}")

