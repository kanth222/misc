import time
import csv
import sys
import requests
from bs4 import BeautifulSoup

# HTML file header (Bootstrap included)
html_header = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exam Topics Extracted Questions</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h2 class="text-center">Exam Topics Extracted Questions</h2>
"""

question_html = ''
failed_records = []
html_footer = "</body></html>"
csv_filename = 'matched_links2.csv'


def print_progress_bar(iteration, total, prefix='', suffix='', length=50):
    """
    Call in a loop to create a terminal progress bar.
    iteration : Current iteration (int)
    total     : Total iterations (int)
    prefix    : Prefix string (str)
    suffix    : Suffix string (str)
    length    : Character length of bar (int)
    """
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')


# Read CSV rows into a list so that we know the total number of records
with open(csv_filename, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

total_rows = len(rows)
print(f"Total records to process: {total_rows}\n")

# Process each row with a manual progress bar
for index, row in enumerate(rows, start=1):
    url = row['link']
    print(f"\nProcessing URL: {url}")
    
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/92.0.4515.159 Safari/537.36')
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.find(class_='sec-spacer')
            if element:
                outer_html = str(element)
                question_html += f"""
                    <div class="card p-3 mb-4">
                        <h4>Question {row['qn']}</h4>
                        {outer_html}
                    </div>
                    <hr class="my-4">
                    """
            else:
                print("No element with class 'sec-spacer' found.")
        else:
            print(f"Failed to retrieve page. Status code: {response.status_code}")
            failed_records.append({'url': url, 'qn': row['qn']})
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
    
    print("-" * 60)
    # Update the progress bar
    print_progress_bar(index, total_rows, prefix="Progress", suffix="Complete", length=50)
    
    # Pause between requests
    time.sleep(2)



# Write the collected HTML content to an output file
with open('cse.html', 'w', encoding='utf-8') as file:
    file.write(html_header)
    file.write(question_html)
    file.write(html_footer)

print("\nHTML content has been successfully written to 'cse.html'")
