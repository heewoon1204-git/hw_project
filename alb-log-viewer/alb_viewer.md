# ALB log를 화면에서 간편하게 보여주기

## 환경 세팅

### 1. Python 가상환경에서 Flask 환경 만들기

현재 PC에서 가상환경 만든 후 Flask(웹 서버) 설치

-m venv : pyton의 venv 모듈 생성

```bash
# 가상환경 만들기
python3 -m venv .venv

# 활성화
source .venv/bin/activate
```

가상환경이 만들어졌으면 Flask(웹 서버) 설치

- boto3 : AWS S3 접근

```bash
# Flask 설치
pip install flask boto3

# requirements.txt 파일 생성하기
# 현재 파이썬 환경에 설치된 패키지들을 requirements.txt로 저장하는 명령어
# requirements.txt는 준비물 목록. 도커가 이거보고 Flask 필요 boto3 필요, gunicorn 필요.. 설치해야지!가 됨
pip freeze > requirements.txt
```

### 2. local 환경에서 ALB viewer 생성

app.py, templates의 index.html

### 3. docker로 이미지 생성

```bash
# Dockerfile

FROM python:3.12-slim. -----> Python 3.12가 설치되어 있는 Linux 환경을 바탕으로 이 이미지를 만들어줘. 도커는 기존 이미지를 가져와서 그 위에 내가 필요한 환경을 쌓는 방식이기 때문에 python:3.12-slim 이미지를 가지고 오라는 뜻

WORKDIR /app       ---------> 도커 컨테이너 안에서 작업할 폴더를 /app으로 지정해줘.

COPY requirements.txt .   --> 내 컴퓨터에 있는 requirements.txt를 Docker 이미지의 현재 작업 폴더로 복사해줘.

RUN pip install --no-cache-dir -r requirements.txt  ----> RUN : 도커 컨테이너 안에서 실행할 명령어 

COPY app.py .          ---------> app.py 파이선 프로그램을 복사해줘
COPY templates ./templates  ----> templates 폴더를 복사해줘

EXPOSE 5001     ----------------> 이 컨테이너의 애플리케이션이 5001 포트를 사용한다고 도커에게 알려주는 설정
                                  여기까지는 도커가 이미지 만들 때까지의 설정

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]   ---> 컨테이너가 실행될 때 이 명령어를 실행
                                                             여기서부터는 이미지를 실행할 때 사용할 것

gunicorn : Flask 앱을 실행하기 위한 Python WSGI 서버
--bind 0.0.0.0:5001 : 컨테이너의 모든 네트워크 인터페이스에서 5001 포트를 받아라
app:app : app(app.py):app(Flask 객체)
```