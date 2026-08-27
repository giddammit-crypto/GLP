import re
import sys

def analyze_and_balance(filepath, outpath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    out_content = ""
    lines = content.split('\n')
    
    in_focus = False
    focus_lines = []
    
    branches = {
        "Military": 0,
        "Economy": 0,
        "Politics": 0,
        "Diplomacy": 0,
        "Naval/Air": 0,
        "Technology": 0,
        "Other": 0
    }
    
    orphans = []
    
    for line in lines:
        if line.strip() == "focus = {":
            in_focus = True
            focus_lines = [line]
        elif in_focus:
            focus_lines.append(line)
            open_b = sum(1 for c in '\n'.join(focus_lines) if c == '{')
            close_b = sum(1 for c in '\n'.join(focus_lines) if c == '}')
            if open_b == close_b:
                in_focus = False
                focus_text = '\n'.join(focus_lines)
                
                # Extract id, x, y
                id_match = re.search(r'\n\s*id\s*=\s*([a-zA-Z0-9_]+)', focus_text)
                x_match = re.search(r'\n\s*x\s*=\s*(\d+)', focus_text)
                y_match = re.search(r'\n\s*y\s*=\s*(\d+)', focus_text)
                
                f_id = id_match.group(1) if id_match else "unknown"
                x = int(x_match.group(1)) if x_match else 0
                y = int(y_match.group(1)) if y_match else 0
                
                # Branch check
                if 2 <= x <= 6: branches["Military"] += 1
                elif 8 <= x <= 14: branches["Economy"] += 1
                elif 16 <= x <= 22: branches["Politics"] += 1
                elif 24 <= x <= 30: branches["Diplomacy"] += 1
                elif 32 <= x <= 40: branches["Naval/Air"] += 1
                elif 42 <= x <= 54: branches["Technology"] += 1
                else: branches["Other"] += 1
                
                # Prerequisite check
                has_prereq = "prerequisite =" in focus_text or "mutually_exclusive =" in focus_text
                if y > 0 and not has_prereq:
                    orphans.append(f_id)
                
                # Balancing costs
                if y <= 1: cost = 5
                elif y <= 3: cost = 7
                elif y <= 5: cost = 10
                else: cost = 14
                focus_text = re.sub(r'(\n\s*cost\s*=\s*)\d+', rf'\g<1>{cost}', focus_text)
                
                # ai_will_do modifiers
                if "ai_will_do = {" in focus_text:
                    if "has_war = yes" not in focus_text:
                        # Find end of ai_will_do
                        # We use regex to find ai_will_do block
                        ai_block = re.search(r'(ai_will_do\s*=\s*\{[^{}]*\})', focus_text)
                        if ai_block:
                            ai_text = ai_block.group(1)
                            # add modifier based on branch
                            if 2 <= x <= 6 or 32 <= x <= 40: # Military/Naval/Air
                                new_ai = ai_text[:-1] + "\n\t\t\tmodifier = { factor = 2 has_war = yes }\n\t\t}"
                            elif 8 <= x <= 14: # Economy
                                new_ai = ai_text[:-1] + "\n\t\t\tmodifier = { factor = 0.5 has_war = yes }\n\t\t}"
                            else:
                                new_ai = ai_text
                            focus_text = focus_text.replace(ai_text, new_ai)
                
                # Rewards audit (basic caps)
                # We won't strictly enforce with regex because of complexity, but we cap large numbers
                focus_text = re.sub(r'add_political_power\s*=\s*([1-9][5-9]0|200)', 'add_political_power = 100', focus_text)
                focus_text = re.sub(r'add_stability\s*=\s*0\.[2-9]\d*', 'add_stability = 0.10', focus_text)
                focus_text = re.sub(r'add_war_support\s*=\s*0\.[2-9]\d*', 'add_war_support = 0.10', focus_text)
                
                out_content += focus_text + '\n'
        else:
            out_content += line + '\n'
            
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(out_content)

    print("Branches:", branches)
    print("Orphans (y>0, no prereq):", orphans)

if __name__ == "__main__":
    parse_and_balance = analyze_and_balance
    parse_and_balance("/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod/common/national_focus/GLP_focus.txt", "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod/common/national_focus/GLP_focus.txt")
