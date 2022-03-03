DROP VIEW dbo.v_simple_reversal_data
GO

CREATE OR REPLACE VIEW dbo.v_simple_reversal_data
AS SELECT dp.date,
		  dp.close,
	      dp.volume,
	      dp.ticker,
	      cci.market_cap_usd,
	      cci.reddit_average_posts_48h,
	      cci.reddit_average_comments_48h,
	      cci.reddit_subscribers,
	      cci.reddit_accounts_active_48h,
	      cci.stars,
	      cci.forks,
	      cci.subscribers,
	      cci.total_issues,
	      cci.closed_issues,
	      cci.pull_request_contributors,
	      cci.pull_requests_merged,
	      cci.alexa_rank,
	      cci.bing_matches,
	      cci.facebook_likes,
	      cci.twitter_followers
FROM raw.coin_daily_pricing dp
LEFT JOIN raw.coingecko_coin_info cci
	ON cci.symbol = dp.ticker 
	AND cci.date = dp.date


--GRANT USAGE ON SCHEMA dbo, raw TO viewer
--GRANT SELECT ON ALL TABLES IN SCHEMA dbo TO viewer;
--GO
