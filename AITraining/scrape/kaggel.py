import subprocess
import os

def list_and_download_datasets(search_term, file_types, download_dir, max_results=10):
    """
    Search for datasets on Kaggle, filter by file types, and download the selected datasets.
    
    :param search_term: The search term for finding datasets on Kaggle.
    :param file_types: List of file types to filter datasets by (e.g., ['csv', 'jpg', 'txt']).
    :param download_dir: Directory where the datasets will be downloaded.
    :param max_results: The maximum number of datasets to return and download.
    :return: List of dataset names that were downloaded.
    """
    try:
        # Create the download directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)

        # Step 1: Search Kaggle datasets using the Kaggle CLI
        result = subprocess.run(
            ['kaggle', 'datasets', 'list', '-s', search_term, '--max', str(max_results)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        datasets = result.stdout.decode('utf-8').splitlines()
        downloaded_datasets = []

        # Step 2: Filter datasets by file types and download them
        for dataset in datasets:
            dataset_name = dataset.split()[0]  # Extract dataset name (first part of each line)
            print(f"Checking dataset: {dataset_name}")

            # Step 3: Get the files associated with the dataset
            dataset_files_result = subprocess.run(
                ['kaggle', 'datasets', 'metadata', dataset_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            dataset_metadata = dataset_files_result.stdout.decode('utf-8')

            # Check if any of the files have the specified file types
            if any(file_type in dataset_metadata for file_type in file_types):
                print(f"Downloading dataset: {dataset_name}")
                # Download the dataset
                subprocess.run(['kaggle', 'datasets', 'download', dataset_name, '-p', download_dir, '--unzip'])
                downloaded_datasets.append(dataset_name)

        return downloaded_datasets

    except Exception as e:
        print(f"Error searching for and downloading datasets: {e}")
        return []

def main():
    search_term = 'image' 
    file_types = [
    "pdf", "png", "tiff", "zip", "7z", "rar", "iso", 
    "tar", "ps", "mp4", "ar", "bmp", "bz2", "cab", "flac", 
    "gif", "gz", "ico", "jpg", "ogg", "psd", "rtf", "bpg", 
    "java", "pcap", "xz"
]
    download_dir = '/mnt/shared' 
    
    downloaded_datasets = list_and_download_datasets(search_term, file_types, download_dir, max_results=10)

    if downloaded_datasets:
        print(f"Downloaded datasets: {downloaded_datasets}")
    else:
        print(f"No datasets found for search term: {search_term}")

if __name__ == "__main__":
    main()
