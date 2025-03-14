import os
import zipfile
import shutil

zip_folder = "/mnt/shared/downloads/zip" 
output_folder = "/mnt/shared/downloads/"

os.makedirs(output_folder, exist_ok=True)

for zip_file in os.listdir(zip_folder):
    if zip_file.endswith(".zip"):
        zip_path = os.path.join(zip_folder, zip_file)
        
        temp_extract_path = os.path.join(zip_folder, "temp_extract")
        os.makedirs(temp_extract_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_path)
        
        for root, _, files in os.walk(temp_extract_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lstrip(".")  
                if not file_ext:
                    file_ext = "unknown" 
                
                ext_folder = os.path.join(output_folder, file_ext)
                os.makedirs(ext_folder, exist_ok=True)
                
                src_path = os.path.join(root, file)
                dest_path = os.path.join(ext_folder, file)
                shutil.move(src_path, dest_path)

        shutil.rmtree(temp_extract_path)

print("Unzipping and sorting complete!")
