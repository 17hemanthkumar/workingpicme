"""
Fix DNN model by re-downloading with correct parameters
"""

import os
import urllib.request
import sys

def download_file(url, destination):
    """Download a file with progress indicator"""
    print(f"Downloading {os.path.basename(destination)}...")
    
    def reporthook(count, block_size, total_size):
        if total_size > 0:
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

# Delete existing model files
models_dir = "models"
prototxt = os.path.join(models_dir, 'deploy.prototxt')
caffemodel = os.path.join(models_dir, 'res10_300x300_ssd_iter_140000.caffemodel')

print("Removing old model files...")
if os.path.exists(prototxt):
    os.remove(prototxt)
    print(f"✓ Removed {prototxt}")

if os.path.exists(caffemodel):
    os.remove(caffemodel)
    print(f"✓ Removed {caffemodel}")

# Re-download
print("\nRe-downloading DNN models...")
base_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/"
caffemodel_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"

download_file(base_url + "deploy.prototxt", prototxt)
download_file(caffemodel_url, caffemodel)

print("\n✓ DNN models re-downloaded. Please test again.")
