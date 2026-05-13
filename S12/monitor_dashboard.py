#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 감시 프로그램 모니터링 대시보드

현재 실행중인 감시 프로그램들의 상태를 확인하고 제어합니다.
- 프로세스 상태 확인 (실행중/정지)
- 원클릭 시작/재시작
- 로그 파일 마지막 업데이트 시간 확인
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import time
import json
from typing import Dict, List, Optional, Tuple
import re

# Windows 콘솔 인코딩 설정
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 모니터링 대상 프로그램 설정
MONITORED_PROGRAMS = [
    {
        "name": "S1 주식 실시간 모니터",
        "script": "Real_Time_Monitor_S1.py",
        "bat_file": "run_real_time_monitor_s1.bat",  # S1 폴더의 BAT 파일
        "log_pattern": "realtime_monitor_*.log",
        "description": "거래일 08:00-20:00, 10분 간격 (S1)",
        "enabled": True,
        "process_key": None,  # S1은 스크립트명으로만 구분 (Real_Time_Monitor_S1.py)
        "working_dir": r"C:\Users\log\Desktop\Code\S1"  # S1 폴더에서 실행
    },
    {
        "name": "S12 주식 실시간 모니터",
        "script": "Real_Time_Monitor.py",
        "bat_file": "run_real_time_monitor.bat",
        "log_pattern": "realtime_monitor_*.log",
        "description": "거래일 08:00-20:00, 10분 간격 (S12)",
        "enabled": True,
        "process_key": "trading_signals"  # 프로세스 구분용
    },
    {
        "name": "업비트 시장 하락 감시",
        "script": "upbit_alert_optimized.py",
        "bat_file": "run_upbit_optimized.bat",
        "log_pattern": "upbit_alert_*.log",
        "description": "평일 09:00-18:00, 30분 간격",
        "enabled": True,
        "process_key": None
    },
    {
        "name": "암호화폐 실시간 모니터 (OMG)",
        "script": "crypto_realtime_monitor.py",
        "bat_file": "run_realtime_monitor_safe.bat",  # 중복 방지 기능 포함
        "log_pattern": None,  # 콘솔 출력
        "description": "00:00 파일갱신, 5분 간격 알람 (OMG Phase 1.5)",
        "enabled": True,
        "process_key": None,
        "working_dir": r"C:\Users\log\Desktop\Code\omg"
    }
]

class MonitorDashboard:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.status_cache_file = self.base_dir / "monitor_status_cache.json"

    def find_all_processes(self, script_name: str, process_key: Optional[str] = None) -> List[Dict]:
        """특정 Python 스크립트를 실행하는 모든 프로세스 찾기 (개선된 버전 - pythonw.exe 포함)"""
        processes = []
        try:
            # PowerShell로 python.exe와 pythonw.exe 프로세스 모두 조회
            # pythonw.exe는 백그라운드 실행 시 사용됨
            ps_script = "Get-WmiObject Win32_Process -Filter \"name='python.exe' OR name='pythonw.exe'\" | Select-Object ProcessId,CommandLine,CreationDate,Name | ConvertTo-Json"

            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    import json
                    procs = json.loads(result.stdout.strip())

                    # 단일 객체인 경우 리스트로 변환
                    if not isinstance(procs, list):
                        procs = [procs]

                    # 스크립트 이름 정규화 (경로 구분자 통일, 파일명만 추출)
                    script_name_normalized = script_name.lower().replace('/', '\\').replace('\\', '/')
                    script_basename = Path(script_name).stem.lower()  # 확장자 제거한 파일명
                    script_fullname = Path(script_name).name.lower()  # 파일명만

                    for proc in procs:
                        if not proc or 'CommandLine' not in proc:
                            continue

                        cmd = proc['CommandLine']
                        if not cmd:
                            continue

                        cmd_lower = cmd.lower()
                        # 경로 구분자 통일 (백슬래시/슬래시 모두 처리)
                        cmd_normalized = cmd_lower.replace('/', '\\')

                        # 매칭 여부 확인 (여러 방법 시도)
                        matches = False

                        # 방법 1: 전체 경로 포함 여부
                        if script_name_normalized in cmd_normalized or script_name.lower() in cmd_lower:
                            matches = True
                        
                        # 방법 2: 파일명만으로 매칭 (경로가 다른 경우 대비)
                        if not matches:
                            # 명령줄에서 파일명 추출 시도
                            if script_basename in cmd_normalized or script_fullname in cmd_normalized:
                                # 추가 검증: 확장자 포함 여부 확인
                                if script_fullname in cmd_normalized or f"{script_basename}.py" in cmd_normalized:
                                    matches = True

                        if not matches:
                            continue

                        # process_key가 있으면 더 구체적으로 필터링
                        if process_key:
                            if process_key == "trading_signals_s1":
                                if "trading_signals_s1" not in cmd_lower:
                                    continue
                            elif process_key == "trading_signals":
                                if "trading_signals" not in cmd_lower or "trading_signals_s1" in cmd_lower:
                                    continue

                        # 프로세스 이름 확인 (python.exe 또는 pythonw.exe)
                        proc_name = proc.get('Name', 'python.exe')
                        processes.append({
                            "pid": int(proc['ProcessId']),
                            "name": proc_name,
                            "creation_date": proc.get('CreationDate', ''),
                            "command_line": cmd  # 디버깅용
                        })

                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    print(f"⚠️ 프로세스 파싱 오류: {e}")

        except Exception as e:
            print(f"⚠️ 프로세스 조회 오류: {e}")

        return processes

    def find_process(self, script_name: str, process_key: Optional[str] = None) -> Optional[Dict]:
        """특정 Python 스크립트를 실행하는 프로세스 찾기 (첫 번째만)"""
        processes = self.find_all_processes(script_name, process_key)
        return processes[0] if processes else None

    def find_process_by_key(self, script_name: str, process_key: str) -> Optional[Dict]:
        """process_key를 사용하여 특정 프로세스 찾기 (S1/S12 구분용)"""
        try:
            # PowerShell로 명령줄 포함하여 프로세스 찾기
            ps_script = "Get-WmiObject Win32_Process -Filter \"name='python.exe' OR name='pythonw.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json"

            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    import json
                    procs = json.loads(result.stdout.strip())

                    # 단일 객체인 경우 리스트로 변환
                    if not isinstance(procs, list):
                        procs = [procs]

                    for proc in procs:
                        if not proc or 'CommandLine' not in proc:
                            continue

                        cmd = proc['CommandLine']
                        if not cmd:
                            continue

                        cmd_lower = cmd.lower()

                        # 스크립트 이름 확인
                        if script_name.lower() not in cmd_lower:
                            continue

                        # process_key로 S1/S12 구분
                        if process_key == "trading_signals_s1":
                            # S1: trading_signals_s1.xlsx 포함
                            if "trading_signals_s1" in cmd_lower:
                                return {"pid": int(proc['ProcessId']), "name": "python.exe"}
                        elif process_key == "trading_signals":
                            # S12: trading_signals.xlsx 포함하되 trading_signals_s1 미포함
                            if "trading_signals" in cmd_lower and "trading_signals_s1" not in cmd_lower:
                                return {"pid": int(proc['ProcessId']), "name": "python.exe"}

                except (json.JSONDecodeError, ValueError, KeyError):
                    pass
        except Exception:
            pass
        return None

    def get_latest_log_file(self, pattern: Optional[str], working_dir: Optional[str] = None) -> Optional[Path]:
        """패턴에 맞는 가장 최근 로그 파일 찾기"""
        if pattern is None:
            return None
        try:
            import glob
            search_dir = Path(working_dir) if working_dir else self.base_dir
            log_files = list(search_dir.glob(pattern))
            if log_files:
                return max(log_files, key=lambda p: p.stat().st_mtime)
        except Exception:
            pass
        return None

    def get_log_status(self, log_file: Path) -> Tuple[str, str]:
        """로그 파일 상태 확인"""
        if not log_file or not log_file.exists():
            return "❌", "로그 없음"

        try:
            # 마지막 수정 시간
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            now = datetime.now()
            delta = now - mtime

            # 5분 이내: 활성, 1시간 이내: 정상, 그 이상: 오래됨
            if delta < timedelta(minutes=5):
                status = "🟢"
                time_str = f"{int(delta.total_seconds())}초 전"
            elif delta < timedelta(hours=1):
                status = "🟡"
                time_str = f"{int(delta.total_seconds() / 60)}분 전"
            else:
                status = "🟠"
                time_str = mtime.strftime("%H:%M")

            return status, time_str
        except Exception:
            return "❓", "확인 불가"

    def check_program_status(self, program: Dict) -> Dict:
        """개별 프로그램 상태 확인 (개선된 버전)"""
        if not program["enabled"]:
            return {
                "running": False,
                "status": "⚪",
                "status_text": "비활성화",
                "pid": None,
                "duplicate_count": 0,
                "log_status": "❌",
                "log_time": "N/A"
            }

        # 모든 일치하는 프로세스 찾기
        process_key = program.get("process_key")
        if process_key:
            processes = self.find_all_processes(program["script"], process_key)
        else:
            processes = self.find_all_processes(program["script"])

        # 프로세스를 찾지 못한 경우 강제 검색 시도 (상태 확인 시에도)
        if not processes:
            working_dir = program.get("working_dir")
            processes = self.find_all_processes_force(program["script"], working_dir, process_key)
            # 강제 검색으로 찾은 경우 디버깅 정보 출력 (조용히)
            if processes:
                # 디버깅: 강제 검색으로 프로세스를 찾았지만 일반 검색에서는 못 찾은 경우
                pass  # 필요시 로그 출력 가능

        running = len(processes) > 0
        pid = processes[0]["pid"] if processes else None
        duplicate_count = len(processes)

        # 로그 확인 (log_pattern과 working_dir 전달)
        working_dir = program.get("working_dir")
        log_file = self.get_latest_log_file(program["log_pattern"], working_dir)
        log_status, log_time = self.get_log_status(log_file)

        # 종합 상태 (중복 실행 고려)
        if running:
            if duplicate_count > 1:
                status = "⚠️"
                status_text = f"중복실행 ({duplicate_count}개)"
            else:
                status = "🟢"
                status_text = "실행중"
        else:
            status = "🔴"
            status_text = "정지"

        return {
            "running": running,
            "status": status,
            "status_text": status_text,
            "pid": pid,
            "duplicate_count": duplicate_count,
            "all_pids": [p["pid"] for p in processes],
            "log_status": log_status,
            "log_time": log_time
        }

    def start_program(self, program: Dict) -> bool:
        """프로그램 시작 (중복 실행 방지 강화)"""
        try:
            # 시작 전 프로세스 재확인 (중복 실행 방지)
            process_key = program.get("process_key")
            if process_key:
                existing_processes = self.find_all_processes(program["script"], process_key)
            else:
                existing_processes = self.find_all_processes(program["script"])
            
            # 프로세스를 찾지 못한 경우 강제 검색 시도
            if not existing_processes:
                working_dir = program.get("working_dir")
                process_key = program.get("process_key")
                existing_processes = self.find_all_processes_force(program["script"], working_dir, process_key)

            # python이 종료된 후 CMD가 pause 상태로 남아있는 경우도 중복으로 감지
            if not existing_processes and program.get("bat_file"):
                bat_file = program["bat_file"]
                try:
                    cmd_result = subprocess.run(
                        ['powershell', '-Command',
                         f'@(Get-WmiObject Win32_Process | Where-Object {{ $_.Name -eq "cmd.exe" -and $_.CommandLine -like "*{bat_file}*" }}).Count'],
                        capture_output=True, text=True, encoding='utf-8', timeout=5
                    )
                    if cmd_result.returncode == 0:
                        count = int(cmd_result.stdout.strip() or '0')
                        if count > 0:
                            existing_processes = [{'pid': 0, 'command_line': f'CMD running {bat_file} (pause 상태)'}]
                except Exception:
                    pass

            if existing_processes:
                print(f"⚠️ 경고: 이미 실행 중인 프로세스가 {len(existing_processes)}개 발견되었습니다!")
                for proc in existing_processes:
                    print(f"  - PID {proc['pid']}: {proc.get('command_line', 'N/A')[:80]}...")
                
                # 사용자에게 선택권 제공
                print(f"\n선택:")
                print(f"  1. 기존 프로세스를 종료하고 새로 시작")
                print(f"  2. 기존 프로세스를 유지하고 시작 취소")
                choice = input("선택 (1/2, 기본값: 2): ").strip()
                
                if choice == "1":
                    print(f"⏹️ 기존 프로세스 종료 중...")
                    if self.stop_program(program):
                        print(f"✅ 기존 프로세스 종료 완료")
                        time.sleep(2)  # 프로세스 종료 대기
                    else:
                        print(f"❌ 기존 프로세스 종료 실패. 새 프로세스 시작을 중단합니다.")
                        return False
                else:
                    print(f"⚠️ 시작 취소됨. 기존 프로세스를 유지합니다.")
                    return False

            # working_dir이 지정된 경우 처리
            working_dir = program.get("working_dir")

            # bat 파일이 있으면 bat 파일로 실행
            if program["bat_file"]:
                # working_dir이 있으면 해당 디렉토리에서 bat 파일 찾기
                if working_dir:
                    bat_path = Path(working_dir) / program["bat_file"]
                else:
                    bat_path = self.base_dir / program["bat_file"]

                print(f"📍 BAT 파일 경로: {bat_path}")
                print(f"📍 파일 존재 여부: {bat_path.exists()}")

                if bat_path.exists():
                    # working_dir로 이동하여 실행
                    cwd = working_dir if working_dir else None
                    print(f"📍 작업 디렉토리: {cwd}")

                    # S1, S12 실시간 모니터는 백그라운드로 실행
                    if "S1" in program["name"] or "S12" in program["name"] or "Real_Time_Monitor" in str(bat_path):
                        # 백그라운드 실행 (콘솔 창 없이)
                        print(f"📍 백그라운드로 실행 중...")
                        subprocess.Popen([str(bat_path)],
                                       shell=True,
                                       cwd=cwd,
                                       creationflags=subprocess.CREATE_NO_WINDOW,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                    else:
                        # 다른 프로그램은 새 콘솔 창에서 실행
                        print(f"📍 새 콘솔 창에서 실행 중... (BAT)")
                        subprocess.Popen([str(bat_path)],
                                       shell=True,
                                       cwd=cwd,
                                       creationflags=subprocess.CREATE_NEW_CONSOLE)
                    time.sleep(3)  # 프로세스 시작 대기 (pythonw는 백그라운드 실행이므로 더 긴 대기)
                    
                    # 프로세스 시작 확인
                    process_key = program.get("process_key")
                    if process_key:
                        processes = self.find_all_processes(program["script"], process_key)
                    else:
                        processes = self.find_all_processes(program["script"])
                    
                    if len(processes) > 0:
                        print(f"✅ 프로세스 시작 확인됨 (PID: {processes[0]['pid']}, {processes[0].get('name', 'python.exe')})")
                        return True
                    else:
                        print(f"⚠️ 프로세스가 시작되었으나 확인되지 않습니다. 잠시 후 다시 확인합니다...")
                        time.sleep(2)  # 추가 대기
                        # 재확인
                        if process_key:
                            processes = self.find_all_processes(program["script"], process_key)
                        else:
                            processes = self.find_all_processes(program["script"])
                        
                        if len(processes) > 0:
                            print(f"✅ 프로세스 시작 확인됨 (PID: {processes[0]['pid']}, {processes[0].get('name', 'python.exe')})")
                            return True
                        else:
                            print(f"⚠️ 프로세스를 찾을 수 없습니다. BAT 파일 실행 로그를 확인하세요.")
                            return False
                else:
                    print(f"⚠️ BAT 파일이 없어서 직접 Python 스크립트 실행을 시도합니다.")

            # bat 파일이 없으면 직접 Python 스크립트 실행
            if working_dir:
                script_path = Path(working_dir) / program["script"]
            else:
                script_path = self.base_dir / program["script"]

            if not script_path.exists():
                print(f"❌ 파일을 찾을 수 없습니다: {script_path}")
                return False

            print(f"📍 실행 경로: {script_path}")
            print(f"📍 작업 디렉토리: {working_dir if working_dir else '(기본)'}")

            # Python 경로 찾기
            python_exe = sys.executable
            cwd = working_dir if working_dir else None

            # S1, S12 실시간 모니터는 백그라운드로 실행
            if "Real_Time_Monitor" in str(script_path) or "S1" in program["name"] or "S12" in program["name"]:
                # 백그라운드 실행 (콘솔 창 없이)
                print(f"📍 백그라운드로 실행 중...")
                subprocess.Popen([python_exe, str(script_path)],
                               cwd=cwd,
                               creationflags=subprocess.CREATE_NO_WINDOW,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            else:
                # 암호화폐 모니터 등 다른 프로그램은 새 콘솔 창에서 실행
                print(f"📍 새 콘솔 창에서 실행 중...")
                subprocess.Popen([python_exe, str(script_path)],
                               cwd=cwd,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)

            # 프로세스 시작 대기 및 확인
            time.sleep(3)

            # 실제로 프로세스가 실행 중인지 확인
            process_key = program.get("process_key")
            if process_key:
                processes = self.find_all_processes(program["script"], process_key)
            else:
                processes = self.find_all_processes(program["script"])

            if len(processes) > 0:
                print(f"✅ 프로세스 시작 확인됨 (PID: {processes[0]['pid']}, {processes[0].get('name', 'python.exe')})")
                return True
            else:
                print(f"⚠️ 프로세스가 시작되었으나 즉시 종료되었습니다.")
                print(f"⚠️ 콘솔 창의 에러 메시지를 확인하세요.")
                return False

        except Exception as e:
            print(f"❌ 시작 실패: {e}")
            import traceback
            traceback.print_exc()
        return False

    def find_all_processes_force(self, script_name: str, working_dir: Optional[str] = None, process_key: Optional[str] = None) -> List[Dict]:
        """강제 검색: 모든 python.exe/pythonw.exe 프로세스를 조회하고 더 넓은 범위로 필터링"""
        processes = []
        try:
            ps_script = "Get-WmiObject Win32_Process -Filter \"name='python.exe' OR name='pythonw.exe'\" | Select-Object ProcessId,CommandLine,CreationDate,Name | ConvertTo-Json"
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    import json
                    procs = json.loads(result.stdout.strip())
                    if not isinstance(procs, list):
                        procs = [procs]

                    script_basename = Path(script_name).stem.lower()
                    script_fullname = Path(script_name).name.lower()
                    
                    # working_dir이 있으면 해당 디렉토리 경로도 확인
                    working_dir_lower = None
                    if working_dir:
                        working_dir_lower = Path(working_dir).as_posix().lower()

                    for proc in procs:
                        if not proc or 'CommandLine' not in proc:
                            continue
                        cmd = proc.get('CommandLine', '')
                        if not cmd:
                            continue

                        cmd_lower = cmd.lower()
                        cmd_normalized = cmd_lower.replace('/', '\\')

                        # 더 넓은 범위로 매칭 시도
                        matches = False
                        
                        # 1. 파일명 매칭
                        if script_fullname in cmd_normalized or script_basename in cmd_normalized:
                            matches = True
                        
                        # 2. working_dir이 있고 해당 경로에 스크립트가 있는 경우
                        if not matches and working_dir_lower:
                            if working_dir_lower in cmd_normalized and script_basename in cmd_normalized:
                                matches = True

                        if not matches:
                            continue

                        # process_key가 있으면 더 구체적으로 필터링 (S1/S12 구분)
                        if process_key:
                            if process_key == "trading_signals_s1":
                                if "trading_signals_s1" not in cmd_lower:
                                    continue
                            elif process_key == "trading_signals":
                                if "trading_signals" not in cmd_lower or "trading_signals_s1" in cmd_lower:
                                    continue

                        proc_name = proc.get('Name', 'python.exe')
                        processes.append({
                            "pid": int(proc['ProcessId']),
                            "name": proc_name,
                            "creation_date": proc.get('CreationDate', ''),
                            "command_line": cmd
                        })

                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    print(f"⚠️ 강제 검색 파싱 오류: {e}")

        except Exception as e:
            print(f"⚠️ 강제 검색 오류: {e}")

        return processes

    def stop_program(self, program: Dict) -> bool:
        """프로그램 정지 (모든 중복 프로세스 종료) - 개선된 버전"""
        try:
            # 모든 일치하는 프로세스 찾기
            process_key = program.get("process_key")
            if process_key:
                processes = self.find_all_processes(program["script"], process_key)
            else:
                processes = self.find_all_processes(program["script"])

            # 프로세스를 찾지 못한 경우 강제 검색 시도
            if not processes:
                print(f"⚠️ 일반 검색으로 프로세스를 찾지 못했습니다. 강제 검색을 시도합니다...")
                working_dir = program.get("working_dir")
                process_key = program.get("process_key")
                processes = self.find_all_processes_force(program["script"], working_dir, process_key)
                
                if processes:
                    print(f"  🔍 강제 검색으로 {len(processes)}개 프로세스 발견")
                    for proc in processes:
                        print(f"    - PID {proc['pid']}: {proc.get('command_line', 'N/A')[:80]}...")
                else:
                    print(f"⚠️ 실행 중인 프로세스를 찾을 수 없습니다.")
                    print(f"   스크립트: {program['script']}")
                    if program.get("working_dir"):
                        print(f"   작업 디렉토리: {program['working_dir']}")
                    return False

            # 모든 프로세스 종료
            killed_count = 0
            failed_pids = []
            for proc in processes:
                pid = proc["pid"]
                try:
                    result = subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                                         capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        killed_count += 1
                        print(f"  ✅ PID {pid} 종료")
                    else:
                        failed_pids.append(pid)
                        print(f"  ⚠️ PID {pid} 종료 실패: {result.stderr.strip()}")
                except subprocess.TimeoutExpired:
                    failed_pids.append(pid)
                    print(f"  ⚠️ PID {pid} 종료 타임아웃")
                except Exception as e:
                    failed_pids.append(pid)
                    print(f"  ❌ PID {pid} 종료 실패: {e}")

            time.sleep(1)

            # 종료 후 재확인
            if process_key:
                remaining = self.find_all_processes(program["script"], process_key)
            else:
                remaining = self.find_all_processes(program["script"])
            
            if remaining:
                print(f"  ⚠️ {len(remaining)}개 프로세스가 여전히 실행 중입니다.")
                for proc in remaining:
                    print(f"    - PID {proc['pid']}")

            if killed_count > 0:
                print(f"✅ 총 {killed_count}개 프로세스 종료 완료")
                if failed_pids:
                    print(f"⚠️ {len(failed_pids)}개 프로세스 종료 실패: {failed_pids}")
                return True
            else:
                print(f"❌ 프로세스 종료 실패")
                return False

        except Exception as e:
            print(f"❌ 정지 실패: {e}")
            import traceback
            traceback.print_exc()
        return False

    def cleanup_duplicate_processes(self, program: Dict) -> Tuple[int, int]:
        """중복 프로세스 정리 - 가장 최신 프로세스만 남기고 나머지 종료

        Returns:
            (killed_count, kept_pid): 종료한 개수와 유지한 PID
        """
        try:
            # 모든 일치하는 프로세스 찾기
            process_key = program.get("process_key")
            if process_key:
                processes = self.find_all_processes(program["script"], process_key)
            else:
                processes = self.find_all_processes(program["script"])

            if len(processes) <= 1:
                return (0, processes[0]["pid"] if processes else None)

            # PID가 큰 것이 나중에 실행된 것 (일반적으로)
            # PID 기준으로 정렬하여 가장 큰 것(최신) 유지
            processes.sort(key=lambda p: p["pid"], reverse=True)

            kept_process = processes[0]
            killed_count = 0

            # 나머지 프로세스 종료
            for proc in processes[1:]:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(proc["pid"])],
                                 capture_output=True)
                    killed_count += 1
                except Exception:
                    pass

            time.sleep(1)
            return (killed_count, kept_process["pid"])

        except Exception as e:
            print(f"❌ 중복 정리 실패: {e}")
            return (0, None)

    def display_dashboard(self):
        """대시보드 출력"""
        # 화면 지우기
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=" * 80)
        print("🖥️  실시간 감시 프로그램 모니터링 대시보드")
        print("=" * 80)
        print(f"⏰ 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # 각 프로그램 상태 확인 및 출력
        statuses = []
        for idx, program in enumerate(MONITORED_PROGRAMS, 1):
            status = self.check_program_status(program)
            statuses.append((program, status))

            print(f"{idx}. {program['name']}")
            print(f"   상태: {status['status']} {status['status_text']}", end="")
            if status['pid']:
                print(f" (PID: {status['pid']})", end="")
            print()

            # 중복 실행 시 모든 PID 표시
            if status.get('duplicate_count', 0) > 1:
                all_pids = status.get('all_pids', [])
                print(f"   ⚠️ 중복 PID: {', '.join(map(str, all_pids))}")

            print(f"   설명: {program['description']}")
            print(f"   로그: {status['log_status']} {status['log_time']}")
            print()

        print("=" * 80)
        print("명령어:")
        print("  [1-9]    : 해당 번호 프로그램 시작/재시작")
        print("  s[1-9]   : 해당 번호 프로그램 정지")
        print("  a        : 모든 프로그램 시작")
        print("  x        : 모든 프로그램 정지")
        print("  d        : 중복 프로세스 정리 (최신만 유지)")
        print("  r        : 화면 새로고침 (자동: 30초)")
        print("  q        : 종료")
        print("=" * 80)

        return statuses

    def handle_command(self, cmd: str, statuses: List) -> bool:
        """사용자 명령 처리"""
        cmd = cmd.strip().lower()

        if cmd == 'q':
            return False

        elif cmd == 'r':
            return True

        elif cmd == 'a':
            print("\n🚀 모든 프로그램 시작 중...")
            for program, status in statuses:
                if program["enabled"] and not status["running"]:
                    print(f"  ▶️ {program['name']} 시작 중...")
                    if self.start_program(program):
                        print(f"  ✅ {program['name']} 시작됨")
                    else:
                        print(f"  ❌ {program['name']} 시작 실패")
            time.sleep(2)
            return True

        elif cmd == 'x':
            print("\n🛑 모든 프로그램 정지 중...")
            for program, status in statuses:
                if status["running"]:
                    print(f"  ⏹️ {program['name']} 정지 중...")
                    if self.stop_program(program):
                        print(f"  ✅ {program['name']} 정지됨")
                    else:
                        print(f"  ❌ {program['name']} 정지 실패")
            time.sleep(2)
            return True

        elif cmd == 'd':
            print("\n🧹 중복 프로세스 정리 중...")
            total_killed = 0
            for program, status in statuses:
                if status.get('duplicate_count', 0) > 1:
                    print(f"  🔧 {program['name']} - {status['duplicate_count']}개 중복 발견")
                    killed, kept_pid = self.cleanup_duplicate_processes(program)
                    if killed > 0:
                        total_killed += killed
                        print(f"  ✅ {killed}개 종료, PID {kept_pid} 유지")
                    else:
                        print(f"  ⚠️ 정리 실패")

            if total_killed > 0:
                print(f"\n✅ 총 {total_killed}개 중복 프로세스 정리 완료")
            else:
                print(f"\n✅ 중복 프로세스 없음")
            time.sleep(2)
            return True

        elif cmd.startswith('s') and len(cmd) > 1:
            # 정지 명령
            try:
                idx = int(cmd[1:]) - 1
                if 0 <= idx < len(statuses):
                    program, status = statuses[idx]
                    if status["running"]:
                        print(f"\n⏹️ {program['name']} 정지 중...")
                        if self.stop_program(program):
                            print(f"✅ {program['name']} 정지됨")
                        else:
                            print(f"❌ {program['name']} 정지 실패")
                    else:
                        print(f"\n⚠️ {program['name']}는 이미 정지되어 있습니다.")
                    time.sleep(2)
                    return True
            except ValueError:
                pass

        elif cmd.isdigit():
            # 시작/재시작 명령
            idx = int(cmd) - 1
            if 0 <= idx < len(statuses):
                program, status = statuses[idx]

                # 이미 실행중이면 재시작 확인
                if status["running"]:
                    print(f"\n⚠️ {program['name']}는 이미 실행중입니다.")
                    confirm = input("재시작하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y':
                        print(f"⏹️ {program['name']} 정지 중...")
                        self.stop_program(program)
                        time.sleep(1)

                print(f"🚀 {program['name']} 시작 중...")
                if self.start_program(program):
                    print(f"✅ {program['name']} 시작됨")
                else:
                    print(f"❌ {program['name']} 시작 실패")
                time.sleep(2)
                return True

        print("\n❌ 알 수 없는 명령입니다.")
        time.sleep(1)
        return True

    def run(self, auto_refresh_seconds: int = 30):
        """대시보드 메인 루프 (자동 새로고침 기능)"""
        print("🖥️  모니터링 대시보드를 시작합니다...")
        print(f"   (자동 새로고침: {auto_refresh_seconds}초)")
        time.sleep(1)

        try:
            import msvcrt

            last_refresh = time.time()

            while True:
                statuses = self.display_dashboard()

                # 입력 대기 (non-blocking with auto-refresh)
                print(f"\n명령 입력 (자동 새로고침: {auto_refresh_seconds}초): ", end='', flush=True)

                cmd = ""
                start_time = time.time()

                while True:
                    # 키 입력 확인
                    if msvcrt.kbhit():
                        char = msvcrt.getch()
                        if char == b'\r':  # Enter
                            print()
                            break
                        elif char == b'\x08':  # Backspace
                            if cmd:
                                cmd = cmd[:-1]
                                print('\b \b', end='', flush=True)
                        else:
                            try:
                                c = char.decode('utf-8')
                                cmd += c
                                print(c, end='', flush=True)
                            except:
                                pass

                    # 자동 새로고침 체크
                    if time.time() - last_refresh > auto_refresh_seconds:
                        print("\n\n🔄 [자동 새로고침...]")
                        time.sleep(0.5)
                        last_refresh = time.time()
                        cmd = ""  # 입력 초기화
                        break

                    time.sleep(0.1)

                # 명령 처리
                if cmd.strip():
                    last_refresh = time.time()  # 명령 입력 시 타이머 리셋
                    if not self.handle_command(cmd, statuses):
                        break

        except KeyboardInterrupt:
            print("\n\n👋 대시보드를 종료합니다.")
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

def main():
    """메인 함수"""
    dashboard = MonitorDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
