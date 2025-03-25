import os
import boto3
import base64

class KMSClient:
    def __init__(self):
        self.client = boto3.client(
            'kms',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
    
    def list_keys(self):
        # 모든 키 ID를 가져옴
        response = self.client.list_keys()
        cmk_keys = []
        aliases = {}

        # 별칭 가져오기
        alias_response = self.client.list_aliases()
        for alias in alias_response['Aliases']:
            if 'TargetKeyId' in alias:  # TargetKeyId가 있는 경우
                aliases[alias['TargetKeyId']] = alias['AliasName']

        # CMK 키만 필터링
        for key in response['Keys']:
            key_id = key['KeyId']
            key_info = self.client.describe_key(KeyId=key_id)
            if key_info['KeyMetadata']['KeyManager'] == 'CUSTOMER':  # 고객 관리형 키
                key_alias = aliases.get(key_id, "No Alias")  # 별칭이 없을 경우 "No Alias"
                cmk_keys.append({"KeyId": key_id, "Alias": key_alias})

        return {"keys": cmk_keys}
    
    def encrypt(self, key_id: str, plaintext: str):
        """
        주어진 KMS 키를 사용하여 평문을 암호화합니다.
        
        Args:
            key_id (str): 사용할 KMS 키 ID
            plaintext (str): 암호화할 평문
        
        Returns:
            dict: 암호화된 텍스트와 상태 정보
        """
        try:
            # 평문을 바이트로 변환
            plaintext_bytes = plaintext.encode('utf-8')
            
            # KMS를 사용하여 암호화
            response = self.client.encrypt(
                KeyId=key_id,
                Plaintext=plaintext_bytes
            )
            
            # 암호화된 데이터(CiphertextBlob)를 base64로 인코딩하여 반환
            ciphertext_base64 = base64.b64encode(response['CiphertextBlob']).decode('utf-8')
            
            return {
                'statusCode': 200,
                'ciphertext': ciphertext_base64,
                'keyId': key_id
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'error': str(e)
            }
    
    def decrypt(self, ciphertext_base64: str):
        """
        KMS를 사용하여 암호문을 복호화합니다.
        
        Args:
            ciphertext_base64 (str): base64로 인코딩된 암호문
        
        Returns:
            dict: 복호화된 평문과 상태 정보
        """
        try:
            # base64로 인코딩된 암호문을 디코딩
            ciphertext_blob = base64.b64decode(ciphertext_base64)
            
            # KMS를 사용하여 복호화
            response = self.client.decrypt(
                CiphertextBlob=ciphertext_blob
            )
            
            # 복호화된 평문을 문자열로 변환
            plaintext = response['Plaintext'].decode('utf-8')
            
            return {
                'statusCode': 200,
                'plaintext': plaintext,
                'keyId': response.get('KeyId', 'Unknown')
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'error': str(e)
            }