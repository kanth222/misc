import time
import csv
import sys
import requests
import os
import datetime
import argparse
from bs4 import BeautifulSoup


def main():

    parser = argparse.ArgumentParser(
        description="Output file name"
    )

    parser.add_argument(
        '--csvfile',
        help="The name of the file where csv links are avilable"
    )

    parser.add_argument(
        '--outfile',
        default='results',
        help="The name of the file to store the questions (default: results_date.html)."
    )

    args = parser.parse_args()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

    # Determine the script's directory
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Create folder name as today's date (e.g. "2023-10-05")
    folder_path = os.path.join(base_path, 'results')
    out_file_name = os.path.join(folder_path, args.outfile+'_'+today_date+'.html')

    # Check if the folder exists; if not, create itpam
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")


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

    html_footer = """</body>
    <script>
            document.addEventListener("DOMContentLoaded", function() {
                document.body.addEventListener("click", function (event){
                    if(event.target.classList.contains("reveal-solution")){
                        event.preventDefault();
        
                        let questionBody = event.target.closest(".question-body");
                        let discussionHeader = questionBody.closest(".discussion-header-container");
                        let commentsSection = discussionHeader.nextElementSibling;
        
                        let answerSection = questionBody.querySelector(".question-answer")
                        let metaDataSection = discussionHeader.querySelector(".discussion-meta-data");
                        let hideBtn = questionBody.querySelector(".hide-solution");
        
                        answerSection.classList.remove("d-none")
                        metaDataSection.classList.remove("d-none")
        
                        if(commentsSection && commentsSection.classList.contains("discussion-page-comments-section")){
                            commentsSection.classList.remove("d-none");
        
                            if(!commentsSection.querySelector(".hide-solution-bottom")){
                                let hideBtnBottom = document.createElement("a")
                                hideBtnBottom.href = "#"
                                hideBtnBottom.classList.add("btn", "btn-primary", "hide-solution-bottom")
                                hideBtnBottom.innerText = "Hide Answer"
                                commentsSection.appendChild(hideBtnBottom)
                            }
                        }
        
                        event.target.classList.add("d-none")
                        hideBtn.classList.remove("d-none")
        
        
                    }
                    if (event.target.classList.contains("hide-solution")) {
                        event.preventDefault();
        
                        let questionBody = event.target.closest(".question-body");
                        let discussionHeader = questionBody.closest(".discussion-header-container");
                        let commentsSection = discussionHeader.nextElementSibling;
        
                        let answerSection = questionBody.querySelector(".question-answer")
                        let metaDataSection = discussionHeader.querySelector(".discussion-meta-data");
                        let revealBtn = questionBody.querySelector(".reveal-solution");
        
                        answerSection.classList.add('d-none')
                        metaDataSection.classList.add('d-none')
                        
                        if(commentsSection && commentsSection.classList.contains("discussion-page-comments-section")){
                            commentsSection.classList.add("d-none");
        
                            let hideBtnBottom = commentsSection.querySelector(".hide-solution-bottom")
                            if(hideBtnBottom){
                                hideBtnBottom.remove()
                            }
                        }
                        
                        let hideBtns = questionBody.querySelectorAll(".hide-solution, .hide-solution-bottom")
                        hideBtns.forEach(btn => {
                            btn.classList.add("d-none")
                        });
                        revealBtn.classList.remove("d-none")
        
                    }
        
                    if (event.target.classList.contains("hide-solution-bottom")) {
                        event.preventDefault()
        
                        let commentsSection = event.target.parentElement
                        let questionBody = commentsSection.previousElementSibiling.querySelector(".question-body")
        
                        let discussionHeader = questionBody.closest(".discussion-header-container")
        
                        let answerSection = questionBody.querySelector(".question-answer")
                        let metaDataSection = discussionHeader.querySelector(".discussion-meta-data")
                        let revealBtn = questionBody.querySelector(".reveal-solution")
        
                        answerSection.classList.add("d-none")
                        metaDataSection.classList.add("d-none")
        
                        if (commentsSection && commentsSection.classList.contains("discussion-page-comments-section")) {
                            commentsSection.classList.add("d-none")
        
                            let hideBtnBottom = commentsSection.querySelector(".hide-solution-bottom");
                            if (hideBtnBottom) {
                                hideBtnBottom.remove()
                            }
        
                        }
        
                        let hideBtns = questionBody.querySelectorAll(".hide-solution, .hide-solution-bottom")
                        hideBtns.forEach(btn => {
                            btn.classList.add("d-none")
                        });
                        revealBtn.classList.remove("d-none")
        
                    }
                })
        
                document.querySelectorAll(".discussion-page-comments-section, .discussion-meta-data, .question-answer").forEach(section => {
                    section.classList.add("d-none")
                })
        
                document.querySelectorAll(".hide-solution").forEach(button => {
                    button.classList.add("d-none")
                });
                document.querySelectorAll(".contrib__ulimited").forEach(divs => {
                    divs.remove()
                });
            })
            </script>
    </html>"""

    # csv_filename = 'matched_links2.csv'

    csv_filename = args.csvfile

    if not csv_filename:
        csv_filename = input("Please provide the CSV file name (with extension): ").strip()
        if not csv_filename:
            print("CSV file name is required. Exiting.")
            sys.exit(1)


    question_html = ''
    failed_records = []


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


    def process_url(url, question_number):
        """
        Makes an HTTP GET request to the provided URL, parses it using Beautiful Soup,
        and if an element with class 'sec-spacer' is found, returns a formatted HTML
        string. Otherwise, returns None.
        
        Parameters:
            url (str): URL to process
            question_number (str/int): The question identifier to include in the HTML
            
        Returns:
            str or None: The formatted HTML string if element is found; otherwise, None.
        """
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/92.0.4515.159 Safari/537.36'
            )
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.find(class_='sec-spacer')
                if element:
                    outer_html = str(element)
                    formatted_html = f"""
                        <div class="card p-3 mb-4">
                            <h4>Question {question_number}</h4>
                            {outer_html}
                        </div>
                        <hr class="my-4">
                    """
                    return formatted_html
                else:
                    print(f"URL: {url} - No element with class 'sec-spacer' found.")
                    return None
            else:
                print(f"URL: {url} - Failed to retrieve page. Status code: {response.status_code}")

                return None
        except Exception as e:
            print(f"URL: {url} - An error occurred: {e}")
            return None


    # Read CSV rows into a list so that we know the total number of records
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    total_rows = len(rows)
    print(f"Total records to process: {total_rows}\n")

    # Process each row with a manual progress bar
    for index, row in enumerate(rows, start=1):
        url = row['link']
        question_number = row.get('qn', index)  # Use provided question number or default to index
        # print(f"\nProcessing URL: {url}")
        
        result = process_url(url, question_number)
        if result:
            question_html += result
        else:
            time.sleep(5)
            result22 = process_url(url,question_number)  
            if result22:
                question_html += result22
            else:
                failed_records.append({'url': url, 'qn': question_number})
        
        print("-" * 60)
        print_progress_bar(index, total_rows, prefix="Progress", suffix="Complete", length=50)
        
        # Pause between requests
        time.sleep(2)

    if failed_records:
        print("\nSome records failed:")
        for record in failed_records:
            # parsed_rec = JSON.parse(record)
            result = process_url(record['url'], record['qn'])
            if result:
                question_html += result
            else:
                print(f"URL: {record['url']} | Question: {record['qn']}")

    # Write the collected HTML content to an output file
    with open(out_file_name, 'w', encoding='utf-8') as file:
        file.write(html_header)
        file.write(question_html)
        file.write(html_footer)

    print(f"\nHTML content has been successfully written to ${out_file_name}")


if __name__ == "__main__":
    main()