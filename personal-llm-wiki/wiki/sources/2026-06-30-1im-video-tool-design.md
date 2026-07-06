# source — 1IM Video Tool 설계서

- 원본: raw/inbox/2026-06-30-1im-video-tool-design.md (docs/superpowers/specs/에서 복사, git 커밋 1c27ae10)
- 날짜: 2026-06-30 (파일명 기준) / 유형: 앱 설계서

## 요약

비전공자용 Windows 로컬 영상 도구(FFmpeg 래퍼). V1: 포맷 변환(MP4/MOV/MKV), 목표 용량 압축(2-pass), 음원 추출(MP3/M4A/WAV), 트림, 병합(빠른 concat + 자동 호환 경로). Tkinter 한국어 UI, PyInstaller onedir 포터블 패키징.

## 핵심 사실 (원본 기재)

- **안전 원칙**: 원본 파일 절대 덮어쓰기·삭제 금지, 출력 충돌 시 `_1`, `_2` 순번, 출력 폴더 내 파일은 재처리 제외(재귀 방지)
- **로컬 전용**: 네트워크 호출·계정·텔레메트리 전면 배제 (V1 범위 외로 명시)
- 보안: `subprocess`에 `shell=True` 금지, 명령은 인자 배열로만 구성 (한글 경로·공백 안전)
- FFmpeg 자동 다운로드 없음 — bin/에 수동 동봉, 없으면 명시적 실패 메시지
- 로그는 UTF-8 (한글 깨짐 방지 계열 규칙)
- 프로젝트 위치: `Desktop/code/1im-video-tool` 예정 (설계 시점)

## 미확인

- 구현 착수·완료 여부 — 이 문서는 설계이며 구현 기록 아님 (PORTFOLIO 총람에 기능 목록이 실려 있어 구현이 진행된 것으로 보인다 — 해석)

## 연결

- [decisions/2026-06-30-1im-local-only-safety](../decisions/2026-06-30-1im-local-only-safety.md)
- [projects/local-first-apps](../projects/local-first-apps.md)
- [sources/portfolio-logic-full](portfolio-logic-full.md) — 기능 목록 교차 확인
