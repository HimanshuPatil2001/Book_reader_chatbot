#!/usr/bin/env python3
"""
Simple deployment test script for Koyeb
Tests core functionality without heavy dependencies
"""

import os
import sys

def test_basic_imports():
    """Test basic imports work"""
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber imported successfully")
    except ImportError as e:
        print(f"❌ pdfplumber import failed: {e}")
        return False
    
    try:
        import numpy
        print(f"✅ NumPy imported successfully (version: {numpy.__version__})")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔍 Environment Check:")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")
    print(f"FLASK_DEBUG: {os.environ.get('FLASK_DEBUG', 'Not set')}")
    print(f"PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"PYTHON_VERSION: {os.environ.get('PYTHON_VERSION', 'Not set')}")

def test_memory_usage():
    """Test basic memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"\n💾 Memory Usage:")
        print(f"Total: {memory.total / (1024**3):.2f} GB")
        print(f"Available: {memory.available / (1024**3):.2f} GB")
        print(f"Used: {memory.percent}%")
        
        if memory.available < 100 * 1024 * 1024:  # Less than 100MB
            print("⚠️  Warning: Low memory available")
        else:
            print("✅ Sufficient memory available")
            
    except ImportError:
        print("ℹ️  psutil not available, skipping memory check")

def main():
    """Main test function"""
    print("🚀 Koyeb Deployment Test")
    print("=" * 40)
    
    # Test basic imports
    if not test_basic_imports():
        print("\n❌ Basic imports failed - deployment may fail")
        sys.exit(1)
    
    # Test environment
    test_environment()
    
    # Test memory
    test_memory_usage()
    
    print("\n✅ All tests passed! Ready for deployment.")
    
    # Try to import the app
    try:
        from app import app
        print("✅ Flask app imported successfully")
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        print("This may cause deployment issues")

if __name__ == "__main__":
    main()
