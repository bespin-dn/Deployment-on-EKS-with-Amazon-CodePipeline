from fastapi import APIRouter
from services.bedrock_client import BedrockClient

router = APIRouter()
bedrock_client = BedrockClient()

@router.post("/invoke")
def invoke_bedrock_model(query: str):
    return bedrock_client.invoke_model(query)