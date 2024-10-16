import base64
import os
import random
import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

# AWS SDK(Boto3)로 Bedrock 서비스에 접근하기 위한 클라이언트 생성
session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()
region_name = 'us-east-1'

# Bedrock API 클라이언트 생성
bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)

def translate_haiku_to_english(korean_haiku):
    # 모델 ID 및 요청 설정
    model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
    prompt = f"Translate the following Korean haiku to English:\n\n{korean_haiku}"

    # 요청 데이터 구성
    response = bedrock_client.invoke_model(
        modelId=model_id,
        contentType="text/plain",
        accept="application/json",
        body=prompt.encode('utf-8')
    )

    # 응답 처리
    result = response['body'].read().decode('utf-8')
    return result

# 한글 Haiku 입력
korean_haiku = input("Haiku를 입력하세요 (한글): ")

# 번역 호출
translated_haiku = translate_haiku_to_english(korean_haiku)
print("Translated Haiku:", translated_haiku)

# 이미지 생성 함수
def generate_image(prompt: str, seed: int):
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 12,
        "seed": seed,
        "steps": 80,
    }

    # AWS Bedrock Endpoint
    endpoint_url = f'https://bedrock-runtime.{region_name}.amazonaws.com/models/stability.stable-diffusion-xl-v1/invoke'
    
    # 요청 생성
    headers = {
        'Content-Type': 'application/json',
    }

    # 인증 설정
    auth = AWS4Auth(credentials.access_key, credentials.secret_key, region_name, 'bedrock-runtime', session_token=credentials.token)

    # API 요청
    response = requests.post(endpoint_url, auth=auth, headers=headers, json=payload)

    # 응답 처리
    if response.status_code == 200:
        response_body = response.json()
        artifact = response_body.get("artifacts")[0]
        image_encoded = artifact.get("base64")
        image_bytes = base64.b64decode(image_encoded)

        # 이미지 저장
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_name = f"{output_dir}/generated-{seed}.png"
        with open(file_name, "wb") as f:
            f.write(image_bytes)
        print(f"Image saved as {file_name}")
    else:
        print("Error:", response.status_code, response.text)

# 메인 함수
def main():
    for i in range(1):  # 1번 생성
        seed = random.randint(0, 100000)
        generate_image(prompt=translated_haiku, seed=seed)

if __name__ == "__main__":
    main()
