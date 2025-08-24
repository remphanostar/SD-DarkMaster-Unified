#!/usr/bin/env python3
"""
CivitAI Manual Test Script
Run this to test the basic CivitAI functionality step by step
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime
import time

# ===============================
# BASIC CIVITAI API CLASS
# ===============================

class CivitAIBasic:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
        self.headers = {}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def search_models(self, query="", limit=10, sort="Highest Rated", model_type=None):
        """Basic model search"""
        
        params = {
            'limit': limit,
            'sort': sort
        }
        
        if query:
            params['query'] = query
            
        if model_type:
            params['types'] = [model_type]
            
        if self.api_key:
            params['token'] = self.api_key
        
        try:
            print(f"🔍 Searching CivitAI with params: {params}")
            
            response = requests.get(
                f"{self.base_url}/models",
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            print(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data.get('items', []))} models")
                return data.get('items', [])
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return []
    
    def get_model_details(self, model_id):
        """Get detailed model information"""
        
        params = {}
        if self.api_key:
            params['token'] = self.api_key
            
        try:
            response = requests.get(
                f"{self.base_url}/models/{model_id}",
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get model details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting model details: {e}")
            return None
    
    def download_model_file(self, download_url, filename, download_dir="downloads"):
        """Download a model file"""
        
        # Create download directory
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)
        
        file_path = download_path / filename
        
        try:
            print(f"📥 Starting download: {filename}")
            print(f"🔗 URL: {download_url}")
            
            # Stream download with progress
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"📊 Progress: {progress:.1f}% ({downloaded:,} / {total_size:,} bytes)")
            
            print(f"✅ Download complete: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

# ===============================
# MANUAL TESTING FUNCTIONS
# ===============================

def test_api_connection():
    """Test 1: Basic API connection"""
    print("\n" + "="*60)
    print("🔧 TEST 1: API Connection")
    print("="*60)
    
    try:
        # Initialize without API key first
        civitai = CivitAIBasic()
        print(f"✅ CivitAI class initialized")
        print(f"🔗 Base URL: {civitai.base_url}")
        print(f"🔑 API Key: {'Set' if civitai.api_key else 'Not Set (Public Access)'}")
        return civitai
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return None

def test_basic_search(civitai):
    """Test 2: Basic search functionality"""
    print("\n" + "="*60)
    print("🔍 TEST 2: Basic Search")
    print("="*60)
    
    if not civitai:
        print("❌ Cannot test - API not initialized")
        return None
    
    # Search for realistic models
    search_results = civitai.search_models(
        query="realistic",
        limit=5,
        sort="Highest Rated",
        model_type="Checkpoint"
    )
    
    print(f"\n📊 Search Results: {len(search_results)} models found")
    
    if search_results:
        print("\n🎨 Top Models:")
        for i, model in enumerate(search_results[:3], 1):
            print(f"\n{i}. {model.get('name', 'Unknown')}")
            print(f"   👤 Creator: {model.get('creator', {}).get('username', 'Unknown')}")
            print(f"   📥 Downloads: {model.get('stats', {}).get('downloadCount', 0):,}")
            print(f"   ⭐ Rating: {model.get('stats', {}).get('rating', 0):.1f}/5")
            print(f"   🆔 ID: {model.get('id')}")
        
        return search_results
    else:
        print("❌ No results found")
        return None

def test_model_details(civitai, search_results):
    """Test 3: Get model details"""
    print("\n" + "="*60)
    print("📖 TEST 3: Model Details")
    print("="*60)
    
    if not search_results:
        print("❌ Cannot test - No search results")
        return None
    
    # Use first search result
    test_model = search_results[0]
    model_id = test_model['id']
    
    print(f"📖 Getting details for: {test_model['name']}")
    print(f"🆔 Model ID: {model_id}")
    
    model_details = civitai.get_model_details(model_id)
    
    if model_details:
        print("✅ Model details retrieved!")
        
        versions = model_details.get('modelVersions', [])
        print(f"\n📦 Available versions: {len(versions)}")
        
        if versions:
            latest_version = versions[0]
            print(f"\n🏷️ Latest Version: {latest_version.get('name', 'Unnamed')}")
            print(f"🎯 Base Model: {latest_version.get('baseModel', 'Unknown')}")
            
            files = latest_version.get('files', [])
            print(f"\n📁 Available files: {len(files)}")
            
            for i, file_info in enumerate(files[:3], 1):
                filename = file_info.get('name', 'Unknown')
                file_size = file_info.get('sizeKB', 0)
                file_type = file_info.get('type', 'Unknown')
                
                # Convert size
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f} GB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.1f} MB"
                else:
                    size_str = f"{file_size} KB"
                
                print(f"\n   {i}. 📄 {filename}")
                print(f"      📏 Size: {size_str}")
                print(f"      🏷️ Type: {file_type}")
                print(f"      🔗 Can download: {'Yes' if file_info.get('downloadUrl') else 'No'}")
        
        return model_details
    else:
        print("❌ Failed to get model details")
        return None

def test_small_download(civitai, model_details):
    """Test 4: Download a small file"""
    print("\n" + "="*60)
    print("📥 TEST 4: File Download")
    print("="*60)
    
    if not model_details:
        print("❌ Cannot test - No model details")
        return False
    
    # Find smallest downloadable file
    downloadable_file = None
    
    versions = model_details.get('modelVersions', [])
    if versions:
        files = versions[0].get('files', [])
        
        # Sort by size and find a small one
        sorted_files = sorted(files, key=lambda x: x.get('sizeKB', 0))
        
        for file_info in sorted_files:
            if file_info.get('downloadUrl') and file_info.get('sizeKB', 0) < 50 * 1024:  # < 50MB
                downloadable_file = file_info
                break
    
    if not downloadable_file:
        print("⚠️ No small files found for testing")
        print("💡 Using smallest available file...")
        if files:
            downloadable_file = sorted_files[0] if sorted_files else None
    
    if downloadable_file:
        filename = downloadable_file['name']
        download_url = downloadable_file['downloadUrl']
        file_size = downloadable_file.get('sizeKB', 0)
        
        print(f"🎯 Selected file: {filename}")
        print(f"📏 Size: {file_size / 1024:.1f} MB")
        
        if file_size > 100 * 1024:  # > 100MB
            print(f"⚠️ Large file warning: {file_size / 1024:.1f} MB")
            try:
                response = input("Continue? (y/n): ").lower().strip()
                if response != 'y':
                    print("⏭️ Download skipped")
                    return False
            except (EOFError, KeyboardInterrupt):
                print("\n⏭️ Download skipped (interrupted)")
                return False
        
        # Download
        download_result = civitai.download_model_file(
            download_url=download_url,
            filename=filename,
            download_dir="test_downloads"
        )
        
        if download_result:
            print(f"✅ Download successful: {download_result}")
            return True
        else:
            print("❌ Download failed")
            return False
    else:
        print("❌ No downloadable files found")
        return False

def check_downloads():
    """Test 5: Verify downloads"""
    print("\n" + "="*60)
    print("📂 TEST 5: Download Verification")
    print("="*60)
    
    download_dir = Path("test_downloads")
    
    if not download_dir.exists():
        print("❌ Download directory doesn't exist")
        return
    
    files = list(download_dir.glob("*"))
    
    if files:
        print(f"📊 Found {len(files)} files:")
        total_size = 0
        
        for file_path in files:
            if file_path.is_file():
                file_size = file_path.stat().st_size
                size_mb = file_size / (1024 * 1024)
                print(f"   📄 {file_path.name} ({size_mb:.1f} MB)")
                total_size += file_size
        
        print(f"\n📏 Total size: {total_size / (1024 * 1024):.1f} MB")
        print("✅ Downloads verified!")
    else:
        print("❌ No files found in download directory")

def run_all_tests():
    """Run complete test suite"""
    print("🎨 CivitAI Basic Functionality Test Suite")
    print("=" * 60)
    
    # Test 1: API Connection
    civitai = test_api_connection()
    
    # Test 2: Basic Search
    search_results = test_basic_search(civitai)
    
    # Test 3: Model Details
    model_details = test_model_details(civitai, search_results)
    
    # Test 4: Download
    download_success = test_small_download(civitai, model_details)
    
    # Test 5: Verification
    check_downloads()
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    tests = [
        ("API Connection", civitai is not None),
        ("Basic Search", search_results is not None),
        ("Model Details", model_details is not None),
        ("File Download", download_success),
    ]
    
    passed = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED! Ready for Streamlit integration.")
    elif passed >= len(tests) - 1:
        print("\n✅ MOSTLY SUCCESSFUL! Minor issues to fix.")
    else:
        print("\n⚠️ NEEDS DEBUGGING - Multiple failures.")
    
    return passed == len(tests)

if __name__ == "__main__":
    print("🚀 Starting CivitAI test suite...")
    print("\n💡 This will test:")
    print("   1. CivitAI API connection")
    print("   2. Model search functionality")
    print("   3. Model details retrieval")
    print("   4. File download capability")
    print("   5. Download verification")
    
    input("\nPress Enter to start tests...")
    
    success = run_all_tests()
    
    if success:
        print("\n🚀 Next step: Run the Streamlit app!")
        print("   streamlit run civitai_test_basic.py")
    else:
        print("\n🔧 Fix issues before proceeding")