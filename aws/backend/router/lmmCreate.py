from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import os
import random
import boto3
import json

# APIRouter 정의
router = APIRouter(prefix="/create", tags=["create"])

# 프롬프트 요청 모델 정의
class PromptRequest(BaseModel):
    prompt: str  # 한글 텍스트 프롬프트 입력

# AWS Translate 클라이언트 생성
translate = boto3.client('translate', region_name = "us-east-1")
# AWS S3 클라이언트 생성 (주석 처리된 부분)
# s3 = boto3.client('s3')

# 번역 함수 정의
def translate_to_english(korean_text):
    response = translate.translate_text(
        Text=korean_text,
        SourceLanguageCode="ko",
        TargetLanguageCode="en"
    )
    return response['TranslatedText']

# 이미지 생성 함수
def generate_image(prompt: str, seed: int):
    # 요청 payload 정의
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 12,
        "seed": seed,
        "steps": 80,
    }

    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

    body = json.dumps(payload)

    model_id = "stability.stable-diffusion-xl-v1"

    # 모델 호출
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,
        accept="application/json",
        contentType="application/json",
    )

    # 응답 처리 및 이미지 디코딩
    response_body = json.loads(response['body'].read())
    artifact = response_body.get("artifacts")[0]
    image_encoded = artifact.get("base64").encode("utf-8")
    image_bytes = base64.b64decode(image_encoded)

    return image_bytes

# 라우터 엔드포인트 정의
@router.post("/")
async def create_image(prompt: PromptRequest):
    # 번역 요청된 텍스트를 영어로 번역
    
    prompt_data = translate_to_english(prompt.prompt)
    print(prompt_data)
    # 랜덤 시드 생성
    seed = random.randint(0, 100000)

    try:
        # 이미지 생성
        image_bytes = generate_image(prompt=prompt_data, seed=seed)

        # 이미지를 로컬 저장 (임시)
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_name = f"{output_dir}/generated-{seed}.png"
        with open(file_name, "wb") as f:
            f.write(image_bytes)

        # 생성된 이미지를 S3에 업로드 (주석 처리된 부분)
        # bucket_name = "your-s3-bucket-name"  # 여기에 본인의 S3 버킷 이름을 넣어야 함
        # s3_key = f"generated-images/generated-{seed}.png"
        # s3.put_object(Bucket=bucket_name, Key=s3_key, Body=image_bytes, ContentType='image/png')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 중 오류가 발생했습니다: {str(e)}")

    # Base64 인코딩된 이미지 반환 (Swagger UI에서 테스트 가능하도록 추가)
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # S3 이미지 URL 반환 (주석 처리된 부분)
    # s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

    return {
        "message": "Image created successfully",
        "image_base64": image_base64,
        # "s3_url": s3_url  # S3 URL 주석 처리
    }

handler = Mangum(router)