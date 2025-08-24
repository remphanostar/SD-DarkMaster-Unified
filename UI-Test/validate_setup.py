#!/usr/bin/env python3
"""
Quick validation script to check if everything is ready for CivitAI testing
"""

import sys
import os
from pathlib import Path

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.7+")
        return False

def check_imports():
    """Check required imports"""
    print("\n📦 Checking required packages...")
    required_packages = [
        ("requests", "requests"),
        ("streamlit", "streamlit"),
        ("pathlib", "pathlib"),
        ("json", "json"),
        ("datetime", "datetime")
    ]
    
    all_good = True
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {display_name} - OK")
        except ImportError:
            print(f"   ❌ {display_name} - Missing")
            all_good = False
    
    return all_good

def check_api_connectivity():
    """Check CivitAI API connectivity"""
    print("\n🌐 Checking CivitAI API connectivity...")
    try:
        import requests
        response = requests.get("https://civitai.com/api/v1/models?limit=1", timeout=10)
        if response.status_code == 200:
            print("   ✅ CivitAI API accessible")
            return True
        else:
            print(f"   ⚠️ CivitAI API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ CivitAI API error: {e}")
        return False

def check_files():
    """Check if test files exist"""
    print("\n📁 Checking test files...")
    required_files = [
        "civitai_test_basic.py",
        "civitai_manual_test.py",
        "run_civitai_tests.sh"
    ]
    
    all_good = True
    for filename in required_files:
        if Path(filename).exists():
            print(f"   ✅ {filename} - Found")
        else:
            print(f"   ❌ {filename} - Missing")
            all_good = False
    
    return all_good

def check_permissions():
    """Check file permissions and write access"""
    print("\n🔒 Checking permissions...")
    
    # Check current directory write access
    try:
        test_file = Path("test_write_permission.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ Write permissions - OK")
        return True
    except Exception as e:
        print(f"   ❌ Write permissions - Error: {e}")
        return False

def main():
    """Run all validation checks"""
    print("🔍 CivitAI Setup Validation")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python),
        ("Required Packages", check_imports),
        ("API Connectivity", check_api_connectivity),
        ("Test Files", check_files),
        ("Permissions", check_permissions)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        result = check_func()
        if result:
            passed += 1
    
    print("\n" + "=" * 40)
    print("📊 Validation Summary")
    print("=" * 40)
    print(f"Passed: {passed}/{total} checks")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Ready to run CivitAI tests")
        print("\n🚀 Next steps:")
        print("   1. Run manual tests: python3 civitai_manual_test.py")
        print("   2. Run Streamlit app: streamlit run civitai_test_basic.py")
        print("   3. Or use the helper: ./run_civitai_tests.sh")
        return True
    else:
        print(f"\n⚠️ {total - passed} checks failed")
        print("🔧 Fix the issues above before proceeding")
        
        if passed >= total - 1:
            print("💡 Most checks passed - minor issues only")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)