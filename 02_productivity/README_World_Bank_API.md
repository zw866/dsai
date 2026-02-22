# World Bank API

A short guide to the World Bank Open Data API — endpoints, parameters, and how to query development indicators.

---

## Overview

The World Bank API provides free programmatic access to thousands of development indicators (GDP, population, poverty, education, and more) for countries and regions. Data is returned as JSON or XML. No API key is required.

---

## Usage

### Base URL

```
https://api.worldbank.org/v2
```

### Endpoint Pattern

```
/country/{country_codes}/indicator/{indicator_id}
```

- `country_codes`: Semicolon-separated ISO codes (e.g., `USA;CHN;IND`)
- `indicator_id`: Indicator code (e.g., `NY.GDP.MKTP.CD` for GDP)

### Common Query Parameters

| Parameter  | Description                          |
|------------|--------------------------------------|
| `format`   | `json` or `xml`                      |
| `per_page` | Records per page (default 50, max 200) |
| `date`     | Year range as `start:end` (e.g., `2005:2024`) |
| `page`     | Page number for pagination           |

### Example Request

```bash
curl "https://api.worldbank.org/v2/country/USA;CHN/indicator/NY.GDP.MKTP.CD?format=json&per_page=50&date=2020:2023"
```

### Example Response Structure

Each page returns `[meta, data]`:

- **meta**: Pagination (`pages`, `total`, etc.)
- **data**: Array of records; each record includes `country`, `indicator`, `date`, `value`

---

## Notes

- No API key required.
- Rate limits apply; use reasonable `per_page` and avoid high-frequency polling.
- Not all country–indicator–year combinations have values; `value` may be `null`.
- Official docs: [World Bank API Documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-api-documentation).
- Browse indicators: [World Bank Data Catalog](https://datacatalog.worldbank.org/).
