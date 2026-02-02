# test_file_access.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.storage import default_storage
from django.conf import settings
import boto3

def test_file_access():
    print("\n=== Testing File Access ===")
    test_filename = "test_upload_680af2ce.txt"  # The file from earlier
    full_path = f"media/{test_filename}"  # Django adds 'media/' prefix
    
    # Initialize S3 client
    s3 = boto3.client('s3',
                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                     region_name=settings.AWS_S3_REGION_NAME)
    
    try:
        # List all objects in the bucket to see the exact path
        print("\nListing objects in the bucket:")
        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"- {obj['Key']} (Size: {obj['Size']} bytes)")
        else:
            print("No objects found in the bucket")
        
        # Check the specific file
        print(f"\nChecking file: {full_path}")
        try:
            # Get file metadata
            head = s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=full_path)
            print(f"✓ File exists: {full_path}")
            print(f"  Size: {head['ContentLength']} bytes")
            print(f"  Last Modified: {head['LastModified']}")
            print(f"  Content Type: {head.get('ContentType', 'N/A')}")
            
            # Generate a pre-signed URL for testing
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': full_path},
                ExpiresIn=3600
            )
            print(f"\n🔗 Pre-signed URL (valid for 1 hour):\n{url}")
            
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"❌ File not found: {full_path}")
                print("Checking alternative paths...")
                # Try to find the file with a different path
                response = s3.list_objects_v2(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Prefix=test_filename
                )
                if 'Contents' in response:
                    print("\nFound matching files:")
                    for obj in response['Contents']:
                        print(f"- {obj['Key']}")
                else:
                    print("No matching files found in the bucket")
            else:
                print(f"❌ Error accessing file: {e}")
                
    except Exception as e:
        print(f"❌ Error listing bucket contents: {e}")

if __name__ == "__main__":
    test_file_access()