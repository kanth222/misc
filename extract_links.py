#!/usr/bin/env python3
import sys
import re
import csv
from bs4 import BeautifulSoup




def get_file_names():
    # Try to obtain file names from arguments; if missing, ask the user.
    if len(sys.argv) >= 3:
        input_html = sys.argv[1]
        output_csv = sys.argv[2]
    else:
        input_html = input("Enter the input HTML file name (with path if needed): ").strip()
        output_csv = input("Enter the output CSV file name (with path if needed): ").strip()
    return input_html, output_csv

def main():
    input_html, output_csv = get_file_names()

    # Load the HTML file.
    try:
        with open(input_html, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except Exception as e:
        print(f"Error reading input file {input_html}: {e}")
        sys.exit(1)

    # Parse HTML using BeautifulSoup.
    soup = BeautifulSoup(html_content, 'html.parser')

    # Regex pattern for matching desired URLs.
    pattern = re.compile(r"https:\/\/www\.examtopics\.com\/discussions\/[A-Za-z0-9_-]+\/view\/\d+-.+$")

    # Extract matching <a> tags.
    matching_links = soup.find_all('a', href=pattern)
    
    rows = []
    for link in matching_links:
        href = link['href']

        # Skip the link if its span text is simply the homepage.
        span = link.find("span")
        if span:
            full_text = span.get_text(strip=True)
            if full_text == "https://www.examtopics.com":
                continue
        else:
            full_text = link.get_text(strip=True)
        
        # Extract question number using regex.
        question_number = None
        match = re.search(r"question\s+(\d+)", full_text, re.IGNORECASE)
        if match:
            question_number = int(match.group(1))
            print("Question number:", question_number)
        else:
            print("Question number not found for link:", href)
            # Optionally, you could skip or assign a default value; here we assign 0.
            question_number = 0

        rows.append([question_number, href, full_text])

    # Sort rows by question number from smallest to largest.
    rows.sort(key=lambda x: x[0])

    # Write rows to CSV.
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['qn', 'link', 'text'])  # Header row
            for row in rows:
                writer.writerow(row)
        print(f"CSV file '{output_csv}' created successfully.")
    except Exception as e:
        print(f"Error writing to CSV file {output_csv}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
