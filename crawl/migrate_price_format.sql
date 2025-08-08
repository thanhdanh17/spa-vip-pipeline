-- Script để migrate price format từ NUMERIC sang TEXT có dấu phẩy
-- Chạy script này trong Supabase SQL Editor

-- 1. Backup tables trước khi migrate
CREATE TABLE "FPT_Stock_backup" AS SELECT * FROM "FPT_Stock";
CREATE TABLE "GAS_Stock_backup" AS SELECT * FROM "GAS_Stock";
CREATE TABLE "VCB_Stock_backup" AS SELECT * FROM "VCB_Stock";
CREATE TABLE "IMP_Stock_backup" AS SELECT * FROM "IMP_Stock";

-- 2. Thêm columns mới với kiểu TEXT
ALTER TABLE "FPT_Stock" ADD COLUMN open_price_new TEXT;
ALTER TABLE "FPT_Stock" ADD COLUMN high_price_new TEXT;
ALTER TABLE "FPT_Stock" ADD COLUMN low_price_new TEXT;
ALTER TABLE "FPT_Stock" ADD COLUMN close_price_new TEXT;

ALTER TABLE "GAS_Stock" ADD COLUMN open_price_new TEXT;
ALTER TABLE "GAS_Stock" ADD COLUMN high_price_new TEXT;
ALTER TABLE "GAS_Stock" ADD COLUMN low_price_new TEXT;
ALTER TABLE "GAS_Stock" ADD COLUMN close_price_new TEXT;

ALTER TABLE "VCB_Stock" ADD COLUMN open_price_new TEXT;
ALTER TABLE "VCB_Stock" ADD COLUMN high_price_new TEXT;
ALTER TABLE "VCB_Stock" ADD COLUMN low_price_new TEXT;
ALTER TABLE "VCB_Stock" ADD COLUMN close_price_new TEXT;

ALTER TABLE "IMP_Stock" ADD COLUMN open_price_new TEXT;
ALTER TABLE "IMP_Stock" ADD COLUMN high_price_new TEXT;
ALTER TABLE "IMP_Stock" ADD COLUMN low_price_new TEXT;
ALTER TABLE "IMP_Stock" ADD COLUMN close_price_new TEXT;

-- 3. Convert dữ liệu cũ sang format mới (có dấu phẩy)
-- FPT_Stock
UPDATE "FPT_Stock" SET 
    open_price_new = CASE 
        WHEN open_price = 0 OR open_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(open_price, 'FM999,999,999')
    END,
    high_price_new = CASE 
        WHEN high_price = 0 OR high_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(high_price, 'FM999,999,999')
    END,
    low_price_new = CASE 
        WHEN low_price = 0 OR low_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(low_price, 'FM999,999,999')
    END,
    close_price_new = CASE 
        WHEN close_price = 0 OR close_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(close_price, 'FM999,999,999')
    END;

-- GAS_Stock
UPDATE "GAS_Stock" SET 
    open_price_new = CASE 
        WHEN open_price = 0 OR open_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(open_price, 'FM999,999,999')
    END,
    high_price_new = CASE 
        WHEN high_price = 0 OR high_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(high_price, 'FM999,999,999')
    END,
    low_price_new = CASE 
        WHEN low_price = 0 OR low_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(low_price, 'FM999,999,999')
    END,
    close_price_new = CASE 
        WHEN close_price = 0 OR close_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(close_price, 'FM999,999,999')
    END;

-- VCB_Stock
UPDATE "VCB_Stock" SET 
    open_price_new = CASE 
        WHEN open_price = 0 OR open_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(open_price, 'FM999,999,999')
    END,
    high_price_new = CASE 
        WHEN high_price = 0 OR high_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(high_price, 'FM999,999,999')
    END,
    low_price_new = CASE 
        WHEN low_price = 0 OR low_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(low_price, 'FM999,999,999')
    END,
    close_price_new = CASE 
        WHEN close_price = 0 OR close_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(close_price, 'FM999,999,999')
    END;

-- IMP_Stock
UPDATE "IMP_Stock" SET 
    open_price_new = CASE 
        WHEN open_price = 0 OR open_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(open_price, 'FM999,999,999')
    END,
    high_price_new = CASE 
        WHEN high_price = 0 OR high_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(high_price, 'FM999,999,999')
    END,
    low_price_new = CASE 
        WHEN low_price = 0 OR low_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(low_price, 'FM999,999,999')
    END,
    close_price_new = CASE 
        WHEN close_price = 0 OR close_price IS NULL THEN 'EMPTY'
        ELSE TO_CHAR(close_price, 'FM999,999,999')
    END;

-- 4. Xóa columns cũ và rename columns mới
-- FPT_Stock
ALTER TABLE "FPT_Stock" DROP COLUMN open_price;
ALTER TABLE "FPT_Stock" DROP COLUMN high_price;
ALTER TABLE "FPT_Stock" DROP COLUMN low_price;
ALTER TABLE "FPT_Stock" DROP COLUMN close_price;

ALTER TABLE "FPT_Stock" RENAME COLUMN open_price_new TO open_price;
ALTER TABLE "FPT_Stock" RENAME COLUMN high_price_new TO high_price;
ALTER TABLE "FPT_Stock" RENAME COLUMN low_price_new TO low_price;
ALTER TABLE "FPT_Stock" RENAME COLUMN close_price_new TO close_price;

-- GAS_Stock
ALTER TABLE "GAS_Stock" DROP COLUMN open_price;
ALTER TABLE "GAS_Stock" DROP COLUMN high_price;
ALTER TABLE "GAS_Stock" DROP COLUMN low_price;
ALTER TABLE "GAS_Stock" DROP COLUMN close_price;

ALTER TABLE "GAS_Stock" RENAME COLUMN open_price_new TO open_price;
ALTER TABLE "GAS_Stock" RENAME COLUMN high_price_new TO high_price;
ALTER TABLE "GAS_Stock" RENAME COLUMN low_price_new TO low_price;
ALTER TABLE "GAS_Stock" RENAME COLUMN close_price_new TO close_price;

-- VCB_Stock
ALTER TABLE "VCB_Stock" DROP COLUMN open_price;
ALTER TABLE "VCB_Stock" DROP COLUMN high_price;
ALTER TABLE "VCB_Stock" DROP COLUMN low_price;
ALTER TABLE "VCB_Stock" DROP COLUMN close_price;

ALTER TABLE "VCB_Stock" RENAME COLUMN open_price_new TO open_price;
ALTER TABLE "VCB_Stock" RENAME COLUMN high_price_new TO high_price;
ALTER TABLE "VCB_Stock" RENAME COLUMN low_price_new TO low_price;
ALTER TABLE "VCB_Stock" RENAME COLUMN close_price_new TO close_price;

-- IMP_Stock
ALTER TABLE "IMP_Stock" DROP COLUMN open_price;
ALTER TABLE "IMP_Stock" DROP COLUMN high_price;
ALTER TABLE "IMP_Stock" DROP COLUMN low_price;
ALTER TABLE "IMP_Stock" DROP COLUMN close_price;

ALTER TABLE "IMP_Stock" RENAME COLUMN open_price_new TO open_price;
ALTER TABLE "IMP_Stock" RENAME COLUMN high_price_new TO high_price;
ALTER TABLE "IMP_Stock" RENAME COLUMN low_price_new TO low_price;
ALTER TABLE "IMP_Stock" RENAME COLUMN close_price_new TO close_price;

-- 5. Verify kết quả
SELECT 'FPT_Stock' as table_name, date, open_price, close_price FROM "FPT_Stock" LIMIT 5
UNION ALL
SELECT 'GAS_Stock' as table_name, date, open_price, close_price FROM "GAS_Stock" LIMIT 5
UNION ALL
SELECT 'VCB_Stock' as table_name, date, open_price, close_price FROM "VCB_Stock" LIMIT 5
UNION ALL
SELECT 'IMP_Stock' as table_name, date, open_price, close_price FROM "IMP_Stock" LIMIT 5;
