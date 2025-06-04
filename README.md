```
pip install -r requirements.txt
```
위와 같이 필수 패키지를 다운로드 받고,
```
gdown 1ZYRKiuIAB_Olxbu5xz5XnaUNXQycYzX_ -O checkpoints/korean-handwriting.pth
```
사전학습모델을 받아주세요.
```
python app.py
```
로 실행해주세요.
만약 실행하는 환경에 Poppler가 없다면 Poppler를 설치하셔야 합니다.
ubuntu/debian 계열에선 아래 명령어를 실행해주세요.
```
sudo apt-get update
sudo apt-get install -y poppler-utils

```
