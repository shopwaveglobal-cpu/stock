# 1IM Video Tool

`1IM Video Tool`은 비전문가도 쉽게 쓸 수 있는 Windows 전용 로컬 영상 처리 도구입니다. 모든 작업은 PC 안에서만 실행되며, FFmpeg 명령어는 앱 내부에서 처리됩니다.

## 지원 기능

- 영상 형식 바꾸기: MP4, MOV, MKV 출력
- 영상 용량 줄이기: 25 MB부터 1 GB 또는 직접 입력
- 영상에서 음원 추출: MP3, M4A, WAV
- 앞뒤 몇 초 자르기: 초 또는 소수점 초 입력
- 영상 이어붙이기: 빠른 병합 또는 자동 호환 병합

## 개발 실행

```powershell
cd C:\Users\log\Desktop\code\1im-video-tool
.\run_dev.bat
```

또는:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## 포터블 Windows 버전 빌드

먼저 `bin\ffmpeg.exe`, `bin\ffprobe.exe`가 있어야 합니다. 이 프로젝트는 외부 바이너리를 자동 다운로드하지 않습니다.

```powershell
cd C:\Users\log\Desktop\code\1im-video-tool
.\build.bat
```

빌드 결과:

```text
dist\1IM Video Tool\
dist\1IM_Video_Tool_Portable.zip
```

압축을 풀고 `1IM Video Tool.exe`를 실행하면 Python이나 별도 FFmpeg 설치 없이 사용할 수 있습니다.

## 출력 저장 위치

기본 출력은 원본 파일이 있는 폴더 아래에 저장됩니다.

```text
[원본 폴더]\1IM Video Tool Output\[기능명]\
```

같은 파일명이 이미 있으면 `_1`, `_2`처럼 번호를 붙입니다. 원본 파일은 덮어쓰거나 삭제하지 않습니다.

## 개인정보와 네트워크

모든 처리는 로컬 PC에서만 실행됩니다. 업로드, 클라우드 API, 계정, 분석 수집, 네트워크 호출은 없습니다.

## 알려진 제한

- 손상된 파일이나 DRM으로 보호된 미디어는 실패할 수 있습니다.
- 목표 용량 압축은 영상 길이와 콘텐츠에 따라 정확히 일치하지 않을 수 있습니다.
- 이어붙이기 호환 모드는 영상 속성을 맞추기 때문에 시간이 더 오래 걸릴 수 있습니다.

## Third-party notices

이 앱은 FFmpeg/FFprobe 실행 파일을 함께 배포할 수 있습니다. FFmpeg는 별도 라이선스 조건을 따르므로 배포 전에 `THIRD_PARTY_NOTICES.md`와 FFmpeg 라이선스를 확인해야 합니다.
