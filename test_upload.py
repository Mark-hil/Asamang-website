# test_upload.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

def test_upload():
    print("\n=== Testing File Upload ===")
    test_content = "This is a test file for Asamang Web."
    test_filename = f"test_upload_{os.urandom(4).hex()}.txt"
    
    try:
        print(f"Uploading test file to: {settings.AWS_STORAGE_BUCKET_NAME}")
        
        # Create a test file
        file = ContentFile(test_content.encode('utf-8'), test_filename)
        
        # Save the file
        saved_path = default_storage.save(test_filename, file)
        print(f"✓ File saved as: {saved_path}")
        
        # Get the file URL
        file_url = default_storage.url(saved_path)
        print(f"✓ File URL: {file_url}")
        
        # Verify the file exists
        if default_storage.exists(saved_path):
            print("✓ File verified in storage")
        else:
            print("⚠ Warning: File not found in storage after upload")
            
        # Try to read the file back
        try:
            with default_storage.open(saved_path) as f:
                content = f.read().decode('utf-8')
                if content == test_content:
                    print("✓ File content matches original")
                else:
                    print("⚠ Warning: File content does not match original")
        except Exception as e:
            print(f"⚠ Warning: Could not read back file - {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "NoSuchBucket" in str(e):
            print("  - The specified bucket does not exist")
        elif "Access Denied" in str(e):
            print("  - Check your IAM permissions (s3:PutObject required)")
        return False

if __name__ == "__main__":
    test_upload()