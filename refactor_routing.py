import sys

def refactor(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    
    routing_started = False
    
    for i, line in enumerate(lines):
        if line.startswith('st.sidebar.markdown(f"**Logged in as:'):
            # inject routing init
            new_lines.append('if "current_page" not in st.session_state:\n')
            new_lines.append('    st.session_state["current_page"] = "dashboard"\n\n')
            
            # inject new sidebar
            new_lines.append('st.sidebar.markdown(f"### 👤 {st.session_state[\'username\'].upper()}")\n')
            new_lines.append('st.sidebar.divider()\n')
            
            new_lines.append('if st.sidebar.button("📊 Dashboard", use_container_width=True):\n')
            new_lines.append('    st.session_state["current_page"] = "dashboard"\n')
            new_lines.append('    st.rerun()\n')
            
            new_lines.append('if st.sidebar.button("🧑‍💻 My Profile", use_container_width=True):\n')
            new_lines.append('    st.session_state["current_page"] = "profile"\n')
            new_lines.append('    st.rerun()\n')
            
            new_lines.append('if st.sidebar.button("⚙️ Settings", use_container_width=True):\n')
            new_lines.append('    st.session_state["current_page"] = "settings"\n')
            new_lines.append('    st.rerun()\n')
            
            new_lines.append('st.sidebar.divider()\n')
            new_lines.append('if st.sidebar.button("🚪 Logout", use_container_width=True):\n')
            new_lines.append('    for key in list(st.session_state.keys()):\n')
            new_lines.append('        del st.session_state[key]\n')
            new_lines.append('    st.rerun()\n\n')
            
            # inject page bodies
            new_lines.append('if st.session_state["current_page"] == "dashboard":\n')
            
            routing_started = True
            continue
            
        if routing_started:
            if i >= 125 and i <= 144: # Skip old sidebar logic and theme logic
                continue
            if line.strip() == "":
                new_lines.append(line)
            else:
                new_lines.append('    ' + line)
        else:
            new_lines.append(line)
            
    # append profile and settings blocks
    new_lines.append('\n')
    new_lines.append('elif st.session_state["current_page"] == "profile":\n')
    new_lines.append('    st.title("🧑‍💻 My Profile")\n')
    new_lines.append('    st.divider()\n')
    new_lines.append('    summary = get_portfolio_value(st.session_state["user_id"])\n')
    new_lines.append('    port_value = summary.get("total_market_value")\n')
    new_lines.append('    port_value = float(port_value) if port_value is not None else 0.0\n')
    new_lines.append('    \n')
    new_lines.append('    col1, col2 = st.columns(2)\n')
    new_lines.append('    with col1:\n')
    new_lines.append('        st.metric("Username", st.session_state.get("username", "Unknown"))\n')
    new_lines.append('        st.metric("Email Address", st.session_state.get("email", "N/A"))\n')
    new_lines.append('    with col2:\n')
    new_lines.append('        st.metric("Total Portfolio Value", f"₹{port_value:,.2f}")\n')
    new_lines.append('        st.metric("Trading Tier", "Elite" if port_value > 100000 else "Standard")\n')
    new_lines.append('\n')
    new_lines.append('elif st.session_state["current_page"] == "settings":\n')
    new_lines.append('    st.title("⚙️ App Settings")\n')
    new_lines.append('    st.divider()\n')
    new_lines.append('    st.subheader("Personalization")\n')
    new_lines.append('    theme_choices = [\n')
    new_lines.append('        "Midnight Pro (Dark)", "Cyberpunk (Dark)", "Deep Ocean (Dark)", \n')
    new_lines.append('        "Clean White (Light)", "Sunset Glow (Light)", "Mint Light (Light)"\n')
    new_lines.append('    ]\n')
    new_lines.append('    selected_theme = st.selectbox(\n')
    new_lines.append('        "UI Theme", \n')
    new_lines.append('        theme_choices, \n')
    new_lines.append('        index=theme_choices.index(st.session_state.get("ui_theme", "Clean White (Light)"))\n')
    new_lines.append('    )\n')
    new_lines.append('    if selected_theme != st.session_state.get("ui_theme"):\n')
    new_lines.append('        st.session_state["ui_theme"] = selected_theme\n')
    new_lines.append('        st.rerun()\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    refactor('src/app_ui.py')
