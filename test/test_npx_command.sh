#!/bin/bash
# Test the API with a command execution question (npx)

# Replace with your actual API URL
API_URL="http://localhost:8000/api/"

# Create a test file
cat > test_file.md << 'EOF'
#  Badly  Formatted  Markdown

*  This is an uneven list
* With inconsistent spacing
   *    And weird indentation

>This quote has no space
>   This one has too many

mi1qQ8mdJEAIFx9sU bzM yRIPL n  KAhKUKXIedoU eF9k  q  B  K wW wtg4 8 WH gjB  WO YEhE LRb 3CecF6I5nMAU dBi9  zoWw4EZLHiv ksNw  X 75Dvw0FiUoXzG iFmfaHW7Oe 86sjiL WLCmz Y8 OMd lovkryz5VA7G0bY 7W  F
I4OaL  oXDFT5Amm cebPYUd5Dc 2 fIMBu xK 8pFbvNx w ljsT6QRw cLRqpHvpGE EEf hmRJp VK  QJ3bZ0AQ  9Vs6UVfx3pZ H
EOF

# Send request to run a command
curl -X POST "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Let's make sure you know how to use npx and prettier. Download test_file.md. In the directory where you downloaded it, make sure it is called test_file.md, and run npx -y prettier@3.4.2 test_file.md | sha256sum. What is the output of the command?" \
  -F "file=@test_file.md"

# Clean up
rm test_file.md