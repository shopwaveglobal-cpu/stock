#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd


S12_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S12_DIR))

import Daily_Turnover_Tracker as tracker  # noqa: E402
from Daily_Turnover_Tracker import (  # noqa: E402
    append_to_excel,
    calculate_market_cap_eok,
    parse_listed_share_counts,
    select_stock_condition,
)


class SelectionConditionTests(unittest.TestCase):
    def test_s2_1_includes_exact_boundary(self):
        self.assertEqual(select_stock_condition(50_000, 5_000, True), "S2-1")

    def test_s2_2_includes_exact_boundary(self):
        self.assertEqual(select_stock_condition(100_000, 3_000, True), "S2-2")

    def test_s2_2_has_priority_when_both_conditions_match(self):
        self.assertEqual(select_stock_condition(100_000, 5_000, True), "S2-2")

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

            append_to_excel(workbook, [(today, "005930", "A", 5_000.0)])
            append_to_excel(
                workbook,
                [
                    (today, "005930", "A", 6_000.0),
                    (today, "000660", "B", 7_000.0),
                ],
            )

            saved = pd.read_excel(workbook, sheet_name="universe", dtype={"티커": str})
            existing = saved[saved["티커"] == "005930"].iloc[0]

            self.assertEqual(len(saved), 2)
            self.assertEqual(existing["누적횟수"], 1)
            self.assertEqual(existing["거래대금(억)"], 6_000.0)

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
