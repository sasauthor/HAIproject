---
최근 업데이트 내역
---
2025.06.13
shit+enter를 누르면 문구 입력창 내에서 줄바꿈이 되도록 수정하였습니다.
![스크린샷 2025-06-13 035047](https://github.com/user-attachments/assets/eadc01ce-2b75-4e73-8718-b92c24118e2c)

---
"필독"
---
자음 하나, 모음 하나와 같이 한글자 미만을 입력하면 작동이 되지 않습니다.
한 글자 이상을 입력해주세요.
한글만 됩니다.
Sorry for other language users, It's only for Korean.
다운로드 링크는 가장 최신으로 생성된 이미지를 제공합니다.
이전에 생성한 이미지는 복사/붙여넣기 기능을 활용해 주세요.
(또한 다운로드 링크에 세션간 충돌의 가능성 또한 있습니다.)

---
사용방법
---
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

---
프로젝트 개요
---
본 프로젝트는 세종과학예술영재학교의 2025학년도 인공지능 프로젝트 수행평가로 진행되었습니다.
또한 본 프로젝트는 DM-Font 모델을 활용하였음을 알립니다.
(https://github.com/clovaai/dmfont)

![HAI! 손글씨 AI의 사본](https://github.com/user-attachments/assets/339b9f0b-a6e9-4628-996e-04d8745e68de)
![HAI! 손글씨 AI의 사본 (1)](https://github.com/user-attachments/assets/835a5a3f-c92b-4450-93cd-14d249ba4d50)
![HAI! 손글씨 AI의 사본 (2)](https://github.com/user-attachments/assets/79d80683-728c-426a-9db3-a2e384a52c61)
![HAI! 손글씨 AI의 사본 (3)](https://github.com/user-attachments/assets/51e9ec41-a24d-46ad-878a-d14147dd6d95)
![HAI! 손글씨 AI의 사본 (4)](https://github.com/user-attachments/assets/691e9280-93e5-46cb-a889-7abfe19e7d20)
![HAI! 손글씨 AI의 사본 (5)](https://github.com/user-attachments/assets/1144cb18-8d1b-4c6d-afb9-5f305c425304)
![HAI! 손글씨 AI의 사본 (6)](https://github.com/user-attachments/assets/7eb86d87-50f3-4c14-9bc0-4d56ba29e9cf)
![HAI! 손글씨 AI의 사본 (7)](https://github.com/user-attachments/assets/c1c4751e-f7a4-4283-9700-6a57a26007c1)
![HAI! 손글씨 AI의 사본 (8)](https://github.com/user-attachments/assets/fddc7f28-dde7-422f-87b5-fc540b842f6c)
![HAI! 손글씨 AI의 사본 (9)](https://github.com/user-attachments/assets/cbe6ce5d-ec18-4a99-b5f5-6d4fa6b8c589)
![HAI! 손글씨 AI의 사본 (10)](https://github.com/user-attachments/assets/44d70de2-a7bc-4ad8-a635-081a9528bb17)
![HAI! 손글씨 AI의 사본 (11)](https://github.com/user-attachments/assets/7d42a372-4a09-45c9-876e-abbc710f2475)
![HAI! 손글씨 AI의 사본 (12)](https://github.com/user-attachments/assets/f91c08de-52f7-473a-b36f-b136a8843378)

진행 과정에 있어 사전 모델을 위해 colab을 활용했습니다.
해당 코드 또한 ipynb파일로 첨부합니다.(HAIproject.ipynb)


