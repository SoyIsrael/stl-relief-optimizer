import requests
import pandas as pd

def fetch_acs_tract_info(year, state, county):
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {
        "get": "NAME,B01001_001E",
        "for": "tract:*",
        "in": f"state:{state} county:{county}",
    }
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()

    data = r.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    df["GEOID"] = df["state"] + df["county"] + df["tract"]
    df["POP"] = pd.to_numeric(df["B01001_001E"], errors="coerce")
    df["NAME"] = df["NAME"]

    return df[["GEOID", "NAME", "POP"]]

# Missouri
YEAR = 2023
STATE = "29"
STL_CITY = "510"
STL_COUNTY = "189"

df_city = fetch_acs_tract_info(YEAR, STATE, STL_CITY)
df_county = fetch_acs_tract_info(YEAR, STATE, STL_COUNTY)

tract_info = (
    pd.concat([df_city, df_county], ignore_index=True)
    .drop_duplicates("GEOID")
)

tract_info.to_csv("tract_info.csv", index=False)
print("Saved tract_info.csv")
