"""
Supabase Storage integration for file uploads and downloads.

Provides helper functions to interact with Supabase Storage buckets
for storing and retrieving files and assets.
"""

import os
from supabase import create_client, Client


def _get_supabase_client() -> Client:
    """
    Get configured Supabase client.

    Returns:
        Configured Supabase client instance

    Raises:
        ValueError: If required environment variables are not set
    """
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required. "
            "Please add them to your .env file."
        )

    return create_client(url, key)


def upload_file_bytes(bucket: str, path: str, data: bytes, content_type: str) -> str:
    """
    Upload raw bytes to a Supabase Storage bucket.

    Args:
        bucket: Name of the Supabase Storage bucket
        path: Path within the bucket to store the file
        data: Raw bytes to upload
        content_type: MIME type of the file (e.g., 'image/png', 'application/json')

    Returns:
        Public URL of the uploaded file

    Raises:
        Exception: If upload fails
    """
    supabase = _get_supabase_client()

    # Upload the file
    response = supabase.storage.from_(bucket).upload(
        path=path,
        file=data,
        file_options={"content-type": content_type}
    )

    if response.status_code != 200:
        raise Exception(f"Failed to upload file: {response.json()}")

    # Get public URL
    public_url = supabase.storage.from_(bucket).get_public_url(path)

    return public_url


def download_file_bytes(bucket: str, path: str) -> bytes:
    """
    Download file bytes from a Supabase Storage bucket.

    Args:
        bucket: Name of the Supabase Storage bucket
        path: Path within the bucket to download from

    Returns:
        Raw bytes of the downloaded file

    Raises:
        Exception: If download fails
    """
    supabase = _get_supabase_client()

    # Download the file
    response = supabase.storage.from_(bucket).download(path)

    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.json()}")

    return response.content
