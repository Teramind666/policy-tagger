import streamlit as st
import pandas as pd

# Predefined conflicts between policies (this is just an example)
policy_conflicts = {
    "Adult sexual solicitation": ["General body exposure", "Adult sexual behavior", "Adult sexual activity"],
    "Adult sexual behavior": ["Adult sexual solicitation", "General body exposure", "Adult sexual activity"],
    "Adult sexual activity": ["Adult sexual solicitation", "General body exposure", "Adult sexual behavior"],
    "General body exposure": ["Adult sexual solicitation", "Adult sexual behavior", "Adult sexual activity"],
}

# All available policies
all_policies = ["Adult sexual solicitation", "Adult sexual behavior", "Adult sexual activity", "General body exposure"]

# Initialize session state for tracking selected policies
if "selected_policies" not in st.session_state:
    st.session_state["selected_policies"] = []

# Display available policies to select
st.title("Policy Multitagging Helper Tool")

# Policy selector
st.markdown("### Select policies to tag")
selected_policies = st.multiselect("Choose policies", all_policies)

# Function to check for conflicts
def check_conflicts(selected_policies):
    conflicts = []
    # Loop through the selected policies and check for conflicts
    for policy in selected_policies:
        conflicting_policies = policy_conflicts.get(policy, [])
        # Check if any conflicting policy is also selected
        for conflict in conflicting_policies:
            if conflict in selected_policies:
                conflicts.append(f"{policy} conflicts with {conflict}")
    return conflicts

# Check for any conflicts
conflicting_policies = check_conflicts(selected_policies)

if conflicting_policies:
    st.warning("You have selected conflicting policies! Please review the following:")
    for conflict in conflicting_policies:
        st.write(conflict)
else:
    st.success("No conflicts found! You can safely tag the selected policies.")

# Display guidance on how to tag policies
st.markdown("### How to properly tag policies:")
for policy, conflicts in policy_conflicts.items():
    st.write(f"**{policy}** cannot be tagged with: {', '.join(conflicts)}")

# Option to reset selection
if st.button("Clear selection"):
    st.session_state["selected_policies"] = []
    st.experimental_rerun()
