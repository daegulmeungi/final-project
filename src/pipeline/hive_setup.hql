DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS reviews_processed;

CREATE EXTERNAL TABLE reviews (
  review_id INT,
  language STRING,
  voted_up BOOLEAN,
  playtime_forever INT,
  timestamp_created STRING,
  review STRING,
  game_title STRING,
  region STRING,
  playtime_range STRING
)
STORED AS PARQUET
LOCATION 'hdfs:///user/maria_dev/steam/processed';

CREATE TABLE reviews_processed AS
SELECT
  review_id,
  game_title,
  language,
  CASE
    WHEN language IN ('koreana', 'schinese', 'tchinese', 'japanese') THEN 'East'
    ELSE 'West'
  END AS language_region,
  voted_up,
  playtime_forever,
  playtime_range
FROM reviews;

INSERT OVERWRITE DIRECTORY 'hdfs:///tmp/hive_result1_region_rate'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT
  game_title,
  language_region,
  COUNT(*) AS total,
  SUM(CASE WHEN voted_up = true THEN 1 ELSE 0 END) AS positive,
  ROUND(SUM(CASE WHEN voted_up = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS positive_rate
FROM reviews_processed
GROUP BY game_title, language_region
ORDER BY game_title, language_region;

INSERT OVERWRITE DIRECTORY 'hdfs:///tmp/hive_result2_playtime_rate'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT
  playtime_range,
  COUNT(*) AS total,
  SUM(CASE WHEN voted_up = true THEN 1 ELSE 0 END) AS positive,
  ROUND(SUM(CASE WHEN voted_up = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS positive_rate
FROM reviews_processed
WHERE game_title = 'crimson_desert'
GROUP BY playtime_range
ORDER BY positive_rate;

INSERT OVERWRITE DIRECTORY 'hdfs:///tmp/hive_result3_playtime_dist'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT
  language_region,
  playtime_range,
  COUNT(*) AS total,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY language_region), 2) AS ratio
FROM reviews_processed
WHERE game_title = 'crimson_desert'
GROUP BY language_region, playtime_range
ORDER BY language_region, playtime_range;