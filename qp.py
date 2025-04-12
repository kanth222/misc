from bs4 import BeautifulSoup
import re
import csv

# sample_url = "https://www.examtopics.com/discussions/google/view/75711-exam-professional-cloud-security-engineer-topic-1-question/"

# Load your HTML file
with open('def.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Regex pattern for matching desired URLs
# pattern = re.compile(r'https://www\.examtopics\.com/discussions/google/view/\d+-exam-professional-cloud-security-engineer-topic-1-question/')

# pattern = re.compile(r'https://www\.examtopics\.com/discussions/cyberark/view/\d+-exam-pam-def-topic-1-question-\d+-discussion/')

pattern = re.compile("https:\/\/www\.examtopics\.com\/discussions\/[A-Za-z0-9_-]+\/view\/\d+-.+$")


# Extract matching <a> tags
matching_links = soup.find_all('a', href=pattern)

# Write to CSV
with open('pam-def-mod.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['qn', 'link', 'text'])  # Header row

    for link in matching_links:
        full_text = ''
        question_number = 0
        href = link['href']

        span = link.find("span")
        if span.get_text(strip=True) == "https://www.examtopics.com":
            continue

        if span:
            full_text = span.get_text(strip=True)
        else:
            full_text = span.get_text(strip=True)
        # text = link.get_text(strip=True)
        match = re.search(r"question\s+(\d+)", full_text)
        if match:
            question_number = match.group(1)
            print("Question number:", question_number)
        else:
            print("Question number not found.")
        writer.writerow([question_number, href, full_text])

print("CSV file 'pam_def.csv' created successfully.")


