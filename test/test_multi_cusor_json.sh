#!/bin/bash
# Test the API with a multi-cursor JSON question

# Replace with your actual API URL
API_URL="http://localhost:8000/api/"

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
cd "${TEMP_DIR}"

# Create a sample text file with key=value pairs
cat > q-multi-cursor-json.txt << 'EOF'
name=John Doe
age=30
email=john.doe@example.com
occupation=Software Engineer
address=123 Main St
city=New York
state=NY
zip=10001
phone=555-123-4567
isActive=true
hobbies=reading,coding,hiking
startDate=2023-01-15
EOF

# Send request to the API
echo "Testing multi-cursor JSON conversion and hashing..."
curl -X POST "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Download q-multi-cursor-json.txt and use multi-cursors and convert it into a single JSON object, where \`key=value\` pairs are converted into \`{key: value, key: value, ...}\`. What's the result when you paste the JSON at tools-in-data-science.pages.dev/jsonhash and click the Hash button?" \
  -F "file=@q-multi-cursor-json.txt"

# Clean up
cd - > /dev/null
rm -rf "${TEMP_DIR}"

echo -e "\nTest completed!"