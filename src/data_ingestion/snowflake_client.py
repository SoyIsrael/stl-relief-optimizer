"""Snowflake database client for reading and writing project data."""
import os
from contextlib import contextmanager
from typing import Generator

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class SnowflakeClient:
    """Client for Snowflake database operations."""

    def __init__(
        self,
        account: str | None = None,
        user: str | None = None,
        password: str | None = None,
        warehouse: str | None = None,
        database: str | None = None,
        schema: str | None = None,
    ):
        """
        Initialize Snowflake client with credentials.

        Credentials can be passed directly or loaded from environment variables.
        """
        self.account = account or os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = user or os.getenv("SNOWFLAKE_USER")
        self.password = password or os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")

        self._validate_credentials()

    def _validate_credentials(self) -> None:
        """Ensure all required credentials are present."""
        missing = []
        for attr in ["account", "user", "password", "warehouse", "database", "schema"]:
            if not getattr(self, attr):
                missing.append(attr.upper())
        if missing:
            raise ValueError(f"Missing Snowflake credentials: {', '.join(missing)}")

    @contextmanager
    def connection(self) -> Generator:
        """Context manager for Snowflake connections."""
        import snowflake.connector

        conn = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema,
        )
        try:
            yield conn
        finally:
            conn.close()

    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read a full table into a DataFrame."""
        with self.connection() as conn:
            query = f"SELECT * FROM {table_name}"
            return pd.read_sql(query, conn)

    def write_table(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "replace",
    ) -> None:
        """
        Write a DataFrame to Snowflake.

        Args:
            df: DataFrame to write
            table_name: Target table name
            if_exists: 'replace' or 'append'
        """
        from snowflake.connector.pandas_tools import write_pandas

        with self.connection() as conn:
            if if_exists == "replace":
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                cursor.close()

            write_pandas(
                conn,
                df,
                table_name=table_name.upper(),
                auto_create_table=True,
            )

    def execute(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results."""
        with self.connection() as conn:
            return pd.read_sql(query, conn)

    def get_candidate_sites(self, table_name: str = "CANDIDATE_SITES") -> pd.DataFrame:
        """Fetch candidate sites from Snowflake."""
        return self.read_table(table_name)

    def get_tract_info(self, table_name: str = "POPS") -> pd.DataFrame:
        """Fetch tract population info from Snowflake."""
        return self.read_table(table_name)

    def get_boundaries(self, table_name: str = "BOUNDARIES") -> pd.DataFrame:
        """Fetch tract boundaries (GEOID, lat, lon, geom_geojson) from Snowflake."""
        return self.read_table(table_name)
