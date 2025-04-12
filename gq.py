import time
import csv
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


# Open the CSV file and create a reader object
with open(csv_filename, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Assuming the CSV header for the URLs is "A"
    for row in reader:
        url = row['link']
        print(f"Processing URL: {url}")
        
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
                    # print("Element found with class 'sec-spacer':")
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
                failed_records += {url, row['qn']}
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
        
        print("-" * 60)
        time.sleep(2)


with open('cse.html', 'w', encoding='utf-8') as file:
    file.write(html_header)

    file.write(question_html)

    file.write(html_footer)



# print(f"HTML content has been successfully written to {output_file}")