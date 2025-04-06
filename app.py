import streamlit as st

# Initialize session state for policies and priorities
if "policies" not in st.session_state:
    st.session_state.policies = {
        "Adult sexual solicitation": {"priority": 1, "conflicts": ["Adult sexual activity", "Adult sexual behavior", "General body exposure"], "instructions": "Tag alone if solicitation is present."},
        "Adult sexual activity": {"priority": 2, "conflicts": ["Adult sexual solicitation", "Adult sexual behavior", "General body exposure"], "instructions": "Only tag if no solicitation."},
        "Adult sexual behavior": {"priority": 3, "conflicts": ["Adult sexual solicitation", "Adult sexual activity", "General body exposure"], "instructions": "Only tag if higher severity policies are not present."},
        "General body exposure": {"priority": 4, "conflicts": ["Adult sexual solicitation", "Adult sexual activity", "Adult sexual behavior"], "instructions": "Tag only if other higher priority policies do not apply."},
    }

if "tagged" not in st.session_state:
    st.session_state.tagged = []

st.title("🛡️ Policy Tagging Tool")

# Section to manage policies
with st.expander("🛠️ Manage Policies"):
    st.subheader("Add or Update a Policy")
    policy_name = st.text_input("Policy name")
    priority = st.number_input("Priority (1 = highest)", min_value=1, step=1, key="priority_input")
    instructions = st.text_area("Instructions", key="instructions_input")
    conflicts = st.multiselect("Conflicts with", list(st.session_state.policies.keys()), key="conflicts_input")

    if st.button("Add/Update Policy"):
        if policy_name:
            st.session_state.policies[policy_name] = {
                "priority": priority,
                "conflicts": conflicts,
                "instructions": instructions
            }
            st.success(f"Policy '{policy_name}' has been added or updated.")
        else:
            st.error("Please enter a policy name.")

    st.subheader("Delete a Policy")
    to_delete = st.selectbox("Select a policy to delete", ["None"] + list(st.session_state.policies.keys()), key="delete_select")
    if st.button("Delete Policy") and to_delete != "None":
        del st.session_state.policies[to_delete]
        st.success(f"Policy '{to_delete}' has been deleted.")

# Tagging section
st.markdown("### 🔍 Tag Policies")
all_policies = list(st.session_state.policies.keys())
policy_to_tag = st.selectbox("Select a policy to tag", ["-- Select a policy --"] + all_policies, key="tag_selector")

if policy_to_tag != "-- Select a policy --":
    conflicts = st.session_state.policies[policy_to_tag]["conflicts"]
    priority = st.session_state.policies[policy_to_tag]["priority"]
    blocked = False
    to_remove = None

    for existing in st.session_state.tagged:
        existing_priority = st.session_state.policies[existing]["priority"]
        if existing in conflicts:
            if priority < existing_priority:
                to_remove = existing
                break
            else:
                st.warning(f"❌ Cannot tag '{policy_to_tag}' with '{existing}' due to conflict. '{existing}' has higher priority.")
                blocked = True
                break

    if not blocked and policy_to_tag not in st.session_state.tagged:
        if to_remove:
            st.session_state.tagged.remove(to_remove)
            st.warning(f"⚠️ '{to_remove}' removed because '{policy_to_tag}' has higher priority.")
        st.session_state.tagged.append(policy_to_tag)
        st.success(f"✅ '{policy_to_tag}' tagged successfully.")

st.markdown("### 🏷️ Currently Tagged Policies")
if st.session_state.tagged:
    for t in st.session_state.tagged:
        st.write(f"- **{t}** — _{st.session_state.policies[t]['instructions']}_")
else:
    st.info("No policies tagged yet. Select one above to start.")
