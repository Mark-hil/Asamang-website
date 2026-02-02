# test_s3.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import boto3

def test_s3_connection():
    print("\n=== Testing S3 Connection ===")
    print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"Region: {settings.AWS_S3_REGION_NAME}")
    
    try:
        s3 = boto3.client('s3',
                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                         region_name=settings.AWS_S3_REGION_NAME)
        
        # Test listing buckets
        print("\n[1/2] Testing S3 connection...")
        response = s3.list_buckets()
        print("✓ Successfully connected to S3")
        print(f"  Available buckets: {[b['Name'] for b in response['Buckets']]}")
        
        # Test bucket access
        print(f"\n[2/2] Testing access to bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        s3.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print(f"✓ Successfully accessed bucket")
        
        # Test bucket CORS
        try:
            cors = s3.get_bucket_cors(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            print("✓ CORS is configured")
        except:
            print("⚠ CORS is not configured (this might cause issues with file uploads)")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "InvalidAccessKeyId" in str(e):
            print("  - Check your AWS_ACCESS_KEY_ID")
        if "SignatureDoesNotMatch" in str(e):
            print("  - Check your AWS_SECRET_ACCESS_KEY")
        if "NoSuchBucket" in str(e):
            print(f"  - Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' does not exist")
        if "AccessDenied" in str(e):
            print("  - The provided credentials don't have permission to access this bucket")
        return False

if __name__ == "__main__":
    test_s3_connection()