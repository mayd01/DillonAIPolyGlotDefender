import os
import requests

GITHUB_TOKEN = "REMOVEDydOkFdxaLqEsU7bEq4gQvKhkEoBm5Q0M0ePT"
GITHUB_API_URL = "https://api.github.com/search/code"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_github_files(extension, max_results=5000):
    """
    Search GitHub for files of a specific extension in all repositories.
    """
    query = f"extension:{extension}"
    params = {"q": query, "per_page": max_results}
    
    response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['items']
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

def download_github_file(file_url, download_path):
    """
    Download a file from GitHub using its URL.
    """
    response = requests.get(file_url, headers=HEADERS)
    if response.status_code == 200:
        with open(download_path, 'wb') as f:
            f.write(response.content)
            print(f"Downloaded file: {download_path}")
    else:
        print(f"Failed to download file: {file_url}")

if __name__ == "__main__":
    extensions = ["zip", "rar", "jpg", "png", "pdf"]
    for ext in extensions:
        print(f"Searching GitHub for {ext} files...")
        files = get_github_files(ext)
        if files:
            os.makedirs(f"downloads/{ext}", exist_ok=True)
            for file in files:
                file_url = file['html_url']
                file_name = file_url.split('/')[-1] + f".{ext}"
                download_path = os.path.join("downloads", ext, file_name)
                download_github_file(file_url, download_path)
        else:
            print(f"No {ext} files found on GitHub.")
