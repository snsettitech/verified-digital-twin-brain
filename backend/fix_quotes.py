import sys

# Read the file
with open('routers/cognitive.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count smart quotes
smart_quote_count = content.count('\u2019')
print(f"Found {smart_quote_count} right single quotation marks (U+2019)")

# Replace all smart quotes with straight quotes
fixed_content = content.replace('\u2019', "'")

# Write back
with open('routers/cognitive.py', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(fixed_content)

print("Fixed!")
