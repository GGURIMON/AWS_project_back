# 이미지 생성
import base64
import os
import random
import boto3
import json

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

def main():
	for i in range(0,1):
		seed= random.randint(0,100000)
		generate_image(prompt=prompt_data, seed=seed, index=i)

def generate_image(prompt: str, seed: int, index: int):
	payload={
		"text_prompts":[{"text":prompt_data}],
		"cfg_scale":12,
		"seed":seed,
		"steps":80,

	}

	bedrock=boto3.client(service_name="bedrock-runtime")

	body=json.dumps(payload)

	model_id="stability.stable-diffusion-xl-v1"

	response=bedrock.invoke_model(
		body=body,
		modelId=model_id,
		accept="application/json",
		contentType="application/json",
	)

	response_body=json.loads(response['body'].read())
	artifact=response_body.get("artifacts")[0]
	image_encoded=artifact.get("base64").encode("utf-8")
	image_bytes=base64.b64decode(image_encoded)

	output_dir="output"
	os.makedirs(output_dir,exist_ok=True)
	file_name=f"{output_dir}/generated-{seed}.png"
	with open(file_name,"wb") as f:
		f.write(image_bytes)

if __name__ == "__main__":
    main()