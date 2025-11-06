#!/usr/bin/env python3
"""
Test script to verify data loading logic
Run: python3 test_load_data.py
"""

import os
import sys
import pandas as pd
import glob

def test_load_trades():
    """ทดสอบการโหลดข้อมูล test mode"""
    print("=" * 60)
    print("Testing Data Loading Logic")
    print("=" * 60)

    # Set mode
    MODE = "test"
    all_dfs = []

    # V1.4: ลองอ่านจาก test_results/ (Easy Backtester)
    test_results_dir = "test_results"
    print(f"\n1. Checking directory: {test_results_dir}")
    print(f"   Directory exists: {os.path.exists(test_results_dir)}")

    if os.path.exists(test_results_dir):
        # หาไฟล์ v1.4_*.csv
        v14_files = glob.glob(f"{test_results_dir}/v1.4_*.csv")
        print(f"\n2. Searching for pattern: {test_results_dir}/v1.4_*.csv")
        print(f"   Files found: {len(v14_files)}")

        for filepath in v14_files:
            print(f"\n3. Processing file: {filepath}")
            try:
                df = pd.read_csv(filepath)
                print(f"   ✓ Loaded successfully")
                print(f"   ✓ Rows: {len(df)}")
                print(f"   ✓ Columns: {df.columns.tolist()}")

                if not df.empty:
                    # ดึงชื่อคู่เงินจากชื่อไฟล์
                    filename = os.path.basename(filepath)
                    pair = filename.replace("v1.4_", "").replace("_1m_30d.csv", "")

                    print(f"\n4. Checking pair column:")
                    if 'pair' not in df.columns:
                        df['pair'] = pair
                        print(f"   ✓ Added pair column: '{pair}'")
                    else:
                        print(f"   ✓ Pair column exists (will not overwrite)")
                        print(f"   ✓ Unique pairs: {df['pair'].unique().tolist()}")

                    all_dfs.append(df)
            except Exception as e:
                print(f"   ✗ Error: {e}")
                continue

    # รวมทุกไฟล์
    if all_dfs:
        df = pd.concat(all_dfs, ignore_index=True)

        print("\n" + "=" * 60)
        print("✅ SUCCESS - Data Loaded Successfully!")
        print("=" * 60)
        print(f"Total rows: {len(df)}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"\nUnique pairs: {df['pair'].unique().tolist()}")
        print(f"Pair counts:")
        print(df['pair'].value_counts().to_string())

        # Calculate basic stats
        print(f"\n📊 Basic Statistics:")
        print(f"Win rate: {(df['result'] == 'win').sum() / len(df) * 100:.2f}%")
        print(f"Total profit: ${df['profit'].sum():.2f}")
        print(f"Final capital: ${df['capital'].iloc[-1]:.2f}")

        return df, "📊 BACKTESTING (V1.4)"
    else:
        print("\n" + "=" * 60)
        print("❌ FAIL - No Data Loaded")
        print("=" * 60)
        return pd.DataFrame(), "⚠️ NO TEST DATA"

if __name__ == "__main__":
    df, status = test_load_trades()
    print(f"\nStatus: {status}")
    print(f"DataFrame shape: {df.shape}")
