import streamlit as st
import pandas as pd

# Initialize session state for policies and conflicts
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

if "selected_policies" not in st.session_state:
    st.session_state["selected_policies"] = []

# Define the highest priority policy (e.g., "Adult sexual solicitation")
highest_priority_policy = "Adult sexual solicitation"

# Function to extract tags from a policy title
def extract_tags(title):
    tags = set()
    for word in title.lower().split():
        for keyword, tag in tag_rules.items():
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

# Function to check if the first policy is tagged and remove lower priority policies
def handle_priority_conflict(selected_policies):
    if highest_priority_policy in selected_policies:
        if len(selected_policies) > 1:  # If other policies are selected
            lower_priority_policies = [policy for policy in selected_policies if policy != highest_priority_policy]
            for policy in lower_priority_policies:
                # Remove lower priority policies
                st.warning(f"'{highest_priority_policy}' has higher priority. '{policy}' has been removed.")
                selected_policies.remove(policy)

# Policy management interface
st.title("Policy Multitagging Helper Tool")

st.markdown("### Select policies to tag")

# Select the policies
selected_policies = st.multiselect("Choose policies", st.session_state["all_policies"])

# Handle the priority conflicts when policies are selected
handle_priority_conflict(selected_policies)

# Check for conflicting tags
conflicting_policies = check_conflicts(selected_policies)

if conflicting_policies:
    st.warning("You have selected conflicting policies! Please review the following:")
    for conflict in conflicting_policies:
        st.write(conflict)
else:
    st.success("No conflicts found! You can safely tag the selected policies.")

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

# Option to reset selection
if st.button("Clear selection"):
    st.session_state["selected_policies"] = []
    st.experimental_rerun()
