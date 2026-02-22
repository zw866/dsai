import requests

BASE = "https://api.worldbank.org/v2"
COUNTRIES = "USA;CHN;IND;JPN;DEU"          # 你可以改成任何国家代码组合
INDICATOR = "NY.GDP.MKTP.CD"              # GDP (current US$)
DATE_RANGE = "2005:2024"                  # 20 years
PER_PAGE = 200                            # 一次拿多点，减少翻页

def fetch_all_pages(url, params):
    all_rows = []
    page = 1

    while True:
        params_with_page = dict(params)
        params_with_page["page"] = page

        r = requests.get(url, params=params_with_page, timeout=30)
        print("status:", r.status_code, "| page:", page)

        if r.status_code != 200:
            # 打印一点内容帮助排错
            print("response text (first 300 chars):", r.text[:300])
            raise RuntimeError(f"Request failed: {r.status_code}")

        payload = r.json()

        # World Bank API 正常返回是 [meta, data]
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError("Unexpected response format")

        meta, data = payload[0], payload[1]
        if not data:
            break

        all_rows.extend(data)

        pages = meta.get("pages", 1)
        if page >= pages:
            break
        page += 1

    return all_rows

def main():
    url = f"{BASE}/country/{COUNTRIES}/indicator/{INDICATOR}"
    params = {
        "format": "json",
        "per_page": PER_PAGE,
        "date": DATE_RANGE,
    }

    rows = fetch_all_pages(url, params)

    # 清洗 & 只保留关键字段，方便截图展示
    cleaned = []
    for row in rows:
        cleaned.append({
            "country": (row.get("country") or {}).get("value"),
            "country_id": (row.get("country") or {}).get("id"),
            "year": row.get("date"),
            "indicator": ((row.get("indicator") or {}).get("value")),
            "indicator_id": ((row.get("indicator") or {}).get("id")),
            "value": row.get("value"),
            "unit": row.get("unit"),
            "obs_status": row.get("obs_status"),
        })

    # 过滤掉没有数值的行（有些年份可能是 None）
    cleaned = [x for x in cleaned if x["value"] is not None]

    print("\nTotal records (non-null value):", len(cleaned))
    print("First 15 records:")
    for x in cleaned[:15]:
        print(x)

if __name__ == "__main__":
    main()
