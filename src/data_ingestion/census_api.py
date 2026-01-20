"""Fetch tract-level data from the Census Bureau ACS API."""
import requests
import pandas as pd


def fetch_acs_tract_info(
    year: int,
    state: str,
    county: str,
    variables: str = "NAME,B01001_001E",
    timeout: int = 60,
) -> pd.DataFrame:
    """
    Fetch ACS 5-year estimates for census tracts.

    Args:
        year: ACS data year (e.g., 2023)
        state: 2-digit FIPS code (e.g., "29" for Missouri)
        county: 3-digit FIPS code (e.g., "510" for St. Louis City)
        variables: Comma-separated ACS variable codes
        timeout: Request timeout in seconds

    Returns:
        DataFrame with GEOID, NAME, and POP columns
    """
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {
        "get": variables,
        "for": "tract:*",
        "in": f"state:{state} county:{county}",
    }

    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    df["GEOID"] = df["state"] + df["county"] + df["tract"]
    df["POP"] = pd.to_numeric(df["B01001_001E"], errors="coerce")

    return df[["GEOID", "NAME", "POP"]]


def fetch_stl_tract_info(year: int = 2023) -> pd.DataFrame:
    """Fetch tract info for St. Louis City and County combined."""
    STATE = "29"  # Missouri
    STL_CITY = "510"
    STL_COUNTY = "189"

    df_city = fetch_acs_tract_info(year, STATE, STL_CITY)
    df_county = fetch_acs_tract_info(year, STATE, STL_COUNTY)

    return pd.concat([df_city, df_county], ignore_index=True).drop_duplicates("GEOID")
