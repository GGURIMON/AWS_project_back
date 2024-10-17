# Python 3.10 slim 버전의 Docker 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt를 컨테이너 내부로 복사
COPY requirements.txt .

# 의존성 패키지들을 package 폴더에 설치
RUN pip install --no-cache-dir -r requirements.txt -t ./package

# docker run 명령어에서 '-v' 옵션을 사용해 로컬 디렉토리에 결과물을 저장할 수 있음
CMD ["bash"]
