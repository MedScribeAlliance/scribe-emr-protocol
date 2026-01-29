"""
Simple test script for the MedScribe Alliance Mock Server

Run this after starting the server to verify all endpoints work correctly.

Usage:
    python test_server.py
"""

import requests
import io
import time

BASE_URL = "http://localhost:8000"


def test_discovery():
    """Test discovery endpoint"""
    print("Testing discovery endpoint...")
    response = requests.get(f"{BASE_URL}/.well-known/medscribealliance")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["protocol"] == "medscribealliance"
    print("✓ Discovery endpoint works")
    return data


def test_templates():
    """Test templates listing"""
    print("\nTesting templates endpoint...")
    response = requests.get(f"{BASE_URL}/v1/templates")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert len(data["templates"]) > 0
    print(f"✓ Templates endpoint works ({len(data['templates'])} templates available)")
    return data


def test_session_lifecycle():
    """Test complete session lifecycle"""
    print("\nTesting session lifecycle...")
    
    # 1. Create session
    print("  Creating session...")
    create_response = requests.post(
        f"{BASE_URL}/v1/sessions",
        json={
            "templates": ["soap", "medications"],
            "model": "pro",
            "upload_type": "chunked",
            "communication_protocol": "http",
            "additional_data": {
                "test": "data",
                "emr_encounter_id": "test_123"
            }
        }
    )
    assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}"
    session_data = create_response.json()
    session_id = session_data["session_id"]
    print(f"  ✓ Session created: {session_id}")
    
    # 2. Upload audio files
    print("  Uploading audio files...")
    
    # Create mock audio data
    mock_audio_data = b"MOCK_AUDIO_DATA_" * 100  # ~1.6KB of data
    
    # Upload first chunk
    upload_response_1 = requests.post(
        f"{BASE_URL}/v1/sessions/{session_id}/audio/audio_0.webm",
        headers={"Content-Type": "audio/webm;codecs=opus"},
        data=mock_audio_data
    )
    assert upload_response_1.status_code == 200, f"Expected 200, got {upload_response_1.status_code}"
    print("  ✓ Uploaded audio_0.webm")
    
    # Upload second chunk
    upload_response_2 = requests.post(
        f"{BASE_URL}/v1/sessions/{session_id}/audio/audio_1.webm",
        headers={"Content-Type": "audio/webm;codecs=opus"},
        data=mock_audio_data
    )
    assert upload_response_2.status_code == 200, f"Expected 200, got {upload_response_2.status_code}"
    print("  ✓ Uploaded audio_1.webm")
    
    # 3. Check session status (should be recording)
    print("  Checking session status...")
    status_response = requests.get(f"{BASE_URL}/v1/sessions/{session_id}")
    assert status_response.status_code in [200, 202], f"Expected 200/202, got {status_response.status_code}"
    status_data = status_response.json()
    print(f"  ✓ Session status: {status_data['status']}")
    print(f"  ✓ Audio files received: {status_data['audio_files_received']}")
    
    # 4. End session
    print("  Ending session...")
    end_response = requests.post(
        f"{BASE_URL}/v1/sessions/{session_id}/end",
        json={"audio_files_sent": 2}
    )
    assert end_response.status_code == 202, f"Expected 202, got {end_response.status_code}"
    end_data = end_response.json()
    print(f"  ✓ Session ended: {end_data['message']}")
    
    # 5. Check final status
    print("  Checking final session status...")
    final_status = requests.get(f"{BASE_URL}/v1/sessions/{session_id}")
    final_data = final_status.json()
    print(f"  ✓ Final status: {final_data['status']}")
    
    print("✓ Complete session lifecycle works")
    return session_id


def test_error_cases():
    """Test error handling"""
    print("\nTesting error cases...")
    
    # Test invalid session ID
    response = requests.get(f"{BASE_URL}/v1/sessions/invalid_id")
    assert response.status_code == 404
    print("  ✓ Invalid session returns 404")
    
    # Test unsupported audio format
    response = requests.post(
        f"{BASE_URL}/v1/sessions/ses_test/audio/test.xyz",
        headers={"Content-Type": "audio/xyz"},
        data=b"test"
    )
    assert response.status_code == 404  # Session not found first
    print("  ✓ Error handling works")
    
    print("✓ Error cases handled correctly")


def main():
    """Run all tests"""
    print("=" * 60)
    print("MedScribe Alliance Mock Server - Test Suite")
    print("=" * 60)
    
    try:
        # Test if server is running
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            print("\n❌ Server is not running!")
            print("Please start the server first:")
            print("  uvicorn main:app --reload")
            return
        
        # Run tests
        discovery_data = test_discovery()
        templates_data = test_templates()
        session_id = test_session_lifecycle()
        test_error_cases()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
        print("\nServer Information:")
        print(f"  Protocol: {discovery_data['protocol']}")
        print(f"  Version: {discovery_data['protocol_version']}")
        print(f"  Models: {', '.join([m['id'] for m in discovery_data['models']])}")
        print(f"  Templates: {len(templates_data['templates'])}")
        print(f"  Last Session: {session_id}")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
