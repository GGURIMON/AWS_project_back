# 인페인팅 배경제거 코드 통합
import base64
import boto3
import json
import os

# AWS 서비스 클라이언트 생성
client = boto3.client("bedrock-runtime", region_name="us-east-1")
translate = boto3.client("translate", region_name="us-east-1")

# 모델 ID 설정
model_id = "amazon.titan-image-generator-v2:0"

# 프롬프트 입력 및 번역 함수
def translate_to_english(korean_text):
    response = translate.translate_text(
        Text=korean_text,
        SourceLanguageCode="ko",
        TargetLanguageCode="en"
    )
    return response['TranslatedText']

# 작업 선택 프롬프트 입력
task_prompt = input("원하는 작업을 입력하세요 ('배경 제거' 또는 '인페인팅'): ")
translated_task = translate_to_english(task_prompt).lower()

# 인페인팅 프롬프트 입력
if translated_task == "inpainting":
    inpainting_prompt = input("인페인팅에 사용할 프롬프트를 입력하세요: ")
    prompt_data = translate_to_english(inpainting_prompt)

# 이미지 파일을 Base64로 인코딩
with open("./output/generated-5037.png", "rb") as image_file:
    input_image = base64.b64encode(image_file.read()).decode('utf8')

if translated_task == "remove background":
    # 배경 제거 요청 페이로드 생성
    request = json.dumps({
        "taskType": "BACKGROUND_REMOVAL",
        "backgroundRemovalParams": {
            "image": input_image
        }
    })

elif translated_task == "inpainting":
    # 마스크 이미지 로드 (인페인팅 작업 시 필요)
    with open("./output/house.png", "rb") as mask_file:
        mask_image = base64.b64encode(mask_file.read()).decode('utf8')
    
    # 인페인팅 요청 페이로드 생성
    request = json.dumps({
        "taskType": "INPAINTING",
        "inPaintingParams": {
            "image": input_image,
            "text": prompt_data,
            "maskImage": mask_image
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 512,
            "width": 512,
            "cfgScale": 8.0
        }
    })

else:
    print("잘못된 입력입니다. '배경 제거' 또는 '인페인팅'만 가능합니다.")
    exit()

# 모델 호출
response = client.invoke_model(modelId=model_id, body=request)

# 응답 데이터 디코딩
model_response = json.loads(response["body"].read())
base64_image_data = model_response["images"][0]

# 결과 이미지 저장
i, output_dir = 1, "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
while os.path.exists(os.path.join(output_dir, f"image_{i}.png")):
    i += 1

image_data = base64.b64decode(base64_image_data)
image_path = os.path.join(output_dir, f"image_{i}.png")
with open(image_path, "wb") as file:
    file.write(image_data)

print(f"The generated image has been saved to {image_path}.")
