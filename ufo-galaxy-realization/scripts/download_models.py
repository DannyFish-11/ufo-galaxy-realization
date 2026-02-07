import os
import sys
import urllib.request
import zipfile
import shutil

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print("Download complete.")

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

def main():
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    # Vosk Model (Small English)
    vosk_model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    vosk_zip_path = os.path.join(models_dir, "vosk-model.zip")
    vosk_extract_path = os.path.join(models_dir, "vosk-model-small-en-us-0.15")

    if not os.path.exists(vosk_extract_path):
        print("Vosk model not found. Downloading...")
        try:
            download_file(vosk_model_url, vosk_zip_path)
            extract_zip(vosk_zip_path, models_dir)
            os.remove(vosk_zip_path)
            print("✅ Vosk model installed successfully.")
        except Exception as e:
            print(f"❌ Failed to download Vosk model: {e}")
    else:
        print("✅ Vosk model already exists.")

if __name__ == "__main__":
    main()
