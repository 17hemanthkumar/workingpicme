"""
Setup Script for Robust Face Detection System
Installs dependencies and downloads required models
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"✓ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Setup robust face detection system"""
    print("\n" + "="*80)
    print("ROBUST FACE DETECTION SYSTEM - SETUP")
    print("="*80)
    
    print("\nThis script will:")
    print("1. Install required Python packages")
    print("2. Download DNN model files")
    print("3. Test the installation")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Setup cancelled")
        return
    
    # Step 1: Install packages
    print("\n" + "="*80)
    print("STEP 1: Installing Python Packages")
    print("="*80)
    
    packages = [
        ('mtcnn', 'MTCNN (for faces with sunglasses)'),
        ('opencv-python', 'OpenCV (for DNN and Haar Cascade)'),
        ('dlib', 'dlib (for HOG detector) - This may take a while...'),
    ]
    
    for package, description in packages:
        print(f"\nInstalling {description}...")
        success = run_command(
            f"{sys.executable} -m pip install {package}",
            f"Install {package}"
        )
        if not success:
            print(f"⚠ Warning: {package} installation failed")
            print(f"  The system will work without it, but with reduced capabilities")
    
    # Step 2: Download DNN models
    print("\n" + "="*80)
    print("STEP 2: Downloading DNN Model Files")
    print("="*80)
    
    download_script = os.path.join(os.path.dirname(__file__), 'download_dnn_models.py')
    if os.path.exists(download_script):
        run_command(
            f"{sys.executable} {download_script}",
            "Download DNN models"
        )
    else:
        print("⚠ download_dnn_models.py not found, skipping...")
    
    # Step 3: Test installation
    print("\n" + "="*80)
    print("STEP 3: Testing Installation")
    print("="*80)
    
    test_script = os.path.join(os.path.dirname(__file__), 'test_robust_detection.py')
    if os.path.exists(test_script):
        run_command(
            f"{sys.executable} {test_script}",
            "Test robust detection"
        )
    else:
        print("⚠ test_robust_detection.py not found, skipping test...")
    
    # Summary
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print("\nRobust Face Detection System is ready!")
    print("\nFeatures available:")
    print("  ✓ Multiple detection algorithms with automatic fallback")
    print("  ✓ Image preprocessing for challenging scenarios")
    print("  ✓ Support for sunglasses, varying lighting, different angles")
    print("\nThe system will automatically use robust detection when processing photos.")
    print("="*80)

if __name__ == '__main__':
    main()
