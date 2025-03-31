#!/bin/bash
# Test the API with a JSON sorting question

# Replace with your actual API URL
API_URL="http://localhost:8000/api/"

# Send request to sort a JSON array
curl -X POST "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F 'question=Sort this JSON array by age and then by name: [{"name":"Alice","age":55},{"name":"Bob","age":30},{"name":"Charlie","age":88},{"name":"David","age":36},{"name":"Emma","age":74},{"name":"Frank","age":20},{"name":"Grace","age":65},{"name":"Henry","age":63},{"name":"Ivy","age":22},{"name":"Jack","age":47},{"name":"Karen","age":87},{"name":"Liam","age":63},{"name":"Mary","age":87},{"name":"Nora","age":55},{"name":"Oscar","age":98},{"name":"Paul","age":60}]'