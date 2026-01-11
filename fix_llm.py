import re

# Read the file
with open('core/llm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the """ closes
first_prompt_end = content.find('- **NEVER mix languages unless user mixes first**"""')

if first_prompt_end != -1:
    # Find the next section that should come after
    next_section = content.find('# Initialize backends', first_prompt_end)
    
    if next_section != -1:
        # Remove everything between the closing quotes and the next section
        before = content[:first_prompt_end + len('- **NEVER mix languages unless user mixes first**"""')]
        after = content[next_section:]
        
        fixed_content = before + '\n        \n        ' + after
        
        # Write back
        with open('core/llm.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Fixed syntax error!")
    else:
        print("❌ Could not find initialization section")
else:
    print("❌ Could not find prompt end")
