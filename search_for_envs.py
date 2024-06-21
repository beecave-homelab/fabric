import requests
import re

# URL of the file in raw format
url = "https://raw.githubusercontent.com/danielmiessler/fabric/main/installer/client/cli/utils.py"

# Fetch the raw file content
response = requests.get(url)
file_content = response.text

# Define the regex pattern to find environment variables
env_var_pattern = re.compile(r'\b[A-Z_][A-Z0-9_]*=("[^"]*"|\S+)')

# Search for environment variable patterns
matches = env_var_pattern.findall(file_content)

# Print the matches
if matches:
    print("Found probable matches:")
    for match in matches:
        print(f"  Match: {match}")
else:
    print("No matches found.")
