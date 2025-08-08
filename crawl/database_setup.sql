-- SQL Script để tạo các tables cần thiết cho hệ thống crawl
-- Chạy trong Supabase SQL Editor

-- 1. Table cho tin tức chung (không theo công ty cụ thể)
CREATE TABLE IF NOT EXISTS public.General_News (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    date date NOT NULL,
    link text NOT NULL UNIQUE,
    ai_summary text,
    sentiment text,
    industry text,
    CONSTRAINT General_News_pkey PRIMARY KEY (id)
);

-- 2. Tables cho tin tức theo từng công ty
CREATE TABLE IF NOT EXISTS public.FPT_News (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    date date NOT NULL,
    link text NOT NULL UNIQUE,
    ai_summary text,
    sentiment text,
    CONSTRAINT FPT_News_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.GAS_News (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    date date NOT NULL,
    link text NOT NULL UNIQUE,
    ai_summary text,
    sentiment text,
    CONSTRAINT GAS_News_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.IMP_News (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    date date NOT NULL,
    link text NOT NULL UNIQUE,
    ai_summary text,
    sentiment text,
    CONSTRAINT IMP_News_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.VCB_News (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    date date NOT NULL,
    link text NOT NULL UNIQUE,
    ai_summary text,
    sentiment text,
    CONSTRAINT VCB_News_pkey PRIMARY KEY (id)
);

-- 3. Tables cho giá cổ phiếu
CREATE TABLE IF NOT EXISTS public.FPT_Stock (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    date date NOT NULL DEFAULT now(),
    open_price text NOT NULL,
    high_price text NOT NULL,
    low_price text NOT NULL,
    close_price text NOT NULL,
    change text NOT NULL,
    change_pct text NOT NULL,
    volume text NOT NULL,
    Positive text,
    Neutral text,
    Negative text,
    predict_price text,
    CONSTRAINT FPT_Stock_pkey PRIMARY KEY (id, date)
);

CREATE TABLE IF NOT EXISTS public.GAS_Stock (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    date date NOT NULL DEFAULT now(),
    open_price text NOT NULL,
    high_price text NOT NULL,
    low_price text NOT NULL,
    close_price text NOT NULL,
    change text NOT NULL,
    change_pct text NOT NULL,
    volume text NOT NULL,
    Positive text,
    Neutral text,
    Negative text,
    predict_price text,
    CONSTRAINT GAS_Stock_pkey PRIMARY KEY (id, date)
);

CREATE TABLE IF NOT EXISTS public.IMP_Stock (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    date date NOT NULL DEFAULT now(),
    open_price text NOT NULL,
    high_price text NOT NULL,
    low_price text NOT NULL,
    close_price text NOT NULL,
    change text NOT NULL,
    change_pct text NOT NULL,
    volume text NOT NULL,
    Positive text,
    Neutral text,
    Negative text,
    predict_price text,
    CONSTRAINT IMP_Stock_pkey PRIMARY KEY (id, date)
);

CREATE TABLE IF NOT EXISTS public.VCB_Stock (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    date date NOT NULL DEFAULT now(),
    open_price text NOT NULL,
    high_price text NOT NULL,
    low_price text NOT NULL,
    close_price text NOT NULL,
    change text NOT NULL,
    change_pct text NOT NULL,
    volume text NOT NULL,
    Positive text,
    Neutral text,
    Negative text,
    predict_price text,
    CONSTRAINT VCB_Stock_pkey PRIMARY KEY (id, date)
);

-- 4. Tạo indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_general_news_date ON public.General_News(date DESC);
CREATE INDEX IF NOT EXISTS idx_general_news_link ON public.General_News(link);

CREATE INDEX IF NOT EXISTS idx_fpt_news_date ON public.FPT_News(date DESC);
CREATE INDEX IF NOT EXISTS idx_fpt_news_link ON public.FPT_News(link);

CREATE INDEX IF NOT EXISTS idx_gas_news_date ON public.GAS_News(date DESC);
CREATE INDEX IF NOT EXISTS idx_gas_news_link ON public.GAS_News(link);

CREATE INDEX IF NOT EXISTS idx_imp_news_date ON public.IMP_News(date DESC);
CREATE INDEX IF NOT EXISTS idx_imp_news_link ON public.IMP_News(link);

CREATE INDEX IF NOT EXISTS idx_vcb_news_date ON public.VCB_News(date DESC);
CREATE INDEX IF NOT EXISTS idx_vcb_news_link ON public.VCB_News(link);

CREATE INDEX IF NOT EXISTS idx_fpt_stock_date ON public.FPT_Stock(date DESC);
CREATE INDEX IF NOT EXISTS idx_gas_stock_date ON public.GAS_Stock(date DESC);
CREATE INDEX IF NOT EXISTS idx_imp_stock_date ON public.IMP_Stock(date DESC);
CREATE INDEX IF NOT EXISTS idx_vcb_stock_date ON public.VCB_Stock(date DESC);

-- 5. Thêm comments cho các tables
COMMENT ON TABLE public.General_News IS 'Bảng lưu tin tức tổng quát không theo công ty cụ thể';
COMMENT ON TABLE public.FPT_News IS 'Bảng lưu tin tức công ty FPT';
COMMENT ON TABLE public.GAS_News IS 'Bảng lưu tin tức công ty GAS';
COMMENT ON TABLE public.IMP_News IS 'Bảng lưu tin tức công ty IMP';
COMMENT ON TABLE public.VCB_News IS 'Bảng lưu tin tức công ty VCB';
COMMENT ON TABLE public.FPT_Stock IS 'Bảng lưu lịch sử giá cổ phiếu FPT';
COMMENT ON TABLE public.GAS_Stock IS 'Bảng lưu lịch sử giá cổ phiếu GAS';
COMMENT ON TABLE public.IMP_Stock IS 'Bảng lưu lịch sử giá cổ phiếu IMP';
COMMENT ON TABLE public.VCB_Stock IS 'Bảng lưu lịch sử giá cổ phiếu VCB';
