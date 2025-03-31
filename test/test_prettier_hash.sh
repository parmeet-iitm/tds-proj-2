#!/bin/bash
# Test the API with a README.md prettier hash question

# Replace with your actual API URL
API_URL="http://localhost:8000/api/"

# First, create a simple README.md file for testing
cat > test_readme.md << 'EOF'
# Test Heading

This is a sample README file.

## Features

* Feature 1
* Feature 2

```javascript
console.log("Hello World");
```

> This is a blockquote

| Column 1 | Column 2 |
|----------|----------|
| Item 1   | Item 2   |
EOF

# Send request with the README.md file
curl -X POST "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Download README.md. In the directory where you downloaded it, make sure it is called README.md, and run npx -y prettier@3.4.2 README.md | sha256sum. What is the output of the command?" \
  -F "file=@test_readme.md"

# Clean up
rm test_readme.md