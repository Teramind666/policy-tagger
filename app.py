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

st.title("Policy Tagging Tool")

# Section to manage policies
with st.expander("🛠️ Manage Policies"):
    policy_name = st.text_input("Policy name")
    priority = st.number_input("Priority (1 = highest)", min_value=1, step=1)
    instructions = st.text_area("Instructions")
    conflicts = st.multiselect("Conflicts with", list(st.session_state.policies.keys()))

    if st.button("Add/Update Policy"):
        st.session_state.policies[policy_name] = {
            "priority": priority,
            "conflicts": conflicts,
            "instructions": instructions
        }
        st.success(f"Policy '{policy_name}' added/updated.")

    to_delete = st.selectbox("Select policy to delete", ["None"] + list(st.session_state.policies.keys()))
    if st.button("Delete Policy") and to_delete != "None":
        del st.session_state.policies[to_delete]
        st.success(f"Policy '{to_delete}' deleted.")

# Policy tagging area
st.markdown("### 🔍 Tag Policies")
search_input = st.text_input("Type policy to tag")

if search_input and st.button("Tag Policy"):
    policy = search_input.strip()
    if policy not in st.session_state.policies:
        st.error("Policy not found. Please add it first.")
    else:
        conflicts = st.session_state.policies[policy]["conflicts"]
        priority = st.session_state.policies[policy]["priority"]

        blocked = False
        for existing in st.session_state.tagged:
            existing_priority = st.session_state.policies[existing]["priority"]
            if existing in conflicts:
                if priority < existing_priority:
                    st.session_state.tagged.remove(existing)
                    st.warning(f"'{existing}' removed because '{policy}' has higher priority.")
                    break
                else:
                    st.warning(f"Cannot tag '{policy}' with '{existing}' due to conflict.")
                    blocked = True
                    break

        if not blocked and policy not in st.session_state.tagged:
            st.session_state.tagged.append(policy)
            st.success(f"'{policy}' tagged successfully.")

st.markdown("### 🏷️ Tagged Policies")
if st.session_state.tagged:
    for t in st.session_state.tagged:
        st.write(f"- {t} ({st.session_state.policies[t]['instructions']})")
else:
    st.info("No policies tagged yet.")
