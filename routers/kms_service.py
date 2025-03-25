from fastapi import APIRouter, HTTPException
from services.kms_client import KMSClient
from pydantic import BaseModel

router = APIRouter()
kms_client = KMSClient()

class EncryptRequest(BaseModel):
    key_id: str
    plaintext: str

class DecryptRequest(BaseModel):
    ciphertext: str

@router.get("/keys")
def list_kms_keys():
    return kms_client.list_keys()

@router.post("/encrypt")
def encrypt_data(request: EncryptRequest):
    """
    주어진 KMS 키를 사용하여 데이터를 암호화합니다.
    """
    result = kms_client.encrypt(request.key_id, request.plaintext)
    
    if result.get('statusCode') == 500:
        raise HTTPException(status_code=500, detail=result.get('error', '암호화 과정에서 오류가 발생했습니다.'))
    
    return result

@router.post("/decrypt")
def decrypt_data(request: DecryptRequest):
    """
    KMS를 사용하여 암호화된 데이터를 복호화합니다.
    """
    result = kms_client.decrypt(request.ciphertext)
    
    if result.get('statusCode') == 500:
        raise HTTPException(status_code=500, detail=result.get('error', '복호화 과정에서 오류가 발생했습니다.'))
    
    return result