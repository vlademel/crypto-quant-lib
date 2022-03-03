DROP VIEW dbo.v_active_tickers;
GO

CREATE OR REPLACE VIEW dbo.v_active_tickers
AS SELECT DISTINCT(dp.ticker),
		  cg.id AS cg_id
FROM raw.coin_daily_pricing AS dp
LEFT JOIN (SELECT DISTINCT id, symbol 
		   FROM raw.coin_market_detail) AS cg
	ON cg.symbol = dp.ticker;
GO

GRANT USAGE ON SCHEMA dbo, raw TO admin;
GRANT SELECT ON ALL TABLES IN SCHEMA dbo TO admin;
GO
