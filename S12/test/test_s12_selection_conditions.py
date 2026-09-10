#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd


S12_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S12_DIR))

import Daily_Turnover_Tracker as tracker  # noqa: E402
import Trading_Signal_System as signal_system  # noqa: E402
import telegram_notifier  # noqa: E402
from Daily_Turnover_Tracker import (  # noqa: E402
    append_to_excel,
    calculate_market_cap_eok,
    parse_listed_share_counts,
    save_to_excel,
    select_stock_condition,
)


class SelectionConditionTests(unittest.TestCase):
    def test_s2_1_includes_exact_boundary(self):
        self.assertEqual(select_stock_condition(50_000, 5_000, True), "S2-1")

    def test_s2_2_includes_exact_boundary(self):
        self.assertEqual(select_stock_condition(100_000, 3_000, True), "S2-2")

    def test_reports_both_conditions_when_both_match(self):
        self.assertEqual(select_stock_condition(100_000, 5_000, True), "S2-1+S2-2")

    def test_rejects_stock_between_market_cap_tiers_below_5000_turnover(self):
        self.assertIsNone(select_stock_condition(99_999.99, 4_999.99, True))

    def test_rejects_bearish_stock_even_when_size_and_turnover_match(self):
        self.assertIsNone(select_stock_condition(150_000, 10_000, False))

    def test_rejects_missing_market_cap(self):
        self.assertIsNone(select_stock_condition(None, 10_000, True))

    def test_calculates_close_based_market_cap_in_eok(self):
        self.assertEqual(calculate_market_cap_eok(100_000_000, 50_000), 50_000)

    def test_parses_listed_share_counts_and_ignores_invalid_rows(self):
        response = {
            "list": [
                {"code": "005930", "name": "A", "listCount": "5,919,637,922"},
                {"code": "000660", "name": "B", "listCount": ""},
                {"code": "", "name": "C", "listCount": "100"},
            ]
        }

        self.assertEqual(parse_listed_share_counts(response), {"005930": 5_919_637_922})

    def test_existing_accumulation_keeps_one_row_and_no_same_day_double_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = Path(temp_dir) / "turnover_universe.xlsx"
            today = date.today()

            append_to_excel(
                workbook,
                [(today, "005930", "A", 100_000.0, 5_000.0, "S2-1+S2-2")],
            )
            append_to_excel(
                workbook,
                [
                    (today, "005930", "A", 110_000.0, 4_000.0, "S2-2"),
                    (today, "000660", "B", 60_000.0, 7_000.0, "S2-1"),
                ],
            )

            saved = pd.read_excel(workbook, sheet_name="universe", dtype={"티커": str})
            existing = saved[saved["티커"] == "005930"].iloc[0]

            self.assertEqual(len(saved), 2)
            self.assertEqual(existing["누적횟수"], 1)
            self.assertEqual(existing["거래대금(억)"], 4_000.0)
            self.assertEqual(existing["시가총액(억)"], 110_000.0)
            self.assertEqual(existing["선정조건"], "S2-2")

    def test_corrupt_existing_workbook_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = Path(temp_dir) / "turnover_universe.xlsx"
            original = b"not-an-xlsx"
            workbook.write_bytes(original)

            with self.assertRaises(Exception):
                append_to_excel(
                    workbook,
                    [(date.today(), "005930", "A", 100_000.0, 5_000.0, "S2-1+S2-2")],
                )

            self.assertEqual(workbook.read_bytes(), original)

    def test_saved_workbook_is_a_valid_zip_archive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = Path(temp_dir) / "turnover_universe.xlsx"
            append_to_excel(
                workbook,
                [(date.today(), "005930", "A", 100_000.0, 5_000.0, "S2-1+S2-2")],
            )

            with zipfile.ZipFile(workbook) as archive:
                self.assertIsNone(archive.testzip())

    def test_legacy_row_without_market_cap_can_be_saved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = Path(temp_dir) / "turnover_universe.xlsx"
            legacy = pd.DataFrame(
                [
                    {
                        "첫주도주": date.today(),
                        "최근주도주": date.today(),
                        "티커": "005930",
                        "종목명": "A",
                        "시가총액(억)": pd.NA,
                        "거래대금(억)": 5_000.0,
                        "선정조건": "기존 누적",
                        "누적횟수": 1,
                    }
                ]
            )

            save_to_excel(workbook, legacy, "2026-09-10")

            saved = pd.read_excel(workbook, sheet_name="universe", dtype={"티커": str})
            self.assertTrue(pd.isna(saved.loc[0, "시가총액(억)"]))

    def test_collection_flow_applies_both_tiers_and_rejects_non_matches(self):
        rank_response = {
            "output": [
                {"stk_cd": "000001", "stk_nm": "S2-1", "tvol_tamt": "500000"},
                {"stk_cd": "000002", "stk_nm": "S2-2", "tvol_tamt": "300000"},
                {"stk_cd": "000003", "stk_nm": "Too Small", "tvol_tamt": "400000"},
                {"stk_cd": "000004", "stk_nm": "Bearish", "tvol_tamt": "900000"},
            ]
        }
        share_counts = {
            "000001": 100_000_000,
            "000002": 200_000_000,
            "000003": 160_000_000,
            "000004": 400_000_000,
        }
        candles = {
            "000001": {"open": 49_000, "close": 50_000},
            "000002": {"open": 49_000, "close": 50_000},
            "000003": {"open": 49_000, "close": 50_000},
            "000004": {"open": 51_000, "close": 50_000},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = Path(temp_dir) / "turnover_universe.xlsx"
            with (
                patch.object(
                    tracker,
                    "fetch_rank_data",
                    side_effect=[rank_response, {"output": []}],
                ),
                patch.object(
                    tracker,
                    "fetch_listed_share_counts",
                    return_value=share_counts,
                ),
                patch.object(
                    tracker,
                    "fetch_today_candle",
                    side_effect=lambda _token, code: candles[code],
                ),
            ):
                selected_count = tracker.collect_today_data(
                    "token",
                    tracker.MIN_TURNOVER_EOK,
                    workbook,
                    filter_bullish=True,
                )

            saved = pd.read_excel(workbook, sheet_name="universe", dtype={"티커": str})

            self.assertEqual(selected_count, 2)
            self.assertEqual(set(saved["티커"]), {"000001", "000002"})
            self.assertEqual(
                saved.set_index("티커").loc["000002", "선정조건"],
                "S2-2",
            )


class SelectionConditionAlertTests(unittest.TestCase):
    def test_notification_env_switch_disables_external_messages(self):
        with patch.dict(os.environ, {"STOCK_AUTOMATION_NO_NOTIFY": "1"}):
            self.assertFalse(signal_system.notifications_enabled(False))

    def test_notifications_remain_enabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(signal_system.notifications_enabled(False))

    def test_signal_result_keeps_selection_metadata_from_universe(self):
        result = {"티커": "005930", "종목명": "삼성전자"}
        universe_row = pd.Series(
            {
                "선정조건": "S2-1+S2-2",
                "시가총액(억)": 500_000.0,
                "거래대금(억)": 8_000.0,
            }
        )

        enriched = signal_system.attach_selection_metadata(result, universe_row)

        self.assertEqual(enriched["선정조건"], "S2-1+S2-2")
        self.assertEqual(enriched["시가총액(억)"], 500_000.0)
        self.assertEqual(enriched["거래대금(억)"], 8_000.0)

    def test_realtime_telegram_message_displays_both_condition_label(self):
        with patch.object(telegram_notifier, "send_telegram_message", return_value=True) as send:
            telegram_notifier.send_realtime_alert(
                alert_type="1차 매수선 1% 인접",
                stock_name="삼성전자",
                ticker="005930",
                current_price=80_000,
                target_price=79_500,
                distance_pct=0.63,
                recipients=["me"],
                system_label="S12",
                selection_condition="S2-1+S2-2",
            )

        message = send.call_args.args[0]
        self.assertIn("선정조건: S2-1·S2-2 모두", message)


@unittest.skipUnless(os.name == "nt", "Windows batch behavior test")
class S1WrapperTests(unittest.TestCase):
    def test_s12_wrapper_delegates_to_real_s1_batch_and_preserves_exit_code(self):
        source_wrapper = S12_DIR / "RUN_S1_DAILY.bat"

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fake_s12 = root / "S12"
            fake_s1 = root / "S1"
            fake_s12.mkdir()
            fake_s1.mkdir()
            shutil.copy2(source_wrapper, fake_s12 / source_wrapper.name)

            marker = root / "called.txt"
            (fake_s1 / "RUN_S1_DAILY.bat").write_text(
                f'@echo off\r\necho called>"{marker}"\r\nexit /b 7\r\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                ["cmd.exe", "/d", "/c", str(fake_s12 / source_wrapper.name)],
                cwd=fake_s12,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertTrue(marker.exists(), result.stdout + result.stderr)
            self.assertEqual(result.returncode, 7)


if __name__ == "__main__":
    unittest.main()
