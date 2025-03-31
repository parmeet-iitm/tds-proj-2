"""
Simple test script to validate the TDS Assignment Solver API.
Run this script to test if the API is working correctly.
"""

import requests
import json
import os
import tempfile
import zipfile
import pandas as pd
from pathlib import Path
import argparse

# Default API URL (update this when deployed)
DEFAULT_API_URL = "http://localhost:8000/api/"


def test_api_with_question(api_url, question, file_path=None):
    """
    Test the API with a specific question and optional file.

    Args:
        api_url: The API endpoint URL
        question: The question to test with
        file_path: Optional path to a file to upload
    """
    print(f"\n🧪 Testing with question: {question}")

    if file_path:
        print(f"📁 Using file: {file_path}")

    # Prepare the request
    data = {"question": question}
    files = {"file": None}

    if file_path:
        # Open the file for uploading
        file_name = os.path.basename(file_path)
        files = {"file": (file_name, open(file_path, "rb"))}

    try:
        # Send the request
        response = requests.post(
            api_url,
            data=data,
            files=files
        )

        # Print the result
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Answer: {result['answer']}")
            return result['answer']
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None

    finally:
        # Close file if it was opened
        if file_path and "file" in files and files["file"] is not None:
            files["file"][1].close()


def create_test_csv_file():
    """Create a test CSV file for testing CSV extraction questions."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_csv:
        temp_csv.write(b"id,answer,value\n1,test_answer,42\n")
        temp_csv_path = temp_csv.name

    # Create a temporary ZIP file containing the CSV
    zip_path = Path(temp_csv_path).with_suffix('.zip')

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(temp_csv_path, arcname="extract.csv")

    # Clean up CSV file
    os.remove(temp_csv_path)

    return zip_path


def run_standard_tests(api_url):
    """Run a set of standard tests for the API."""
    print("🚀 Running standard tests for the TDS Assignment Solver API")
    print(f"🔗 API URL: {api_url}")

    # Test 1: Wednesday counting question
    wednesday_question = "How many Wednesdays are there in the date range 1985-09-10 to 2011-10-02?"
    wednesday_result = test_api_with_question(api_url, wednesday_question)

    # Test 2: JSON sorting question
    json_question = 'Sort this JSON array by age: [{"name":"Alice","age":55},{"name":"Bob","age":30},{"name":"Charlie","age":55}]'
    json_result = test_api_with_question(api_url, json_question)

    # Test 3: CSV extraction question
    csv_question = "Download and unzip file which has a single extract.csv file inside. What is the value in the \"answer\" column of the CSV file?"

    try:
        # Create test file
        zip_path = create_test_csv_file()

        # Test with file
        csv_result = test_api_with_question(api_url, csv_question, zip_path)

    finally:
        # Clean up
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)

    # Test 4: Prettier hash question
    prettier_question = "Download README.md. In the directory where you downloaded it, make sure it is called README.md, and run npx -y prettier@3.4.2 README.md | sha256sum. What is the output of the command?"

    # Create a simple README.md file for testing
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
        temp_file.write(b"# Test Heading\n\nThis is a test README file.\n* Bullet point\n* Another bullet point\n")
        readme_path = temp_file.name

    try:
        # Test with file
        prettier_result = test_api_with_question(api_url, prettier_question, readme_path)
    finally:
        # Clean up
        if os.path.exists(readme_path):
            os.remove(readme_path)

    # Test 5: Google Sheets formula question
    sheets_question = "In Google Sheets, what is the result of this formula: =SUM(ARRAY_CONSTRAIN(SEQUENCE(100, 100, 0, 8), 1, 10))?"
    sheets_result = test_api_with_question(api_url, sheets_question)

    # Summary
    print("\n📊 Test Summary:")
    print(f"Wednesday counting: {'✅ Pass' if wednesday_result else '❌ Fail'}")
    print(f"JSON sorting: {'✅ Pass' if json_result else '❌ Fail'}")
    print(f"CSV extraction: {'✅ Pass' if csv_result else '❌ Fail'}")
    print(f"Prettier hash: {'✅ Pass' if prettier_result else '❌ Fail'}")
    print(f"Google Sheets formula: {'✅ Pass' if sheets_result else '❌ Fail'}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Test the TDS Assignment Solver API")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="API endpoint URL")
    parser.add_argument("--question", help="Specific question to test")
    parser.add_argument("--file", help="Path to file to upload with the question")

    args = parser.parse_args()

    # If specific question provided, test just that
    if args.question:
        test_api_with_question(args.url, args.question, args.file)
    else:
        # Otherwise run standard tests
        run_standard_tests(args.url)

    print("\n🏁 Testing complete!")


if __name__ == "__main__":
    main()