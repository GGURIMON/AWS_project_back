from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import base64
import boto3
import json
import os
import random

# APIRouter 정의
router = APIRouter(prefix = "/edit", tags = ["edit"])

# AWS 서비스 클라이언트 생성
client = boto3.client("bedrock-runtime", region_name="us-east-1")
translate = boto3.client("translate", region_name="us-east-1")

# 모델 ID 설정
model_id = "amazon.titan-image-generator-v2:0"

# 요청 모델 정의
class InpaintingRequest(BaseModel):
    prompt: str  # 한글 텍스트 프롬프트 입력

# 번역 함수 정의
def translate_to_english(korean_text):
    response = translate.translate_text(
        Text=korean_text,
        SourceLanguageCode="ko",
        TargetLanguageCode="en"
    )
    return response['TranslatedText']

# FastAPI 엔드포인트 정의
@router.post("//test-prompt")
async def inpaint_image(request: InpaintingRequest, input_image: UploadFile = File(...), mask_image: UploadFile = File(...)):
    try:
        # 프롬프트 번역 (한글 -> 영어)
        prompt_data = translate_to_english(request.text)

        # 이미지 파일을 Base64로 인코딩
        input_image_bytes = await input_image.read()
        input_image_base64 = base64.b64encode(input_image_bytes).decode('utf8')

        mask_image_bytes = await mask_image.read()
        mask_image_base64 = base64.b64encode(mask_image_bytes).decode('utf8')

        # 요청 페이로드 생성
        request_payload = {
            "taskType": "INPAINTING",
            "inPaintingParams": {
                "image": input_image_base64,
                "text": prompt_data,
                "maskImage": mask_image_base64
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 512,
                "width": 512,
                "cfgScale": 8.0
            }
        }

        body = json.dumps(request_payload)

        # 모델 호출
        response = client.invoke_model(modelId=model_id, body=body, accept="application/json", contentType="application/json")

        # 응답 데이터 디코딩
        response_body = json.loads(response["body"].read())
        base64_image_data = response_body["images"][0]

        # 생성된 이미지 저장
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_name = f"generated-{random.randint(0, 100000)}.png"
        image_path = os.path.join(output_dir, file_name)

        image_data = base64.b64decode(base64_image_data)
        with open(image_path, "wb") as file:
            file.write(image_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 중 오류가 발생했습니다: {str(e)}")

    return {
        "message": "Image successfully generated",
        "image_path": image_path
    }

@router.post("/")
async def test_prompt(prompt: InpaintingRequest):
    prompt_data = prompt.prompt
    print(prompt_data)
    # try:
    #     # 받은 프롬프트 텍스트 출력
    #     prompt_data = prompt.prompt
    #     translated_prompt = translate_to_english(prompt_data)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"프롬프트 처리 중 오류가 발생했습니다: {str(e)}")

    # return {
    #     "original_prompt": prompt_data,
    #     "translated_prompt": translated_prompt
    # }

handler = Mangum(router)