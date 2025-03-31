#!/bin/bash
# Test the API with a Google Sheets formula question

# Replace with your actual API URL
API_URL="http://localhost:8000/api/"

# Send request for a Google Sheets formula question
curl -X POST "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Type this formula into Google Sheets. =SUM(ARRAY_CONSTRAIN(SEQUENCE(100, 100, 0, 8), 1, 10)). What is the result?"