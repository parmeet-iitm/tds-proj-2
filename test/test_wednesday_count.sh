#!/bin/bash
# Test the API with a date calculation question (counting Wednesdays)

# Replace with your actual API URL
API_URL="http://localhost:8000/api/"

# Send request to count Wednesdays between two dates
curl -s -X POST "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "question=How many Wednesdays are there in the date range 1985-09-10 to 2011-10-02?"