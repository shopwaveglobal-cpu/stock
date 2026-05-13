#!/usr/bin/env python3
"""
start "Korean Title" program 명령어에서
CP949 파싱 시 닫는 따옴표가 사라지는지 분석
"""

def cp949_parse_simulate(data: bytes) -> list:
    """CP949 바이트 스트림을 파싱하여 토큰 목록 반환"""
    tokens = []
    i = 0
    while i < len(data):
        b = data[i]
        if b < 0x81:
            # 단바이트 ASCII 문자
            tokens.append(('ascii', bytes([b]), chr(b)))
            i += 1
        elif 0x81 <= b <= 0xFE:
            # CP949 리드 바이트
            if i + 1 < len(data):
                trail = data[i+1]
                # 유효한 트레일 바이트: 0x40-0x7E 또는 0x80-0xFE
                if (0x40 <= trail <= 0x7E) or (0x80 <= trail <= 0xFE):
                    tokens.append(('cp949', bytes([b, trail]), f'[{b:02X}{trail:02X}]'))
                    i += 2
                else:
                    # 유효하지 않은 트레일 바이트 - 리드 바이트를 단독으로 처리
                    tokens.append(('orphan', bytes([b]), f'[orphan:{b:02X}]'))
                    tokens.append(('ascii', bytes([trail]), chr(trail) if trail < 128 else f'[{trail:02X}]'))
                    i += 2
            else:
                tokens.append(('orphan', bytes([b]), f'[orphan:{b:02X}]'))
                i += 1
        else:
            tokens.append(('unknown', bytes([b]), f'[{b:02X}]'))
            i += 1
    return tokens

# 테스트: run_real_time_monitor_with_display.bat의 start 명령
# start "S12 로그 모니터" powershell ...
print("=== run_real_time_monitor_with_display.bat 분석 ===")
with open(r'C:\Users\log\Desktop\Code\S12\run_real_time_monitor_with_display.bat', 'rb') as f:
    raw = f.read()

# start 명령어가 있는 줄 찾기
for line in raw.split(b'\n'):
    line = line.rstrip(b'\r')
    if b'start' in line.lower() and b'"' in line:
        print(f"\n원본 바이트: {line!r}")
        tokens = cp949_parse_simulate(line)

        # 따옴표 추적
        in_quotes = False
        quote_start = None
        title = []
        after_title = []

        print("\nCP949 파싱 결과:")
        for i, (typ, raw_b, char) in enumerate(tokens):
            if typ == 'ascii' and char == '"':
                if not in_quotes:
                    in_quotes = True
                    print(f'  [{i}] OPEN_QUOTE "')
                else:
                    in_quotes = False
                    print(f'  [{i}] CLOSE_QUOTE "')
            elif in_quotes:
                print(f'  [{i}] {typ}: {char} (raw: {raw_b.hex()})')
                title.append(char)
            else:
                print(f'  [{i}] {typ}: {char!r} (raw: {raw_b.hex()})')

        # 요약
        print(f"\n→ 타이틀로 파싱된 내용: {''.join(title)}")
        break

print("\n=== start_realtime_monitor.bat BOM 분석 ===")
with open(r'C:\Users\log\Desktop\Code\S12\start_realtime_monitor.bat', 'rb') as f:
    bom_raw = f.read()

print(f"첫 10 바이트 (hex): {bom_raw[:10].hex()}")
print(f"UTF-8 BOM 존재: {bom_raw[:3] == bytes([0xEF, 0xBB, 0xBF])}")
print()

# BOM 이후 첫 줄
first_line = bom_raw.split(b'\n')[0].rstrip(b'\r')
print(f"첫 줄 파싱 결과:")
tokens = cp949_parse_simulate(first_line)
for i, (typ, raw_b, char) in enumerate(tokens):
    print(f"  [{i}] {typ}: {char!r} (raw: {raw_b.hex()})")

print("\n→ @echo off 인식 여부: @ 문자가", end=" ")
has_at = any(c == '@' for _, _, c in tokens)
print("있음 (정상)" if has_at else "없음 ← BOM이 @ 를 삼켰음! (문제!)")

print("\n=== 모든 배치파일의 start 명령어에서 따옴표 불균형 감지 ===")
import os
dirs = [r'C:\Users\log\Desktop\Code\S12', r'C:\Users\log\Desktop\Code\S1']
for d in dirs:
    for fname in sorted(os.listdir(d)):
        if not fname.endswith('.bat'):
            continue
        fpath = os.path.join(d, fname)
        with open(fpath, 'rb') as f:
            content = f.read()
        for lineno, line in enumerate(content.split(b'\n'), 1):
            line = line.rstrip(b'\r')
            if b'start' not in line.lower():
                continue
            if b'"' not in line:
                continue
            stripped = line.strip().upper()
            if stripped.startswith(b'REM') or stripped.startswith(b'ECHO'):
                continue

            # 따옴표 카운트
            tokens = cp949_parse_simulate(line)
            quote_count = sum(1 for typ, raw_b, char in tokens if typ == 'ascii' and char == '"')
            if quote_count % 2 != 0:
                print(f"⚠️ {fname}:{lineno}: 따옴표 불균형 ({quote_count}개)!")
                print(f"   원본: {line!r}")
