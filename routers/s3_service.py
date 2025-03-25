from fastapi import APIRouter
from services.s3_client import S3Client

router = APIRouter()
s3_client = S3Client()

@router.get("/buckets")
def list_s3_buckets():
    return s3_client.list_buckets()