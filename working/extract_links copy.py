#!/usr/bin/env python3
import sys
import re
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def url_to_regex(url: str) -> str:
    # Basic sanitization: remove whitespace
    url = url.strip()

    # Validate URL structure
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid URL format.")

    # Escape and convert digits to regex pattern
    escaped_url = re.escape(url)
    pattern = re.sub(r'(?<!\\)(\d+)', r'\\d+', escaped_url)
    return pattern

def get_inputs():
    # Accept input HTML, output CSV, and sample URL
    if len(sys.argv) >= 4:
        input_html = sys.argv[1].strip()
        output_csv = sys.argv[2].strip()
        sample_url = sys.argv[3].strip()
    else:
        input_html = input("Enter the input HTML file name (with path if needed): ").strip()
        output_csv = input("Enter the output CSV file name (with path if needed): ").strip()
        sample_url = input("Enter a sample URL to build regex from: ").strip()
    return input_html, output_csv, sample_url

def main():
    try:
        input_html, output_csv, sample_url = get_inputs()
        regex_pattern = url_to_regex(sample_url)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Read HTML file
    try:
        with open(input_html, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except Exception as e:
        print(f"Error reading input file '{input_html}': {e}")
        sys.exit(1)

    soup = BeautifulSoup(html_content, 'html.parser')
    pattern = re.compile(regex_pattern)
    print(regex_pattern)
    matching_links = soup.find_all('a', href=pattern)

    rows = []
    for link in matching_links:
        href = link['href']

        span = link.find("span")
        full_text = span.get_text(strip=True) if span else link.get_text(strip=True)

        # Skip homepage links
        if full_text == "https://www.examtopics.com":
            continue

        # Extract question number
        match = re.search(r"question\s+(\d+)", full_text, re.IGNORECASE)
        question_number = int(match.group(1)) if match else 0

        rows.append([question_number, href, full_text])

    rows.sort(key=lambda x: x[0])

    # Write to CSV
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['qn', 'link', 'text'])
            writer.writerows(rows)
        print(f"CSV file '{output_csv}' created successfully.")
    except Exception as e:
        print(f"Error writing to CSV file '{output_csv}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
