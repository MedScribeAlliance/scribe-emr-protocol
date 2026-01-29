"""
Example client demonstrating how to interact with the MedScribe Alliance Protocol

This script shows a complete workflow:
1. Discover service capabilities
2. List available templates
3. Create a session
4. Upload audio files (chunked)
5. End the session
6. Poll for results

Usage:
    python example_client.py
"""

import requests
import time
import os
from typing import Optional


class MedScribeClient:
    """Simple client for MedScribe Alliance Protocol"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def discover(self):
        """Get service discovery document"""
        print("📡 Fetching discovery document...")
        response = requests.get(f"{self.base_url}/.well-known/medscribealliance")
        response.raise_for_status()
        discovery = response.json()
        
        print(f"✓ Protocol: {discovery['protocol']} v{discovery['protocol_version']}")
        print(f"✓ Service: {discovery['service']['name']}")
        print(f"✓ Models available: {', '.join([m['id'] for m in discovery['models']])}")
        print(f"✓ Upload methods: {', '.join(discovery['capabilities']['upload_methods'])}")
        print(f"✓ Audio formats: {len(discovery['capabilities']['audio_formats'])} supported")
        
        return discovery
    
    def list_templates(self):
        """List available templates"""
        print("\n📋 Fetching available templates...")
        response = requests.get(f"{self.base_url}/v1/templates")
        response.raise_for_status()
        templates = response.json()
        
        print(f"✓ Found {len(templates['templates'])} templates:")
        for template in templates['templates']:
            print(f"  - {template['id']}: {template['name']}")
        
        return templates
    
    def create_session(
        self,
        templates: list,
        model: str = "lite",
        upload_type: str = "chunked",
        additional_data: dict = None
    ):
        """Create a new session"""
        print(f"\n🔨 Creating session with templates: {', '.join(templates)}...")
        
        payload = {
            "templates": templates,
            "model": model,
            "upload_type": upload_type,
            "communication_protocol": "http",
            "additional_data": additional_data or {}
        }
        
        response = requests.post(f"{self.base_url}/v1/sessions", json=payload)
        response.raise_for_status()
        session = response.json()
        
        self.session_id = session['session_id']
        print(f"✓ Session created: {self.session_id}")
        print(f"✓ Status: {session['status']}")
        print(f"✓ Upload URL: {session['upload_url']}")
        print(f"✓ Expires at: {session['expires_at']}")
        
        return session
    
    def upload_audio_file(self, file_path: str, sequence: int = 0):
        """Upload a single audio file"""
        if not self.session_id:
            raise ValueError("No active session. Create a session first.")
        
        print(f"\n📤 Uploading audio file: {file_path} (sequence: {sequence})...")
        
        # Determine content type from file extension
        extension = file_path.split('.')[-1].lower()
        content_types = {
            'webm': 'audio/webm;codecs=opus',
            'mp3': 'audio/mp3',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'm4a': 'audio/m4a',
        }
        content_type = content_types.get(extension, 'audio/webm')
        
        # Read file or create mock data if file doesn't exist
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                audio_data = f.read()
        else:
            print(f"  ℹ️  File not found, using mock data")
            audio_data = b"MOCK_AUDIO_DATA_" * 1000  # ~16KB mock data
        
        filename = f"audio_{sequence}.{extension}"
        
        response = requests.post(
            f"{self.base_url}/v1/sessions/{self.session_id}/audio/{filename}",
            headers={"Content-Type": content_type},
            data=audio_data
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Uploaded: {result['filename']} ({result['size_bytes']} bytes)")
        
        return result
    
    def upload_audio_chunks(self, file_paths: list):
        """Upload multiple audio chunks"""
        print(f"\n📤 Uploading {len(file_paths)} audio chunks...")
        
        for i, file_path in enumerate(file_paths):
            self.upload_audio_file(file_path, sequence=i)
            time.sleep(0.1)  # Small delay between uploads
        
        print(f"✓ All {len(file_paths)} chunks uploaded")
    
    def end_session(self, audio_files_sent: int):
        """End the session and trigger processing"""
        if not self.session_id:
            raise ValueError("No active session. Create a session first.")
        
        print(f"\n🏁 Ending session...")
        
        response = requests.post(
            f"{self.base_url}/v1/sessions/{self.session_id}/end",
            json={"audio_files_sent": audio_files_sent}
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Session ended")
        print(f"✓ Status: {result['status']}")
        print(f"✓ Message: {result['message']}")
        print(f"✓ Files received: {result['audio_files_received']}/{audio_files_sent}")
        
        return result
    
    def get_session_status(self):
        """Get current session status"""
        if not self.session_id:
            raise ValueError("No active session. Create a session first.")
        
        response = requests.get(f"{self.base_url}/v1/sessions/{self.session_id}")
        response.raise_for_status()
        
        return response.json()
    
    def poll_for_results(self, max_attempts: int = 10, interval: int = 2):
        """Poll for session results"""
        if not self.session_id:
            raise ValueError("No active session. Create a session first.")
        
        print(f"\n⏳ Polling for results (max {max_attempts} attempts, {interval}s interval)...")
        
        for attempt in range(max_attempts):
            status = self.get_session_status()
            
            print(f"  Attempt {attempt + 1}/{max_attempts}: {status['status']}")
            
            # Check if processing is complete
            if status['status'] in ['completed', 'partial', 'failed', 'expired']:
                print(f"\n✓ Processing complete!")
                print(f"  Status: {status['status']}")
                
                if 'transcript' in status and status['transcript']:
                    print(f"  Transcript: {status['transcript'][:100]}...")
                
                if 'templates' in status and status['templates']:
                    print(f"  Templates extracted: {', '.join(status['templates'].keys())}")
                
                return status
            
            time.sleep(interval)
        
        print("\n⚠️  Max polling attempts reached. Session may still be processing.")
        return status


def main():
    """Run example workflow"""
    print("=" * 70)
    print("MedScribe Alliance Protocol - Example Client")
    print("=" * 70)
    
    # Initialize client
    client = MedScribeClient("http://localhost:8000")
    
    try:
        # 1. Discover service capabilities
        discovery = client.discover()
        
        # 2. List available templates
        templates = client.list_templates()
        
        # 3. Create a session
        session = client.create_session(
            templates=["soap", "medications"],
            model="pro",
            upload_type="chunked",
            additional_data={
                "emr_encounter_id": "enc_12345",
                "patient_id": "pat_67890",
                "physician_id": "doc_11111",
            }
        )
        
        # 4. Upload audio files
        # You can provide real audio files or use mock data
        audio_files = [
            "audio_chunk_0.webm",
            "audio_chunk_1.webm",
            "audio_chunk_2.webm",
        ]
        
        client.upload_audio_chunks(audio_files)
        
        # 5. End the session
        client.end_session(audio_files_sent=len(audio_files))
        
        # 6. Poll for results
        final_status = client.poll_for_results(max_attempts=5, interval=1)
        
        # Display results
        print("\n" + "=" * 70)
        print("📊 Final Results")
        print("=" * 70)
        print(f"Session ID: {client.session_id}")
        print(f"Status: {final_status['status']}")
        print(f"Audio files: {final_status.get('audio_files_received', 0)}")
        
        if 'completed_at' in final_status:
            print(f"Completed at: {final_status['completed_at']}")
        
        if 'model_used' in final_status:
            print(f"Model used: {final_status['model_used']}")
        
        if 'language_detected' in final_status:
            print(f"Language detected: {final_status['language_detected']}")
        
        print("\n✅ Example workflow completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server!")
        print("Make sure the server is running:")
        print("  uvicorn main:app --reload")
    
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
