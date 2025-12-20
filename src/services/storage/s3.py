import boto3
import uuid
import os
from typing import Tuple, Optional
from botocore.config import Config

from src.config import settings


class S3Service:
    """Service for AWS S3 operations."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=Config(signature_version="s3v4")
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def generate_upload_url(
        self,
        file_name: str,
        file_type: str,
        project_id: str,
        expiration: int = 3600
    ) -> Tuple[str, str]:
        """
        Generate a presigned URL for file upload.
        
        Args:
            file_name: Original file name
            file_type: MIME type of the file
            project_id: Project ID for organizing files
            expiration: URL expiration time in seconds
            
        Returns:
            Tuple of (presigned_url, s3_key)
        """
        # Generate unique S3 key
        unique_id = str(uuid.uuid4())
        s3_key = f"projects/{project_id}/documents/{unique_id}/{file_name}"
        
        presigned_url = self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": s3_key,
                "ContentType": file_type
            },
            ExpiresIn=expiration
        )
        
        return presigned_url, s3_key
    
    def generate_download_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for file download.
        
        Args:
            s3_key: The S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned download URL
        """
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": s3_key
            },
            ExpiresIn=expiration
        )
    
    def download_file_to_temp(
        self,
        document_id: str,
        file_key: str,
        file_type: str
    ) -> str:
        """
        Download file from S3 to temporary location.
        
        Args:
            document_id: Document ID for unique naming
            file_key: S3 object key
            file_type: File extension
            
        Returns:
            Path to temporary file
        """
        temp_file = f"/tmp/{document_id}.{file_type}"
        
        self.s3_client.download_file(
            self.bucket_name,
            file_key,
            temp_file
        )
        
        return temp_file
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_key: S3 object key
            
        Returns:
            True if deletion was successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except Exception as e:
            print(f"Error deleting S3 file: {e}")
            return False
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            file_key: S3 object key
            
        Returns:
            True if file exists
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except:
            return False
