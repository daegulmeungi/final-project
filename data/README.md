## Source
- Steam Public API
  - Crimson Desert (App ID: 3321460)
  - Black Desert (App ID: 582660)
## Schema
| Column | Type | Description |
|--------|------|-------------|
| review_id | INT | Steam recommendation ID |
| language | STRING | Review language |
| voted_up | BOOLEAN | Positive(true) / Negative(false) |
| playtime_forever | INT | Total playtime (minutes) |
| timestamp_created | STRING | Review creation timestamp |
| review | STRING | Review text |
| game_title | STRING | crimson_desert / black_desert |
## Files
- `crimson_desert_reviews_sample.csv` - Crimson Desert reviews sample (1,000 rows)
- `black_desert_reviews_sample.csv` - Black Desert reviews sample (1,000 rows)
- Full dataset: 249,542 rows (collected via `src/ingest/collect_reviews.py`)
## Notes
- Raw data is excluded from this repository due to file size
- Run `src/ingest/collect_reviews.py` to collect full dataset