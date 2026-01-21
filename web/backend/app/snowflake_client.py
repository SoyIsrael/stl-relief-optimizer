"""Snowflake database client for the web backend."""
import os
import json
from contextlib import contextmanager
from typing import Generator, List, Dict, Any

from dotenv import load_dotenv

# Load .env from the project root (two directories up from this file)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))


class SnowflakeClient:
    """Client for Snowflake database operations."""

    def __init__(self):
        """Initialize with credentials from environment variables."""
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")
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

    def get_block_groups(self) -> List[Dict[str, Any]]:
        """
        Fetch block groups with geometries for the frontend.
        Returns a list of dicts with geoid, lat, lon, population, and polygon coordinates.
        """
        query = """
            SELECT
                TO_VARCHAR(b.GEOID) AS GEOID,
                b."lat"::FLOAT AS LAT,
                b."lon"::FLOAT AS LON,
                b."geom_geojson" AS GEOM_GEOJSON,
                COALESCE(pc.POP, COALESCE(p.POP, 0))::FLOAT AS POP
            FROM BLOCK_GROUP_BOUNDARIES b
            LEFT JOIN BLOCK_GROUP_DEMOGRAPHICS p
              ON TO_VARCHAR(b.GEOID) = TO_VARCHAR(p.GEOID)
            LEFT JOIN BLOCK_GROUP_DEMOGRAPHICS_COUNTY pc
              ON TO_VARCHAR(b.GEOID) = TO_VARCHAR(pc.GEOID)
        """

        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            geom_json = row_dict.get("GEOM_GEOJSON")

            # Parse geometry
            polygon = None
            if geom_json:
                try:
                    if isinstance(geom_json, str):
                        geom = json.loads(geom_json)
                    else:
                        geom = geom_json

                    if geom.get("type") == "Polygon":
                        polygon = geom["coordinates"][0]
                    elif geom.get("type") == "MultiPolygon":
                        # Use first polygon for simplicity
                        polygon = geom["coordinates"][0][0]
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass

            if polygon:
                results.append({
                    "geoid": row_dict["GEOID"],
                    "lat": row_dict["LAT"],
                    "lon": row_dict["LON"],
                    "population": row_dict["POP"] or 0,
                    "polygon": polygon,
                })

        return results

    def get_candidates(self) -> List[Dict[str, Any]]:
        """Fetch candidate sites for the frontend."""
        query = """
            SELECT
                "site_id" AS SITE_ID,
                "name" AS NAME,
                "type" AS TYPE,
                "lat"::FLOAT AS LAT,
                "lon"::FLOAT AS LON
            FROM CANDIDATE_SITES
        """

        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "site_id": row[0],
                "name": row[1],
                "type": row[2],
                "lat": row[3],
                "lon": row[4],
            }
            for row in rows
        ]


# Singleton instance
_client = None


def get_client() -> SnowflakeClient:
    """Get or create the Snowflake client singleton."""
    global _client
    if _client is None:
        _client = SnowflakeClient()
    return _client
