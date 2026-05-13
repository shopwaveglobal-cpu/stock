#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"(?좏겙을 찾을 수 없습니다" 팝업 원인 추적
"""
import sys

# 사용자가 본 문자열: (?좏겙
# 이 문자들의 유니코드 코드포인트 확인
popup_text = "(?좏겙"
print("=== 팝업 문자 분석 ===")
print(f"문자: {popup_text!r}")
print(f"유니코드 코드포인트: {[hex(ord(c)) for c in popup_text]}")

# CP949로 인코딩했을 때 바이트
try:
    cp949_bytes = popup_text.encode('cp949')
    print(f"\nCP949 바이트 (hex): {cp949_bytes.hex()}")
    print(f"CP949 바이트 (list): {list(cp949_bytes)}")
    print(f"CP949 바이트 (ASCII view): {cp949_bytes}")
except Exception as e:
    print(f"CP949 인코딩 오류: {e}")

print("\n=== 역추적: 이 바이트들이 어떤 원본에서 왔을까? ===")

# 만약 이 바이트들이 UTF-8로 저장된 파일을 CP949로 읽은 결과라면
# 원본 UTF-8 바이트가 무엇인지 찾아야 함
# CP949 → 바이트 → 그 바이트를 UTF-8로 해석
try:
    cp949_bytes = popup_text.encode('cp949')
    as_utf8 = cp949_bytes.decode('utf-8', errors='replace')
    print(f"CP949 바이트를 UTF-8로 읽으면: {as_utf8!r}")
    print(f"  → 코드포인트: {[hex(ord(c)) for c in as_utf8]}")
except Exception as e:
    print(f"UTF-8 해석 오류: {e}")

# Latin-1으로 해석
try:
    cp949_bytes = popup_text.encode('cp949')
    as_latin1 = cp949_bytes.decode('latin-1')
    print(f"CP949 바이트를 Latin-1으로 읽으면: {as_latin1!r}")
    print(f"  → 바이트값: {[hex(b) for b in as_latin1.encode('latin-1')]}")
except Exception as e:
    print(f"Latin-1 해석 오류: {e}")

# 순수 바이트로 보기
try:
    cp949_bytes = popup_text.encode('cp949')
    print(f"\n각 바이트 분석:")
    for i, b in enumerate(cp949_bytes):
        if 32 <= b < 127:
            print(f"  byte[{i}]: 0x{b:02X} = {chr(b)!r} (ASCII)")
        else:
            print(f"  byte[{i}]: 0x{b:02X} = (non-ASCII)")
except Exception as e:
    print(f"오류: {e}")

print("\n=== 일반적인 프로그램 이름들이 CP949 환경에서 어떻게 보이는가 ===")
test_strings = [
    "python",
    "pythonw",
    "python.exe",
    "wscript",
    "cmd",
    "powershell",
    "C:\\Python314\\python.exe",
]
for s in test_strings:
    # ASCII이므로 CP949에서 동일
    print(f"  {s!r} → CP949: 동일 (순수 ASCII)")

print("\n=== 한국어가 포함된 경로/파일명 CP949 표현 ===")
# 만약 경로에 한국어가 있다면?
# 예: "프로그램" etc.
test_korean = [
    "프로그램",
    "사용자",
    "바탕화면",
    "시작",
]
for s in test_korean:
    try:
        b = s.encode('cp949')
        print(f"  {s!r} → CP949 hex: {b.hex()}")
    except Exception as e:
        print(f"  {s!r} → 오류: {e}")

print("\n=== UTF-8로 저장된 배치파일이 CP949로 읽힐 때의 변환 예시 ===")
# 만약 배치파일에 한국어 주석이 있고, 그 바이트가 명령어에 끼어들면?
# Korean UTF-8 bytes that when read as CP949 produce special chars
print("분석: UTF-8 한국어 3바이트 시퀀스 (0xE?-0xEF, 0x80-0xBF, 0x80-0xBF)")
print("이 바이트들은 CP949에서:")
print("  바이트1 (0xE0-0xEF): CP949 lead byte")
print("  바이트2 (0x80-0xBF): CP949 trail byte")
print("  바이트3 (0x80-0xBF): CP949 next lead byte")
print("  → 모두 유효한 CP949 쌍을 형성 (ASCII 특수문자 없음)")
print("  → REM 줄의 한국어는 명령어 파싱에 영향 없음")
