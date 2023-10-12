import os
import requests
from bs4 import BeautifulSoup

PDF_FOLDER_PATH = os.getenv(
    'PDF_FOLDER_PATH',
    '/Users/juancparra/Documents/llm-agent-biomedical/pdf_files/'
)


def download_pdf(base_url, path):
    # Send HTTP request and fetch the content
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all 'a' tags with href attribute
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']

        if href.endswith('/') and not href.startswith('/'):
            # This is a folder, recurse into this folder
            print(f"Found subfolder: {base_url + href}")
            download_pdf(base_url + href, path + href)
        elif href.endswith('.pdf'):
            # This is a PDF file, download it
            pdf_url = base_url + href
            print(f"Downloading PDF: {pdf_url}")

            # Check if file already exists
            if not os.path.isfile(path + href):
                try:
                    # Send request to download the pdf file with a timeout
                    pdf_response = requests.get(pdf_url, timeout=90)

                    # Create directory if not exists
                    os.makedirs(os.path.dirname(path), exist_ok=True)

                    # Write the content of the response to a file
                    with open(path + href, 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"Saved PDF: {path + href}")
                except requests.exceptions.Timeout:
                    print(f"Timeout reached while downloading {pdf_url}."
                          " Moving on to next file.")
            else:
                print(
                    f"File already exists: {path + href}. Skipping download."
                )


if __name__ == "__main__":
    # Start from the base URL
    download_pdf(
        'https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/',
        '/Users/juancparra/Documents/llm-agent-biomedical/pdf_files/'
    )
