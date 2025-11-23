# test_installation.py
import sys

print("="*60)
print("Testing Face Recognition Project Installation")
print("="*60)
print(f"\nPython: {sys.version}")
print(f"Location: {sys.executable}")
print(f"In venv: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
print("\n" + "="*60)

packages_to_test = {
    "numpy": "NumPy",
    "scipy": "SciPy", 
    "sklearn": "Scikit-learn",
    "cv2": "OpenCV",
    "PIL": "Pillow",
    "face_recognition": "Face Recognition",
    "dlib": "dlib",
    "tensorflow": "TensorFlow",
    "mtcnn": "MTCNN",
    "flask": "Flask",
    "flask_cors": "Flask-CORS"
}

success = 0
failed = []

for module, name in packages_to_test.items():
    try:
        if module == "sklearn":
            import sklearn
            version = sklearn.__version__
        elif module == "PIL":
            from PIL import Image
            import PIL
            version = PIL.__version__
        elif module == "cv2":
            import cv2
            version = cv2.__version__
        elif module == "mtcnn":
            from mtcnn import MTCNN
            version = "Loaded"
        elif module == "flask_cors":
            import flask_cors
            version = flask_cors.__version__ if hasattr(flask_cors, '__version__') else "Loaded"
        else:
            exec(f"import {module}")
            version = eval(f"{module}.__version__") if hasattr(eval(module), "__version__") else "Loaded"
        
        print(f"✓ {name:20s} {version}")
        success += 1
    except Exception as e:
        print(f"✗ {name:20s} FAILED: {str(e)[:50]}")
        failed.append(name)

print("\n" + "="*60)
print(f"Result: {success}/{len(packages_to_test)} packages loaded")
if failed:
    print(f"Failed: {', '.join(failed)}")
else:
    print("✓ All packages loaded successfully!")
print("="*60)

# Test MTCNN specifically
print("\nTesting MTCNN initialization...")
try:
    from mtcnn import MTCNN
    detector = MTCNN()
    print("✓ MTCNN detector initialized successfully!")
except Exception as e:
    print(f"✗ MTCNN initialization failed: {e}")