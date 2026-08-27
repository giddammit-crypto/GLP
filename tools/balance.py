import re
import sys

def parse_and_balance(filepath, outpath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple state machine to parse and modify focuses
    # We will search for focuses and apply rules based on their y value
    
    out_content = ""
    lines = content.split('\n')
    
    in_focus = False
    focus_lines = []
    
    for line in lines:
        if line.strip() == "focus = {":
            in_focus = True
            focus_lines = [line]
        elif in_focus:
            focus_lines.append(line)
            # count braces to find end of focus
            open_b = sum(1 for c in '\n'.join(focus_lines) if c == '{')
            close_b = sum(1 for c in '\n'.join(focus_lines) if c == '}')
            if open_b == close_b:
                in_focus = False
                # Process focus_lines
                focus_text = '\n'.join(focus_lines)
                
                # Extract y
                y_match = re.search(r'\n\s*y\s*=\s*(\d+)', focus_text)
                if y_match:
                    y = int(y_match.group(1))
                    if y <= 1:
                        cost = 5
                    elif y <= 3:
                        cost = 7
                    else:
                        cost = 10
                    # Replace cost
                    focus_text = re.sub(r'(\n\s*cost\s*=\s*)\d+', rf'\g<1>{cost}', focus_text)
                    
                    # Update ai_will_do
                    # Look for ai_will_do block
                    if "ai_will_do" in focus_text:
                        # Add modifier for war and peace if they don't exist
                        if "has_war = yes" not in focus_text:
                            # It's a simplistic addition, just before the closing brace of ai_will_do
                            ai_match = re.search(r'(\n\s*ai_will_do\s*=\s*\{[^}]*)(\n\s*\})', focus_text)
                            if ai_match:
                                # Not perfect because of nested braces, but ai_will_do is usually simple.
                                # Let's skip complex ai_will_do parsing for now or do a simple replace
                                pass
                
                out_content += focus_text + '\n'
        else:
            out_content += line + '\n'
            
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(out_content)

if __name__ == "__main__":
    parse_and_balance("/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod/common/national_focus/GLP_focus.txt", "/home/astra/.gemini/antigravity/scratch/hoi4_gulyaypole_mod/common/national_focus/GLP_focus_balanced.txt")
