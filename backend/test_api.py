#!/usr/bin/env python3
"""
Simple API test for enhanced toxicity detection endpoints

This script tests the new API endpoints without requiring heavy model downloads.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def test_health_endpoint():
    """Test the health endpoint"""
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"Enhanced features available: {data['features']['enhanced_features']}")
            print(f"Available features: {[k for k, v in data['features'].items() if v]}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - server may not be running")
        return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_enhanced_detect():
    """Test enhanced detection endpoint"""
    print("\n=== Testing Enhanced Detection ===")
    
    test_cases = [
        "ur such an idiot 😡 lol jk",
        "Great job... really amazing work 🙄",
        "That's a nice day today"
    ]
    
    for text in test_cases:
        try:
            response = requests.post(
                f"{API_BASE}/detect",
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nText: {text}")
                print(f"Toxic: {data.get('is_toxic', 'N/A')}")
                print(f"Confidence: {data.get('confidence', 'N/A')}")
                print(f"Enhanced: {data.get('enhanced', False)}")
                
                if data.get('enhanced'):
                    print(f"Normalized: {data.get('normalization_applied', 'N/A')}")
                    if data.get('sarcasm_analysis'):
                        sarc = data['sarcasm_analysis']
                        print(f"Sarcastic: {sarc.get('is_sarcastic', 'N/A')}")
            else:
                print(f"❌ Detection failed for '{text}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Detection error for '{text}': {e}")

def test_normalization_endpoint():
    """Test text normalization endpoint"""
    print("\n=== Testing Normalization Endpoint ===")
    
    test_text = "OMG ur sooooo stupid 😡 lol jk"
    
    try:
        response = requests.post(
            f"{API_BASE}/normalize",
            json={"text": test_text},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Original: {data.get('original_text', 'N/A')}")
            print(f"Normalized: {data.get('normalized_text', 'N/A')}")
            print(f"Applied: {data.get('normalization_applied', 'N/A')}")
            print("✅ Normalization endpoint working")
        elif response.status_code == 503:
            print("⚠️ Enhanced features not available on server")
        else:
            print(f"❌ Normalization failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Normalization error: {e}")

def test_sarcasm_endpoint():
    """Test sarcasm detection endpoint"""
    print("\n=== Testing Sarcasm Detection Endpoint ===")
    
    test_text = "Great job... really amazing work 🙄"
    
    try:
        response = requests.post(
            f"{API_BASE}/detect_sarcasm",
            json={"text": test_text},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Text: {test_text}")
            print(f"Sarcastic: {data.get('is_sarcastic', 'N/A')}")
            print(f"Confidence: {data.get('confidence', 'N/A')}")
            print(f"Level: {data.get('confidence_level', 'N/A')}")
            print("✅ Sarcasm endpoint working")
        elif response.status_code == 503:
            print("⚠️ Enhanced features not available on server")
        else:
            print(f"❌ Sarcasm detection failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Sarcasm detection error: {e}")

def main():
    """Run all API tests"""
    print("🧪 Starting Enhanced API Tests\n")
    
    # Test if server is running
    if not test_health_endpoint():
        print("\n💡 To run these tests, start the server with:")
        print("   cd backend && python app.py")
        return
    
    # Test enhanced endpoints
    test_enhanced_detect()
    test_normalization_endpoint()
    test_sarcasm_endpoint()
    
    print("\n🎉 API tests completed!")

if __name__ == "__main__":
    main()