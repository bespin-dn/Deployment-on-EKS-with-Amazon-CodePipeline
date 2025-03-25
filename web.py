import os
import boto3
import json


from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

## Client
# AWS S3 Client 생성
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# AWS KMS Client 생성
kms_client = boto3.client(
    'kms',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# AWS Bedrock Client 생성
bedrock_AWS_REGION = 'us-east-1'
bedrock_client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=bedrock_AWS_REGION
)

## Logic
## Abount S3
@app.get("/s3/buckets")
def list_s3_buckets():
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return {"buckets": buckets}


## About KMS
@app.get("/kms/keys")
def list_kms_keys():
    # 모든 키 ID를 가져옴
    response = kms_client.list_keys()
    cmk_keys = []
    aliases = {}

    # 별칭 가져오기
    alias_response = kms_client.list_aliases()
    for alias in alias_response['Aliases']:
        if 'TargetKeyId' in alias:  # TargetKeyId가 있는 경우
            aliases[alias['TargetKeyId']] = alias['AliasName']

    # CMK 키만 필터링
    for key in response['Keys']:
        key_id = key['KeyId']
        key_info = kms_client.describe_key(KeyId=key_id)
        if key_info['KeyMetadata']['KeyManager'] == 'CUSTOMER':  # 고객 관리형 키
            key_alias = aliases.get(key_id, "No Alias")  # 별칭이 없을 경우 "No Alias"
            cmk_keys.append({"KeyId": key_id, "Alias": key_alias})

    return {"keys": cmk_keys}

## About Inference with bedrock
# ModelId = "anthropic.claude-3-7-sonnet-20250219-v1:0"
ModelId = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
# ModelId = "anthropic.claude-3-5-sonnet-20241022-v2:0"
# ModelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"

@app.post("/bedrock/invoke")
def invoke_bedrock_model(query: str):
    try:
        # Add your logic here
        promptBody = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            # "text": "You are an elementary school math teacher. You should explain the formula as simple as possible."
                            "text": "You are a mathamatics professor. You should explain the formula as simple as possible."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            ],
            "max_tokens": 512,
            "temperature": 0.5
        }

        # body_bytes = json.dumps(promptBody).encode('utf-8')
        body_bytes = json.dumps(promptBody)

        response = bedrock_client.invoke_model(
            modelId=ModelId,
            body=body_bytes,
            contentType='application/json'
        )
        return {
            'statusCode': 200,
            'body': json.loads(response["body"].read())["content"][0]["text"]
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

#async def root():
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/home")
async def home():
    return {"message": "Home"}

@app.get("/home/{name}")
async def read_name(name: str):
    return {'name' : name}

@app.get("/home_err/{name}")
async def read_name_err(name: int):
    return {'name' : name}

## POST Method
@app.post("/")
async def home_post(msg: str):
    return {"Hello" : "POST", "msg": msg}