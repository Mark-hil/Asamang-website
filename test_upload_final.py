# test_upload_final.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

def test_upload_and_verify():
    print("\n=== Testing S3 File Upload with Verification ===")
    test_content = "This is a final test file for Asamang Web."
    test_filename = f"test_final_{os.urandom(4).hex()}.txt"
    
    # Initialize S3 client for direct verification
    s3 = boto3.client('s3',
                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                     region_name=settings.AWS_S3_REGION_NAME)
    
    try:
        print(f"\n[1/3] Uploading test file to S3 via Django storage...")
        file = ContentFile(test_content.encode('utf-8'), test_filename)
        saved_path = default_storage.save(test_filename, file)
        print(f"✓ File saved to: {saved_path}")
        
        # Get the URL that Django would generate
        file_url = default_storage.url(saved_path)
        print(f"✓ Django file URL: {file_url}")
        
        # List all objects in the bucket to see what's actually there
        print("\n[2/3] Listing all objects in the bucket...")
        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        
        if 'Contents' in response:
            print("\nFound these objects in the bucket:")
            for obj in response['Contents']:
                print(f"- {obj['Key']} (Size: {obj['Size']} bytes)")
        else:
            print("No objects found in the bucket")
        
        # Check if file exists in S3 (try both with and without media/ prefix)
        print("\n[3/3] Checking file locations...")
        possible_paths = [
            saved_path,  # Direct path
            f"media/{saved_path}",  # With media/ prefix
            f"static/{saved_path}",  # In case it went to static
            test_filename  # Just the filename
        ]
        
        found = False
        for path in possible_paths:
            try:
                response = s3.head_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=path
                )
                print(f"✓ Found file at: {path}")
                print(f"  Size: {response['ContentLength']} bytes")
                print(f"  Last Modified: {response['LastModified']}")
                found = True
                
                # Generate a pre-signed URL
                presigned_url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': path
                    },
                    ExpiresIn=3600
                )
                print(f"\n🔗 Pre-signed URL (valid for 1 hour):")
                print(presigned_url)
                break
                
            except ClientError as e:
                if e.response['Error']['Code'] != '404':
                    print(f"  Error checking {path}: {e}")
        
        if not found:
            print("\n❌ File not found in any expected location.")
            print("   Please check your S3 bucket for the uploaded file.")
            print("\nPossible issues:")
            print("1. The file might not have been uploaded (check for any errors above)")
            print("2. The file might be in a different path than expected")
            print("3. There might be permission issues with the bucket")
            print("\nCheck your S3 bucket manually to see if the file exists.")
                
    except Exception as e:
        print(f"\n❌ Error during upload: {str(e)}")
        if "NoCredentialsError" in str(e):
            print("   Please check your AWS credentials in the .env file")
        elif "NoSuchBucket" in str(e):
            print(f"   Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' does not exist")
        elif "Access Denied" in str(e):
            print("   The provided AWS credentials don't have permission to access this bucket")

if __name__ == "__main__":
    test_upload_and_verify()