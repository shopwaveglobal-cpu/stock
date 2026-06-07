#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
암호화폐 실시간 모니터링 시스템

기능:
1. 기존 ANALYSIS 파일에서 B1~B7 값 로드
2. 5분 간격으로 실시간 가격과 비교하여 알람 전송
3. forbidden 베이스 알람 로직:
   - cutoff_price보다 높은 레벨은 알람 차단
   - 각 레벨당 1회만 알람 (RESTART 시 초기화)
   - SELL 없으면 "첫 자리" 마커 표시

주의:
- 00:00 일일 업데이트는 daily_update.py에서 별도로 실행됨
- 이 파일은 실시간 모니터링 전용
"""

import os
import sys
import pandas as pd
import requests
import time
import json
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import subprocess
import pathlib

# S12 디렉토리의 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from telegram_notifier import send_telegram_message

try:
    from slack_notifier import send_slack_alert, send_slack_buy_execution_alert
except ImportError:
    print(f"Warning: Could not import slack_notifier. Slack 알림은 건너뜁니다.")
    send_slack_alert = None
    send_slack_buy_execution_alert = None

class CryptoRealtimeMonitor:
    def __init__(self):
        self.omg_dir = pathlib.Path(__file__).parent  # 현재 스크립트 위치
        self.analysis_file = None
        self.monitoring_data = {}  # {symbol: {next_target, buy_levels, rank, name}}
        self.alert_history = {}  # {symbol: {target: sent_date}}
        self.alert_history_file = "alert_history.json"

        # 알람 이력 로드
        self.load_alert_history()
        
    def load_alert_history(self):
        """알람 이력 로드"""
        try:
            if os.path.exists(self.alert_history_file):
                with open(self.alert_history_file, 'r', encoding='utf-8') as f:
                    self.alert_history = json.load(f)
        except Exception as e:
            print(f"알람 이력 로드 실패: {e}")
            self.alert_history = {}
    
    def save_alert_history(self):
        """알람 이력 저장"""
        try:
            with open(self.alert_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.alert_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"알람 이력 저장 실패: {e}")

    def should_send_alert_for_level(self, symbol: str, target_level: str) -> Tuple[bool, bool]:
        """
        레벨별 알람 전송 여부 판단 (forbidden 베이스 로직)

        로직:
        1. forbidden 체크: cutoff_price보다 높은 레벨은 금지
        2. 중복 알람 체크: 이미 알람 보낸 레벨은 차단
        3. 첫 자리 판단: SELL 없으면 "첫 자리" 마커 추가

        Args:
            symbol: 코인 심볼 (예: "BTC")
            target_level: 현재 근접한 레벨 (예: "B1", "B2", "B7")

        Returns:
            Tuple[bool, bool]: (알람 전송 여부, 첫 자리 여부)
        """
        try:
            # 1. debug 파일 읽기
            debug_file = f"debug/{symbol.lower()}_debug.csv"
            if not os.path.exists(debug_file):
                return (False, False)

            df = pd.read_csv(debug_file)

            # 2. 최신 스냅샷
            snapshots = df[df['event'].isna() | (df['event'] == '')]
            if len(snapshots) == 0:
                return (False, False)

            last_snapshot = snapshots.iloc[-1]

            # 3. cutoff_price 확인
            cutoff_price = last_snapshot.get('cutoff_price')
            if pd.isna(cutoff_price):
                cutoff_price = None
            else:
                cutoff_price = float(cutoff_price)

            # 4. target_level 가격 확인
            target_price = last_snapshot.get(target_level)
            if pd.isna(target_price):
                return (False, False)
            else:
                target_price = float(target_price)

            # 5. forbidden 체크 (베이스 로직)
            if cutoff_price is not None and target_price > cutoff_price:
                return (False, False)  # 금지 레벨

            # 6. RESTART 추적 (없으면 첫 행 날짜를 기준점으로 사용)
            restart_events = df[df['event'].str.contains('RESTART', na=False)]
            if len(restart_events) == 0:
                last_restart_date = str(df.iloc[0]['date']) if len(df) > 0 else "0000-00-00"
            else:
                last_restart_date = restart_events.iloc[-1]['date']

            # 7. alert_history 초기화
            if symbol not in self.alert_history:
                self.alert_history[symbol] = {}

            if "last_restart_date" not in self.alert_history[symbol]:
                self.alert_history[symbol]["last_restart_date"] = last_restart_date

            # RESTART 날짜 변경 시 초기화
            if self.alert_history[symbol]["last_restart_date"] != last_restart_date:
                self.alert_history[symbol]["last_restart_date"] = last_restart_date
                self.alert_history[symbol]["alerted_levels"] = {}

            if "alerted_levels" not in self.alert_history[symbol]:
                self.alert_history[symbol]["alerted_levels"] = {}

            # 8. 중복 알람 체크 (메인 로직)
            if target_level in self.alert_history[symbol]["alerted_levels"]:
                return (False, False)  # 이미 알람 보냄

            # 9. 첫 자리 판단 (마커용)
            if len(restart_events) > 0:
                after_restart = df.loc[restart_events.index[-1] + 1:]
            else:
                after_restart = df  # RESTART 없으면 전체 파일 기준
            sell_events = after_restart[after_restart['event'].str.contains('SELL', na=False)]
            is_first = (len(sell_events) == 0)

            # 10. 알람 기록
            self.alert_history[symbol]["alerted_levels"][target_level] = True
            self.save_alert_history()

            return (True, is_first)

        except Exception as e:
            print(f"알람 조건 확인 실패 ({symbol} {target_level}): {e}")
            return (False, False)
    
    def reload_analysis_data(self):
        """ANALYSIS 파일 재로드 (파일 갱신 없이 읽기만)"""
        print(f"[{datetime.now()}] ANALYSIS 파일 재로드 중...")

        try:
            # 최신 ANALYSIS 파일 찾기
            output_dir = self.omg_dir / "output"
            analysis_files = list(output_dir.glob("coin_analysis_*.xlsx"))
            if not analysis_files:
                print("[ERROR] ANALYSIS 파일을 찾을 수 없습니다.")
                return False

            # 가장 최신 파일 선택
            self.analysis_file = max(analysis_files, key=os.path.getctime)
            print(f"[INFO] ANALYSIS 파일: {self.analysis_file.name}")

            # ANALYSIS 파일에서 모니터링 데이터 로드
            self.load_monitoring_data()

            # 알람 이력은 RESTART 시에만 초기화 (날짜 기반 초기화 제거)
            # should_send_alert_for_level()에서 RESTART 날짜 변경 시 자동 초기화

            print(f"[OK] 데이터 재로드 완료! [{datetime.now()}]")
            return True

        except Exception as e:
            print(f"[ERROR] 데이터 재로드 실패: {e}")
            return False
    
    def load_monitoring_data(self):
        """ANALYSIS 파일에서 모니터링 데이터 로드"""
        if not self.analysis_file or not self.analysis_file.exists():
            print("ANALYSIS 파일이 없습니다.")
            return
        
        try:
            df = pd.read_excel(self.analysis_file)
            self.monitoring_data = []
            
            for _, row in df.iterrows():
                symbol = row['심볼']
                next_target = row['다음매수목표']
                
                # 모니터링 제외 조건
                if pd.isna(next_target) or next_target in ['', 'STOP LOSS (실행됨)']:
                    continue
                
                # B1~B7 값 추출
                buy_levels = {}
                for i in range(1, 8):
                    level_key = f'B{i}'
                    if level_key in row and pd.notna(row[level_key]):
                        try:
                            # 콤마 제거 후 변환
                            value_str = str(row[level_key]).replace(',', '')
                            buy_levels[level_key] = float(value_str)
                        except (ValueError, TypeError):
                            continue
                
                # Stop_Loss 값 추출
                if 'Stop_Loss' in row and pd.notna(row['Stop_Loss']):
                    try:
                        value_str = str(row['Stop_Loss']).replace(',', '')
                        buy_levels['Stop_Loss'] = float(value_str)
                    except (ValueError, TypeError):
                        pass
                
                # 현재가 처리
                current_price = 0
                if pd.notna(row['현재가']):
                    try:
                        current_price_str = str(row['현재가']).replace(',', '')
                        current_price = float(current_price_str)
                    except (ValueError, TypeError):
                        current_price = 0
                
                # H값 처리
                h_value = 0
                if pd.notna(row['H값']):
                    try:
                        h_value_str = str(row['H값']).replace(',', '')
                        h_value = float(h_value_str)
                    except (ValueError, TypeError):
                        h_value = 0
                
                # 순위 안전 처리 (NaN 체크)
                rank = 0
                if '순위' in row and pd.notna(row['순위']):
                    try:
                        rank_value = row['순위']
                        # 문자열이면 숫자로 변환 시도
                        if isinstance(rank_value, str):
                            rank_value = rank_value.replace(',', '').strip()
                        # float로 변환 후 정수로 변환 (NaN 체크)
                        import math
                        rank_float = float(rank_value)
                        if math.isnan(rank_float) or math.isinf(rank_float):
                            rank = 0
                        else:
                            rank = int(rank_float)
                    except (ValueError, TypeError, OverflowError):
                        rank = 0
                
                self.monitoring_data.append({
                    'symbol': symbol,
                    'next_target': next_target,
                    'buy_levels': buy_levels,
                    'rank': rank,
                    'name': row['코인명'],
                    'current_price': current_price,
                    'h_value': h_value
                })
            
            print(f"모니터링 데이터 로드 완료: {len(self.monitoring_data)}개 코인")
            
        except Exception as e:
            print(f"모니터링 데이터 로드 실패: {e}")
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """현재가 조회 (Binance Ticker API)"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            params = {"symbol": f"{symbol}USDT"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and 'price' in data:
                return float(data['price'])
            return None

        except Exception as e:
            print(f"{symbol} 현재가 조회 실패: {e}")
            return None

    def get_candle_low(self, symbol: str, interval: str = "5m") -> Optional[float]:
        """5분봉 저가 조회 (Binance Kline API) - 모니터링 간격에 맞춤"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": f"{symbol}USDT",
                "interval": interval,
                "limit": 1  # 최근 1개 봉
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                return float(data[0][3])  # 저가 (low)
            return None

        except Exception as e:
            print(f"{symbol} 5분봉 저가 조회 실패: {e}")
            return None
    
    def calculate_divergence(self, current_price: float, target_price: float) -> float:
        """이격도 계산 (현재가 기준)"""
        if target_price == 0:
            return float('inf')
        return abs((current_price - target_price) / target_price) * 100
    
    def check_buy_execution(self, coin_data: Dict) -> Optional[Dict]:
        """5분봉 저가로 매수 실행 감지"""
        symbol = coin_data['symbol']
        next_target = coin_data['next_target']
        buy_levels = coin_data['buy_levels']
        
        # 다음 매수 목표가가 B1~B7인 경우만 체크
        if not next_target.startswith('B'):
            return None
        
        target_price = buy_levels.get(next_target)
        if not target_price:
            return None
        
        # 5분봉 저가 조회
        candle_low = self.get_candle_low(symbol, interval="5m")
        if not candle_low:
            return None
        
        # 저가가 목표가에 도달했는지 확인
        if candle_low <= target_price:
            return {
                'symbol': symbol,
                'target': next_target,
                'next_target': next_target,
                'buy_levels': buy_levels,
                'target_price': target_price,
                'candle_low': candle_low,
                'rank': coin_data['rank'],
                'name': coin_data['name'],
                'h_value': coin_data['h_value']
            }
        
        return None
    
    def calculate_average_buy_and_sell_price(self, coin_data: Dict) -> Dict:
        """평균 매수선과 매도가 계산"""
        # execution_data는 'target', coin_data는 'next_target' 키 사용 → 둘 다 처리
        next_target = coin_data.get('next_target') or coin_data.get('target')  # 예: "B3"
        buy_levels = coin_data['buy_levels']
        
        # 매수 단계 추출 (B3 → 3)
        stage_num = int(next_target[1])
        
        # 1단계부터 현재 단계까지의 매수가들
        buy_prices = []
        for i in range(1, stage_num + 1):
            level_key = f'B{i}'
            if level_key in buy_levels and buy_levels[level_key]:
                buy_prices.append(buy_levels[level_key])
        
        # 평균 매수선 계산
        avg_buy_price = sum(buy_prices) / len(buy_prices)
        
        # 매도 기준 적용 (SELL_THRESHOLDS)
        sell_thresholds = {1: 7.7, 2: 17.3, 3: 24.4, 4: 37.4, 5: 52.7, 6: 79.9, 7: 98.5}
        sell_threshold = sell_thresholds[stage_num]
        sell_price = avg_buy_price * (1 + sell_threshold / 100)
        
        return {
            'avg_buy_price': avg_buy_price,
            'sell_price': sell_price,
            'sell_threshold': sell_threshold,
            'stage_num': stage_num
        }
    
    def get_allowed_targets(self, next_target: str) -> List[str]:
        """다음 매수 목표에 따른 허용 알람 목표 반환"""
        if next_target.startswith('B'):
            # B1~B7인 경우
            level_num = int(next_target[1])
            return [f'B{i}' for i in range(level_num, 8)] + ['STOP LOSS (실행 전)']
        elif next_target == 'STOP LOSS (실행 전)':
            return ['STOP LOSS (실행 전)']
        else:
            return []
    
    def check_alert_condition(self, coin_data: Dict, current_price: float) -> List[Tuple[Dict, bool]]:
        """알람 조건 확인 (forbidden 베이스 로직 적용)"""
        symbol = coin_data['symbol']
        next_target = coin_data['next_target']
        buy_levels = coin_data['buy_levels']

        # 허용되는 알람 목표들
        allowed_targets = self.get_allowed_targets(next_target)

        alerts = []

        for target in allowed_targets:
            if target not in buy_levels:
                continue

            target_price = buy_levels[target]
            divergence = self.calculate_divergence(current_price, target_price)

            # 5% 이내 접근 시 알람 조건 확인
            if divergence <= 5.0:
                # forbidden + 중복 체크 + 첫 자리 판단
                should_alert, is_first = self.should_send_alert_for_level(symbol, target)

                if should_alert:
                    alert_data = {
                        'symbol': symbol,
                        'target': target,
                        'target_price': target_price,
                        'current_price': current_price,
                        'divergence': divergence,
                        'rank': coin_data['rank'],
                        'name': coin_data['name'],
                        'h_value': coin_data['h_value']
                    }
                    alerts.append((alert_data, is_first))

        return alerts
    
    def format_price(self, price: float, h_value: float = None) -> str:
        """가격을 천 단위 콤마로 포맷팅 (H값에 따라 소수점 자릿수 조정)"""
        if price is None:
            return ""
        
        # H값에 따라 소수점 자릿수 결정
        if h_value is not None:
            if h_value <= 1:
                return f"{price:,.6f}"
            elif h_value <= 10:
                return f"{price:,.4f}"
        
        return f"{price:,.2f}"
    
    def get_sell_threshold(self, buy_level: str) -> Optional[float]:
        """매수 레벨에 따른 매도 기준 퍼센트 반환"""
        sell_thresholds = {
            'B1': 7.7,
            'B2': 17.3,
            'B3': 24.4,
            'B4': 37.4,
            'B5': 52.7,
            'B6': 79.9,
            'B7': 98.5
        }
        return sell_thresholds.get(buy_level)
    
    def send_alert(self, alert: Dict, is_first: bool):
        """텔레그램 알람 전송"""
        try:
            # 코인명에 "(첫 자리)" 마커 추가
            coin_display = f"{alert['name']} ({alert['symbol']})"
            if is_first:
                coin_display = f"{alert['name']} ({alert['symbol']}) (첫 자리)"
                emoji = "🆕"
            else:
                emoji = "🪙"

            # 가격 포맷팅 (H값 기반)
            h_value = alert.get('h_value', 0)
            current_price_str = self.format_price(alert['current_price'], h_value)
            target_price_str = self.format_price(alert['target_price'], h_value)
            h_value_str = self.format_price(h_value, h_value)

            # 매도 기준 퍼센트 가져오기
            sell_threshold = self.get_sell_threshold(alert['target'])
            sell_criteria_text = ""
            if sell_threshold:
                sell_criteria_text = f"\n매도 기준: +{sell_threshold}%"

            # 알람 메시지 포맷팅
            message = (
                f"{emoji} <b>매수 목표 접근 알림</b>\n"
                f"────────────\n"
                f"코인명: {coin_display}\n"
                f"시총 순위: {alert['rank']}\n\n"
                f"현재가: ${current_price_str}\n"
                f"매수목표: <b>{alert['target']} - ${target_price_str}</b>{sell_criteria_text}\n"
                f"이격도: <b>{alert['divergence']:.2f}%</b>\n"
                f"────────────\n"
                f"<tg-spoiler>* 기준 고점: ${h_value_str}</tg-spoiler>"
            )

            # Slack 전송
            slack_success = False
            if send_slack_alert:
                alert_with_first = alert.copy()
                alert_with_first['is_first'] = is_first
                slack_success = send_slack_alert(alert_with_first)

            if slack_success:
                first_marker = " (첫 자리)" if is_first else ""
                print(f"알람 전송 성공: {alert['symbol']} {alert['target']}{first_marker} (Slack)")
            else:
                print(f"알람 전송 실패: {alert['symbol']} {alert['target']}")

        except Exception as e:
            print(f"알람 전송 오류: {e}")
    
    def send_buy_execution_alert(self, execution_data: Dict):
        """매수 실행 알림 전송"""
        try:
            # 평균 매수선과 매도가 계산
            price_data = self.calculate_average_buy_and_sell_price(execution_data)
            
            # 현재가 조회
            current_price = self.get_current_price(execution_data['symbol'])
            
            # 가격 포맷팅 (H값 기반)
            h_value = execution_data.get('h_value', 0)
            current_price_str = f"${self.format_price(current_price, h_value)}" if current_price else "조회실패"
            target_price_str = self.format_price(execution_data['target_price'], h_value)
            candle_low_str = self.format_price(execution_data['candle_low'], h_value)
            avg_buy_price_str = self.format_price(price_data['avg_buy_price'], h_value)
            sell_price_str = self.format_price(price_data['sell_price'], h_value)
            h_value_str = self.format_price(h_value, h_value)
            
            # 매수 실행 메시지 포맷팅 (새로운 형식)
            message = (
                f"⚡ <b>매수 실행 알림</b>\n"
                f"────────────\n"
                f"코인명: {execution_data['name']} ({execution_data['symbol']})\n"
                f"시총 순위: {execution_data['rank']}\n\n"
                f"매수 목표: {execution_data['target']} — ${target_price_str}\n"
                f"5분봉 저가: ${candle_low_str}\n\n"
                f"현재가: {current_price_str}\n"
                f"평균매수가: ${avg_buy_price_str}\n"
                f"예상 매도가: ${sell_price_str} (+{price_data['sell_threshold']:.1f}%)\n"
                f"────────────\n"
                f"<tg-spoiler>* 기준 고점: ${h_value_str}</tg-spoiler>"
            )
            
            # Slack 전송
            slack_success = False
            if send_slack_buy_execution_alert:
                slack_success = send_slack_buy_execution_alert(execution_data, price_data, current_price)

            if slack_success:
                # 매수 실행 이력 업데이트
                today = datetime.now().strftime("%Y-%m-%d")
                symbol = execution_data['symbol']
                target = execution_data['target']

                if symbol not in self.alert_history:
                    self.alert_history[symbol] = {}
                if not isinstance(self.alert_history[symbol], dict):
                    self.alert_history[symbol] = {}

                execution_key = f"{target}_EXECUTED"
                self.alert_history[symbol][execution_key] = today
                self.save_alert_history()
                print(f"매수 실행 알림 전송 완료: {symbol} {target} (Slack)")
            else:
                print(f"매수 실행 알림 전송 실패: {execution_data['symbol']} {execution_data['target']}")
                
        except Exception as e:
            print(f"매수 실행 알림 전송 실패: {e}")
    
    def run_monitoring_cycle(self):
        """5분 간격 모니터링 사이클"""
        if not self.monitoring_data:
            print("모니터링 데이터가 없습니다.")
            return
        
        print(f"[{datetime.now()}] 모니터링 사이클 시작...")
        
        for coin_data in self.monitoring_data:
            try:
                symbol = coin_data['symbol']
                # 실시간 가격 조회
                current_price = self.get_current_price(symbol)
                if current_price is None:
                    continue
                
                # 알람 조건 확인 (접근 알림)
                alerts = self.check_alert_condition(coin_data, current_price)

                # 알람 전송 (is_first 포함)
                for alert_data, is_first in alerts:
                    self.send_alert(alert_data, is_first)
                
                # 매수 실행 감지 (30분봉 저가 기준)
                execution_data = self.check_buy_execution(coin_data)
                if execution_data:
                    # 중복 실행 알림 방지
                    today = datetime.now().strftime("%Y-%m-%d")
                    symbol = execution_data['symbol']
                    target = execution_data['target']
                    execution_key = f"{target}_EXECUTED"
                    
                    if (symbol not in self.alert_history or 
                        not isinstance(self.alert_history[symbol], dict) or
                        execution_key not in self.alert_history[symbol] or
                        self.alert_history[symbol][execution_key] != today):
                        
                        self.send_buy_execution_alert(execution_data)
                
                # API 제한 방지
                time.sleep(0.1)
                
            except Exception as e:
                print(f"{symbol} 모니터링 오류: {e}")
        
        print(f"[{datetime.now()}] 모니터링 사이클 완료")
    
    def load_existing_analysis_file(self):
        """기존 ANALYSIS 파일을 찾아서 로드 (파일 갱신 없이)"""
        try:
            output_dir = self.omg_dir / "output"
            analysis_files = list(output_dir.glob("coin_analysis_*.xlsx"))
            if not analysis_files:
                print("기존 ANALYSIS 파일을 찾을 수 없습니다.")
                return False

            # 가장 최신 파일 선택
            self.analysis_file = max(analysis_files, key=os.path.getctime)
            print(f"기존 ANALYSIS 파일 로드: {self.analysis_file.name}")

            # ANALYSIS 파일에서 모니터링 데이터 로드
            self.load_monitoring_data()
            return True

        except Exception as e:
            print(f"기존 ANALYSIS 파일 로드 실패: {e}")
            return False

    def start_monitoring(self):
        """모니터링 시작"""
        print("\n" + "=" * 60)
        print("암호화폐 실시간 모니터링 시스템 시작")
        print("=" * 60)
        print("[WARNING] 00:00 일일 업데이트는 daily_update.py에서 별도 실행됨")
        print("=" * 60)

        # 스케줄 설정 (5분 간격 모니터링만)
        schedule.every(5).minutes.do(self.run_monitoring_cycle)

        # 매일 00:05에 ANALYSIS 파일 재로드 (daily_update.py가 00:00에 생성한 파일 읽기)
        schedule.every().day.at("00:05").do(self.reload_analysis_data)

        # 초기 실행: 기존 파일 로드만 (갱신하지 않음)
        print("\n[INFO] 기존 데이터 로드 중...")
        if self.load_existing_analysis_file():
            print("[OK] 기존 데이터 로드 완료")
            print(f"[INFO] 모니터링 중인 코인: {len(self.monitoring_data)}개")
        else:
            print("[ERROR] 기존 데이터 로드 실패")
            print("[WARNING] 먼저 daily_update.py를 실행하여 분석 파일을 생성하세요.")
            return

        print("\n" + "=" * 60)
        print("[START] 5분 간격 실시간 모니터링 시작")
        print("[INFO] 매일 00:05에 데이터 자동 재로드")
        print("[INFO] Ctrl+C로 중단")
        print("=" * 60 + "\n")

        # 메인 루프
        try:
            while True:
                schedule.run_pending()
                sys.stdout.flush()
                time.sleep(60)  # 1분마다 스케줄 확인
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("[STOP] 모니터링 중단됨")
            print("=" * 60)
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"\n[ERROR] 모니터링 오류: {e}")
            print(error_msg)
            self._log_crash(str(e), error_msg)

    def _log_crash(self, error: str, traceback_str: str):
        """크래시 로그를 파일에 기록"""
        log_dir = self.omg_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "omg_monitor_error.log"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[CRASH] {ts}\n")
            f.write(f"Error: {error}\n")
            f.write(traceback_str)
            f.write(f"{'='*60}\n")

def main():
    monitor = CryptoRealtimeMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
