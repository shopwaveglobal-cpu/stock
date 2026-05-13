#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to capture crypto monitor errors"""
import sys
import traceback

print("=" * 60)
print("Testing crypto_realtime_monitor.py import and execution")
print("=" * 60)
print()

try:
    print("Step 1: Attempting to import crypto_realtime_monitor...")
    import crypto_realtime_monitor
    print("[OK] Import successful")
    print()

    print("Step 2: Creating CryptoRealtimeMonitor instance...")
    monitor = crypto_realtime_monitor.CryptoRealtimeMonitor()
    print("[OK] Instance created successfully")
    print()

    print("Step 3: Checking omg_dir...")
    print(f"  omg_dir = {monitor.omg_dir}")
    print(f"  omg_dir exists = {monitor.omg_dir.exists()}")
    print()

    print("Step 4: Checking for analysis file...")
    output_dir = monitor.omg_dir / "output"
    print(f"  output_dir = {output_dir}")
    print(f"  output_dir exists = {output_dir.exists()}")

    if output_dir.exists():
        analysis_files = list(output_dir.glob("coin_analysis_*.xlsx"))
        print(f"  Found {len(analysis_files)} analysis files")
        if analysis_files:
            print(f"  Latest: {analysis_files[0].name}")
    print()

    print("Step 5: Loading existing analysis file...")
    result = monitor.load_existing_analysis_file()
    print(f"  Load result: {result}")
    print()

    if result:
        print("Step 6: Checking monitoring data...")
        print(f"  Loaded {len(monitor.monitoring_data)} coins")
        print()

        print("=" * 60)
        print("All checks passed! Monitor is ready to run.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("[WARNING] Analysis file load failed!")
        print("=" * 60)

except Exception as e:
    print()
    print("=" * 60)
    print("[ERROR] ERROR OCCURRED!")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    print("Full traceback:")
    print(traceback.format_exc())
    print("=" * 60)
    sys.exit(1)
