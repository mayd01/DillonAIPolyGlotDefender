import os
from kaggle.api.kaggle_api_extended import KaggleApi

# Kaggle configuration
KAGGLE_API = KaggleApi()
KAGGLE_API.authenticate()

def download_kaggle_dataset(dataset_name, download_path="downloads"):
    """
    Download a dataset from Kaggle by its name.
    """
    print(f"Downloading {dataset_name} from Kaggle...")
    try:
        KAGGLE_API.dataset_download_files(dataset_name, path=download_path, unzip=True)
        print(f"Downloaded dataset {dataset_name} to {download_path}")
    except Exception as e:
        print(f"Error downloading {dataset_name}: {str(e)}")

if __name__ == "__main__":
    # List of Kaggle dataset names that are relevant to the extensions you're looking for
    dataset_names = ["zip", "rar", "mp4", "jpg", "png"]
    for dataset in dataset_names:
        download_kaggle_dataset(dataset)
