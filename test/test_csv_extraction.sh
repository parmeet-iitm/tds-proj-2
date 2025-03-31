#!/bin/bash
# Test the API with a CSV extraction question

# Replace with your actual API URL
API_URL="http://localhost:8000/api"

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
cd "${TEMP_DIR}"

# Create a CSV file
cat > extract.csv << 'EOF'
id,answer,value
1,test_answer_1ee23,42
2,another_value,53
3,third_value,67
EOF

# Create a ZIP file containing the CSV
zip -q test_archive.zip extract.csv

# Send request with the ZIP file
curl -X POST "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Download and unzip file test_archive.zip which has a single extract.csv file inside. What is the value in the \"answer\" column of the CSV file?" \
  -F "file=@test_archive.zip"

# Clean up
cd - > /dev/null
rm -rf "${TEMP_DIR}"