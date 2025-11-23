"""
Download DNN Face Detection Models
Downloads the required model files for OpenCV DNN face detector
"""

import os
import urllib.request
import sys

def download_file(url, destination):
    """Download a file with progress indicator"""
    print(f"Downloading {os.path.basename(destination)}...")
    
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r{percent}% ")
        sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, destination, reporthook)
        print("\n✓ Download complete")
        return True
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False

def main():
    """Download DNN model files"""
    print("=" * 80)
    print("DNN Face Detection Model Downloader")
    print("=" * 80)
    
    # Create models directory
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    print(f"\nModels directory: {models_dir}")
    
    # Model URLs
    base_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/"
    
    files = {
        'deploy.prototxt': base_url + 'deploy.prototxt',
        'res10_300x300_ssd_iter_140000.caffemodel': 
            'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel'
    }
    
    # Download each file
    success_count = 0
    for filename, url in files.items():
        destination = os.path.join(models_dir, filename)
        
        # Check if file already exists
        if os.path.exists(destination):
            print(f"\n{filename} already exists, skipping...")
            success_count += 1
            continue
        
        print(f"\nDownloading {filename}...")
        if download_file(url, destination):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    if success_count == len(files):
        print("✓ All model files downloaded successfully!")
        print("✓ DNN face detector is ready to use")
    else:
        print(f"⚠ Downloaded {success_count}/{len(files)} files")
        print("Some files may need to be downloaded manually")
    print("=" * 80)

if __name__ == '__main__':
    main()
