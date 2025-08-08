import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# ====================== KẾT NỐI DB ======================
def get_engine():
    user = "postgres"
    password = "D%40nh12345"  # encode @ thành %40
    host = "db.baenxyqklayjtlbmubxe.supabase.co"
    port = 5432
    database = "postgres"

    return create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    )

def get_connection():
    return psycopg2.connect(
        host="db.baenxyqklayjtlbmubxe.supabase.co",
        port=5432,
        database="postgres",
        user="postgres",
        password="D@nh12345",
        sslmode="require"
    )

# ====================== LẤY DỮ LIỆU TỪ DB ======================
def get_news_sentiment(engine, news_table):
    query = f'SELECT "date", "sentiment" FROM "{news_table}" WHERE "sentiment" IS NOT NULL;'
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_date(df["date"]).dt.date

    df_counts = df.groupby(["date", "sentiment"]).size().reset_index(name="count")
    df_pivot = df_counts.pivot(index="date", columns="sentiment", values="count").fillna(0)

    for col in ["Positive", "Neutral", "Negative"]:
        if col not in df_pivot.columns:
            df_pivot[col] = 0

    df_pivot = df_pivot.reset_index()
    return df_pivot[["date", "Positive", "Neutral", "Negative"]]

def get_news_sentiment_by_dates(engine, news_table, dates):
    # dates là set hoặc list các ngày dạng 'YYYY-MM-DD'
    if not dates:
        return pd.DataFrame(columns=["date", "Positive", "Neutral", "Negative"])
    date_list = "', '".join(dates)
    query = f'''
        SELECT "date", "sentiment"
        FROM "{news_table}"
        WHERE "sentiment" IS NOT NULL AND "date" IN ('{date_list}');
    '''
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df_counts = df.groupby(["date", "sentiment"]).size().reset_index(name="count")
    df_pivot = df_counts.pivot(index="date", columns="sentiment", values="count").fillna(0)
    for col in ["Positive", "Neutral", "Negative"]:
        if col not in df_pivot.columns:
            df_pivot[col] = 0
    df_pivot = df_pivot.reset_index()
    return df_pivot[["date", "Positive", "Neutral", "Negative"]]

def get_stock_data(engine, stock_table):
    query = f'SELECT "date" FROM "{stock_table}" ORDER BY "date";'
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

def get_stock_data_by_dates(engine, stock_table, dates):
    if not dates:
        return pd.DataFrame(columns=["date"])
    date_list = "', '".join(dates)
    query = f'SELECT "date" FROM "{stock_table}" WHERE "date" IN (\'{date_list}\') ORDER BY "date";'
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

# ====================== XỬ LÝ MERGE & CỘNG DỒN ======================
def merge_sentiment_with_stock(news_df, stock_df):
    merged = stock_df.copy()
    merged["Positive"] = 0
    merged["Neutral"] = 0
    merged["Negative"] = 0

    news_dict = news_df.set_index("date").to_dict(orient="index")

    prev_day = None
    buffer_pos, buffer_neu, buffer_neg = 0, 0, 0

    for i, row in merged.iterrows():
        day = row["date"]

        # cộng dồn tất cả tin tức xảy ra **trong khoảng (prev_day, day]**
        for news_day, values in news_dict.items():
            if (prev_day is None or news_day > prev_day) and news_day <= day:
                buffer_pos += values["Positive"]
                buffer_neu += values["Neutral"]
                buffer_neg += values["Negative"]

        merged.loc[i, "Positive"] = buffer_pos
        merged.loc[i, "Neutral"] = buffer_neu
        merged.loc[i, "Negative"] = buffer_neg

        # reset sau khi gán vào ngày stock
        buffer_pos, buffer_neu, buffer_neg = 0, 0, 0
        prev_day = day

    return merged

# ====================== RESET VỀ 0 ======================
def reset_sentiment(conn, stock_table):
    cur = conn.cursor()
    sql = f"""
    UPDATE "{stock_table}"
    SET "Positive" = 0,
        "Neutral"  = 0,
        "Negative" = 0;
    """
    cur.execute(sql)
    conn.commit()
    cur.close()
    print(f"🔄 Reset tất cả sentiment về 0 cho {stock_table}")

# ====================== UPDATE DB ======================
def update_stock_table(conn, stock_table, merged_df):
    cur = conn.cursor()
    for _, row in merged_df.iterrows():
        sql = f"""
        UPDATE "{stock_table}"
        SET "Positive" = %s,
            "Neutral"  = %s,
            "Negative" = %s
        WHERE "date" = %s;
        """
        cur.execute(sql, (int(row["Positive"]), int(row["Neutral"]), int(row["Negative"]), row["date"]))
    conn.commit()
    cur.close()

def update_stock_table_by_dates(conn, stock_table, merged_df):
    cur = conn.cursor()
    for _, row in merged_df.iterrows():
        sql = f"""
        UPDATE "{stock_table}"
        SET "Positive" = %s,
            "Neutral"  = %s,
            "Negative" = %s
        WHERE "date" = %s;
        """
        cur.execute(sql, (int(row["Positive"]), int(row["Neutral"]), int(row["Negative"]), row["date"]))
    conn.commit()
    cur.close()

# ====================== MAIN ======================
def main():
    stock_codes = ["GAS", "FPT"]

    for code in stock_codes:
        print(f"\n🔄 Đang xử lý {code}...")

        engine = get_engine()
        conn = get_connection()
        print("✅ Đã kết nối DB")

        news_table = f"{code}_News"
        stock_table = f"{code}_Stock"

        try:
            news_df = get_news_sentiment(engine, news_table)
            print(f"📄 Lấy {len(news_df)} dòng tin tức từ {news_table}")

            stock_df = get_stock_data(engine, stock_table)
            print(f"📊 Lấy {len(stock_df)} dòng stock từ {stock_table}")

            merged_df = merge_sentiment_with_stock(news_df, stock_df)
            print("✅ Merge xong, reset & update DB...")

            reset_sentiment(conn, stock_table)
            update_stock_table(conn, stock_table, merged_df)
            print(f"✅ Đã update xong {code}_Stock")

        except Exception as e:
            print(f"❌ Lỗi khi xử lý {code}: {e}")

        finally:
            conn.close()
            engine.dispose()  # ✅ Đảm bảo engine được đóng

if __name__ == "__main__":
    main()