import sys

def refactor(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    
    # We will track if we are inside a tab block. 
    # A tab block starts with "with tab_" at index 0.
    # It ends when we hit another line at index 0 that is not empty.
    
    in_tab_block = False
    
    for line in lines:
        if line.startswith('tabs_list ='):
            new_lines.append('is_admin = st.session_state["role"] == "admin"\n')
            new_lines.append('if is_admin:\n')
            new_lines.append('    tabs = st.tabs(["Admin Panel", "Market View", "Compare Models"])\n')
            new_lines.append('    tab_admin, tab_market, tab_compare = tabs[0], tabs[1], tabs[2]\n')
            new_lines.append('    tab_backtest = tab_strategy = tab_portfolio = None\n')
            new_lines.append('else:\n')
            new_lines.append('    tabs = st.tabs(["Market View", "Backtest", "Strategy Builder", "Portfolio", "Compare Models"])\n')
            new_lines.append('    tab_market, tab_backtest, tab_strategy, tab_portfolio, tab_compare = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]\n')
            new_lines.append('    tab_admin = None\n')
            continue
        
        if line.startswith('if st.session_state["role"] == "admin":') and 'append("Admin Panel")' in lines[lines.index(line)+1]:
            continue # skip the old logic
        if line.strip() == 'tabs_list.append("Admin Panel")':
            continue
        if line.startswith('tabs = st.tabs('):
            continue
        if line.startswith('tab_market, tab_backtest'):
            continue
            
        # The old admin tab block was:
        # if st.session_state["role"] == "admin":
        #     with tabs[5]:
        if line.startswith('if st.session_state["role"] == "admin":'):
            try:
                next_line = lines[lines.index(line)+1]
                if 'with tabs[' in next_line:
                    new_lines.append('if tab_admin:\n')
                    new_lines.append('    with tab_admin:\n')
                    in_tab_block = True
                    continue
            except IndexError:
                pass

        if line.strip().startswith('with tabs['):
            continue

        if line.startswith('with tab_'):
            tab_var = line.strip().split(':')[0].replace('with ', '')
            new_lines.append(f'if {tab_var}:\n')
            new_lines.append(f'    {line}')
            in_tab_block = True
            continue
            
        if in_tab_block:
            if line.strip() == '' or line.startswith(' ') or line.startswith('\t'):
                new_lines.append('    ' + line if line.strip() != '' else line)
            else:
                # We hit a new un-indented block, meaning the tab block is over
                in_tab_block = False
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    refactor('src/app_ui.py')
