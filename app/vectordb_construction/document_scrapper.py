import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def download_pdf(base_url: str, path: str) -> None:
    """
    This function is used to download all PDF files from a given URL. It recursively
    searches through the website's directories for PDF files and downloads them.

    Args:
        base_url (str): The base URL of the website from which to download PDFs.
        path (str): The local directory where the downloaded PDFs should be saved.

    Returns:
        None
    """
    # Send HTTP request to the base URL and parse the content using BeautifulSoup
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all 'a' tags with href attribute in the parsed HTML
    links = soup.find_all("a", href=True)

    # Iterate over each link
    for link in links:
        href = link["href"]

        # Check if the link is a subdirectory on the website
        if href.endswith("/") and not href.startswith("/"):
            # Recurse into this subdirectory and look for more PDFs
            print(f"Found subfolder: {base_url + href}")
            download_pdf(base_url + href, f"{path}/{href}")

        # Check if the link is a PDF file
        elif href.endswith(".pdf"):
            # Construct the full URL of the PDF file
            pdf_url = base_url + href
            print(f"Downloading PDF: {pdf_url}")

            # Check if the PDF file already exists locally
            if not os.path.isfile(f"{path}/{href}"):
                try:
                    # Send a GET request to download the PDF file
                    # If the server does not respond within 90 seconds, raise a Timeout
                    # exception
                    pdf_response = requests.get(pdf_url, timeout=90)

                    # Create the local directory if it does not exist
                    os.makedirs(os.path.dirname(path), exist_ok=True)

                    # Write the content of the response to a local file
                    with open(f"{path}/{href}", "wb") as f:
                        f.write(pdf_response.content)
                    print(f"Saved PDF: {path}/{href}'")
                except requests.exceptions.Timeout:
                    # If a Timeout exception is raised, skip this file and move on to
                    # the next one
                    print(
                        f"Timeout reached while downloading {pdf_url}. Moving on to"
                        " next file."
                    )
            else:
                # If the file already exists locally, skip the download
                print(f"File already exists: '{path}/{href}'. Skipping download.")


if __name__ == "__main__":
    load_dotenv()

    ONLINE_LIBRARY_PATH = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/"

    PDF_FOLDER_PATH = os.getenv(
        "PDF_FOLDER_PATH", "/Users/juancparra/Documents/llm-agent-biomedical/pdf_files/"
    )
    # Start from the base URL
    download_pdf(ONLINE_LIBRARY_PATH, PDF_FOLDER_PATH)
