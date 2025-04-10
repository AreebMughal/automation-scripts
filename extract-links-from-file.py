import json
import re

# Input file path
input_file = "sns_topics.txt"
output_file = "sns_links.json"

# Regular expression to match URLs
url_pattern = re.compile(r"https?://[^\s]+")

# Dictionary to store extracted URLs
sns_links = {}

# Read the file and process it
with open(input_file, "r") as file:
    current_topic = None
    print('----', file)
    for line in file:
        line = line.strip()

        # Check if the line starts with "Topic:" to capture topic name
        if line.startswith("Topic: arn:aws:sns"):
            current_topic = line.split(": ", 1)[1]
            sns_links[current_topic] = []

        # Search for URLs in the line
        match = url_pattern.search(line)
        if match and current_topic:
            sns_links[current_topic].append(match.group())

# Save extracted links to a JSON file
with open(output_file, "w") as json_file:
    json.dump(sns_links, json_file, indent=4)

print(f"Extracted links saved to {output_file}")
