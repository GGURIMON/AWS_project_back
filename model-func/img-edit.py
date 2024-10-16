# 드래그박스 이용한 이미지 부분 편집(인페인팅)
import base64
import boto3
import json
import os

# AWS 서비스 클라이언트 생성
client = boto3.client("bedrock-runtime", region_name="us-east-1")
translate = boto3.client("translate", region_name="us-east-1")

# 모델 ID 설정
model_id = "amazon.titan-image-generator-v2:0"

# 프롬프트 입력 및 번역
translate = boto3.client('translate')

def translate_to_english(korean_text):
	response=translate.translate_text(
		Text=korean_text,
		SourceLanguageCode="ko",
		TargetLanguageCode="en"
	)
	return response['TranslatedText']

korean_prompt=input("프롬프트 입력 창 :")

prompt_data=translate_to_english(korean_prompt)

# 이미지 파일을 Base64로 인코딩
with open("./output/generated-98346.png", "rb") as image_file:
    input_image = base64.b64encode(image_file.read()).decode('utf8')

with open("./output/people.png", "rb") as image_file:
    mask_image = base64.b64encode(image_file.read()).decode('utf8')

# 요청 페이로드 생성
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
print(prompt_data)

# 모델 호출
response = client.invoke_model(modelId=model_id, body=request)

# 응답 데이터 디코딩
model_response = json.loads(response["body"].read())
base64_image_data = model_response["images"][0]

# 생성된 이미지 저장
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
