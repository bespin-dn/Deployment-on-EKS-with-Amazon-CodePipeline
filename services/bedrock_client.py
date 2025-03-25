import os
import boto3
import json

class BedrockClient:
    def __init__(self):
        self.bedrock_AWS_REGION = 'us-east-1'
        self.client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.bedrock_AWS_REGION
        )
        # ModelId = "anthropic.claude-3-7-sonnet-20250219-v1:0"
        self.ModelId = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        # ModelId = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        # ModelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    
    def invoke_model(self, query: str):
        try:
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

            body_bytes = json.dumps(promptBody)

            response = self.client.invoke_model(
                modelId=self.ModelId,
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