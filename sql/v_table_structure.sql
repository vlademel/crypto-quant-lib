DROP VIEW dbo.v_table_structure
GO

CREATE OR REPLACE VIEW dbo.v_table_structure
AS SELECT struct.schema_name,
		  struct.table_name,
		  struct.db_column,
		  (CASE WHEN struct.db_type = 'FIX'
		  		THEN tag.db_type
		  		ELSE struct.db_type
		  END) AS db_type
	FROM dbo.table_structure struct
	LEFT JOIN fix.fix_tags tag
		  ON tag.db_column = struct.db_column;
GO

GRANT USAGE ON SCHEMA dbo, raw TO viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA dbo TO viewer;
GO
