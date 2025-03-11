import os
import requests

GITHUB_TOKEN = "REMOVEDydOkFdxaLqEsU7bEq4gQvKhkEoBm5Q0M0ePT"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_github_files(extension, max_results=5000):
    """
    Search GitHub for files of a specific extension.
    """
    query = f"extension:{extension}"
    url = f"https://api.github.com/search/code?q={query}&per_page={max_results}"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

def get_default_branch(repo_full_name):
    """
    Fetch the default branch of a repository.
    """
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("default_branch", "main")
    return "main"

def get_lfs_download_url(repo_full_name, file_path):
    """
    Fetch the actual file download URL if stored in Git LFS.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return data.get("download_url")  # Actual file URL
    return None

def file_size_check(url):
    """
    Check if the file size is larger than 256 bytes before downloading.
    """
    response = requests.head(url, headers=HEADERS)
    if response.status_code == 200:
        file_size = int(response.headers.get('Content-Length', 0))
        return file_size > 256
    return False

def download_github_file(file_info, download_path):
    """
    Download a file from GitHub using the correct branch.
    Detects if the file is stored in Git LFS and fetches it.
    """
    repo_full_name = file_info['repository']['full_name']
    file_path = file_info['path']

    # Detect the default branch
    branch = get_default_branch(repo_full_name)

    # Try to download from the raw GitHub content URL
    raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/{branch}/{file_path}"
    
    # Check if the file size is larger than 256 bytes
    if not file_size_check(raw_url):
        print(f"File {file_info['name']} is too small (< 256 bytes), skipping download.")
        return

    response = requests.get(raw_url, headers=HEADERS)

    if response.status_code == 200:
        content = response.content

        # Check if it's a Git LFS pointer file
        if b"version https://git-lfs.github.com/spec/v1" in content:
            print(f"File {file_info['name']} is stored using Git LFS. Fetching actual file...")
            actual_url = get_lfs_download_url(repo_full_name, file_path)
            if actual_url:
                response = requests.get(actual_url, headers=HEADERS)
                if response.status_code == 200:
                    content = response.content
                else:
                    print(f"Failed to download LFS file: {response.status_code}")
                    return
            else:
                print("Could not determine LFS file download URL.")
                return
        
        with open(download_path, 'wb') as f:
            f.write(content)
            print(f"Downloaded: {download_path}")
    else:
        print(f"Failed to download: {raw_url} (Status: {response.status_code})")

if __name__ == "__main__":
    file_signatures = [
        "pdf", "png", "tiff", "zip", "7z", "rar", "iso", 
        "tar", "ps", "mp4", "ar", "bmp", "bz2", "cab", "flac", 
        "gif", "gz", "ico", "jpg", "ogg", "psd", "rtf", "bpg", 
        "java", "pcap", "xz"
    ]

    extensions = file_signatures
    for ext in extensions:
        print(f"Searching GitHub for {ext} files...")
        files = get_github_files(ext)
        if files:
            os.makedirs(f"/mnt/shared/downloads/{ext}", exist_ok=True)
            for file_info in files:
                file_name = file_info['name']
                download_path = os.path.join("/mnt/shared/downloads", ext, file_name)
                download_github_file(file_info, download_path)
        else:
            print(f"No {ext} files found on GitHub.")
