#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để kiểm tra chi tiết 15 ngày lịch sử được sử dụng cho timeseries prediction
Located in sentiment folder for better organization
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import database manager
from database import SupabaseManager

def check_15_days_history_for_stock(stock_code: str):
    """
    Kiểm tra 15 ngày lịch sử của một cổ phiếu
    
    Args:
        stock_code: Mã cổ phiếu (FPT, GAS, IMP, VCB)
    """
    print(f"\n{'='*60}")
    print(f"📊 15 NGÀY LỊCH SỬ CHO {stock_code}")
    print(f"{'='*60}")
    
    try:
        # Initialize database
        db_manager = SupabaseManager()
        table_name = f"{stock_code}_Stock"
        
        # Query exactly like timeseries prediction does
        response = (
            db_manager.client.table(table_name)
            .select("*")
            .neq("close_price", "")
            .not_.is_("close_price", "null")
            .order("date", desc=True)
            .limit(15)  # Chính xác 15 ngày như trong timeseries
            .execute()
        )
        
        if not response.data:
            print(f"❌ Không có dữ liệu cho {stock_code}")
            return None
        
        # Process data
        df = pd.DataFrame(response.data)
        df["Ngày"] = pd.to_datetime(df["date"])
        df["Giá đóng cửa"] = pd.to_numeric(
            df["close_price"].astype(str).str.replace(",", ""),
            errors="coerce",
        )
        
        # Process sentiment columns
        for col in ["Positive", "Neutral", "Negative"]:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = (
                    pd.to_numeric(df[col].replace("", "0"), errors="coerce")
                    .fillna(0)
                )
        
        # Sort by date (oldest first for display)
        df = df.sort_values("Ngày").reset_index(drop=True)
        
        print(f"📈 Tổng số ngày có dữ liệu: {len(df)}")
        print(f"📅 Từ ngày: {df['Ngày'].iloc[0].strftime('%Y-%m-%d')}")
        print(f"📅 Đến ngày: {df['Ngày'].iloc[-1].strftime('%Y-%m-%d')}")
        print(f"💰 Giá cuối: {df['Giá đóng cửa'].iloc[-1]:,.0f} VND")
        
        print(f"\n📋 CHI TIẾT 15 NGÀY:")
        print("-" * 90)
        print(f"{'STT':<4} {'Ngày':<12} {'Giá đóng cửa':<15} {'Positive':<10} {'Neutral':<10} {'Negative':<10}")
        print("-" * 90)
        
        for idx, row in df.iterrows():
            stt = idx + 1
            ngay = row['Ngày'].strftime('%Y-%m-%d')
            gia = f"{row['Giá đóng cửa']:,.0f}"
            pos = f"{row['Positive']:.0f}"
            neu = f"{row['Neutral']:.0f}"
            neg = f"{row['Negative']:.0f}"
            
            print(f"{stt:<4} {ngay:<12} {gia:<15} {pos:<10} {neu:<10} {neg:<10}")
        
        print("-" * 90)
        
        # Statistics
        avg_price = df['Giá đóng cửa'].mean()
        min_price = df['Giá đóng cửa'].min()
        max_price = df['Giá đóng cửa'].max()
        
        print(f"\n📊 THỐNG KÊ:")
        print(f"💰 Giá trung bình: {avg_price:,.0f} VND")
        print(f"📉 Giá thấp nhất: {min_price:,.0f} VND")
        print(f"📈 Giá cao nhất: {max_price:,.0f} VND")
        print(f"📊 Tổng Positive: {df['Positive'].sum():.0f}")
        print(f"📊 Tổng Neutral: {df['Neutral'].sum():.0f}")
        print(f"📊 Tổng Negative: {df['Negative'].sum():.0f}")
        
        return df
        
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra {stock_code}: {e}")
        return None

def main():
    """Main function"""
    print("🚀 KIỂM TRA 15 NGÀY LỊCH SỬ CHO TIMESERIES PREDICTION")
    print("="*80)
    print(f"⏰ Thời gian kiểm tra: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📍 Located in sentiment folder")
    
    # Available stocks
    stocks = ["FPT", "GAS", "IMP", "VCB"]
    
    all_data = {}
    
    for stock in stocks:
        df = check_15_days_history_for_stock(stock)
        if df is not None:
            all_data[stock] = df
    
    # Summary comparison
    if all_data:
        print(f"\n{'='*80}")
        print("📊 TỔNG KẾT SO SÁNH")
        print("="*80)
        print(f"{'Cổ phiếu':<10} {'Số ngày':<10} {'Giá cuối':<15} {'Ngày đầu':<12} {'Ngày cuối':<12}")
        print("-" * 80)
        
        for stock, df in all_data.items():
            so_ngay = len(df)
            gia_cuoi = f"{df['Giá đóng cửa'].iloc[-1]:,.0f}"
            ngay_dau = df['Ngày'].iloc[0].strftime('%Y-%m-%d')
            ngay_cuoi = df['Ngày'].iloc[-1].strftime('%Y-%m-%d')
            
            print(f"{stock:<10} {so_ngay:<10} {gia_cuoi:<15} {ngay_dau:<12} {ngay_cuoi:<12}")
    
    print("\n✅ Hoàn thành kiểm tra!")
    print("💡 Đây chính là 15 ngày lịch sử được sử dụng để dự báo timeseries")
    print("📁 Script location: sentiment/check_15_days_history.py")

if __name__ == "__main__":
    main()
