#!/usr/bin/env python3
"""
배치파일에서 REM이 아닌 줄에 비ASCII 바이트를 찾는 도구
비ASCII 바이트가 명령어에 포함되면 CP949 파싱 오류로 팝업 유발 가능
"""
import os

# 검사할 디렉토리들
dirs = [
    r"C:\Users\log\Desktop\Code\S12",
    r"C:\Users\log\Desktop\Code\S1",
    r"C:\Users\log\Desktop\Code\omg",
]

# 결과 저장
issues = []

for d in dirs:
    if not os.path.exists(d):
        continue
    for fname in os.listdir(d):
        if not fname.endswith('.bat'):
            continue
        fpath = os.path.join(d, fname)
        try:
            with open(fpath, 'rb') as f:
                raw_bytes = f.read()

            # 라인별로 분석
            lines = raw_bytes.split(b'\n')
            for lineno, line in enumerate(lines, 1):
                # CR 제거
                line = line.rstrip(b'\r')

                # 빈 줄 스킵
                if not line.strip():
                    continue

                # REM 줄 (대소문자 무관) 스킵
                stripped = line.strip().upper()
                if stripped.startswith(b'REM') and (len(stripped) == 3 or stripped[3:4] in (b' ', b'\t')):
                    continue

                # :: 주석 스킵
                if stripped.startswith(b'::'):
                    continue

                # 비ASCII 바이트 찾기 (0x80 이상)
                non_ascii = [(i, b) for i, b in enumerate(line) if b >= 0x80]

                if non_ascii:
                    issues.append({
                        'file': fpath,
                        'line': lineno,
                        'content': line,
                        'non_ascii': non_ascii
                    })
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

print(f"=== 비ASCII 바이트를 포함한 명령어 줄 (총 {len(issues)}개) ===\n")

for issue in issues:
    print(f"파일: {issue['file']}")
    print(f"줄 {issue['line']}: {issue['content']!r}")
    print(f"비ASCII 바이트: {[(f'pos={i}', f'0x{b:02X}') for i, b in issue['non_ascii']]}")

    # 해당 바이트들이 CP949에서 어떻게 보이는지
    try:
        cp949_view = issue['content'].decode('cp949', errors='replace')
        print(f"CP949로 읽으면: {cp949_view!r}")
    except Exception as e:
        print(f"CP949 decode error: {e}")
    print()

if not issues:
    print("✅ 비ASCII 바이트를 포함한 명령어 줄이 없습니다.")
    print("→ 배치파일들의 명령어 줄은 모두 순수 ASCII입니다.")
    print("→ 팝업의 원인은 배치파일 인코딩이 아닙니다.")
