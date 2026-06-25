import sys

def fix(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    
    admin_started = False
    
    for i, line in enumerate(lines):
        if 'st.header("Admin Dashboard")' in line:
            admin_started = True
            new_lines.append('if tab_admin:\n')
            new_lines.append('    with tab_admin:\n')
            
        if admin_started:
            if line.startswith('            '):
                new_lines.append('        ' + line[12:])
            elif line.strip() == '':
                new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    fix('src/app_ui.py')
