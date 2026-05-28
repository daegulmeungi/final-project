# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, round, sum as spark_sum, count, avg, to_date, lit
from pyspark.sql import Window
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator

spark = SparkSession.builder \
    .appName("SteamReviewAnalysis") \
    .enableHiveSupport() \
    .getOrCreate()

df = spark.read.parquet("hdfs:///user/maria_dev/steam/processed")

df_processed = df.withColumn(
    "language_region",
    when(col("language").isin("koreana", "schinese", "tchinese", "japanese"), "East")
    .otherwise("West")
)

df_clean = df_processed.dropna(subset=["voted_up", "playtime_forever", "language_region"])

black = df_clean.filter(col("game_title") == "black_desert") \
    .groupBy("language_region") \
    .agg(
        count("*").alias("black_total"),
        round(spark_sum(when(col("voted_up") == True, 1).otherwise(0)) * 100.0 / count("*"), 2).alias("black_rate")
    )

crimson = df_clean.filter(col("game_title") == "crimson_desert") \
    .groupBy("language_region") \
    .agg(
        count("*").alias("crimson_total"),
        round(spark_sum(when(col("voted_up") == True, 1).otherwise(0)) * 100.0 / count("*"), 2).alias("crimson_rate")
    )

result6 = black.join(crimson, "language_region") \
    .withColumn("change", round(col("crimson_rate") - col("black_rate"), 2)) \
    .orderBy("language_region")

result6.coalesce(1).write.mode("overwrite").csv("hdfs:///user/maria_dev/results/result6_game_comparison", header=True)

black_pt = df_clean.filter(col("game_title") == "black_desert") \
    .groupBy("playtime_range") \
    .agg(count("*").alias("black_total")) \
    .withColumn("black_ratio", round(col("black_total") * 100.0 / 49950, 2))

crimson_pt = df_clean.filter(col("game_title") == "crimson_desert") \
    .groupBy("playtime_range") \
    .agg(count("*").alias("crimson_total")) \
    .withColumn("crimson_ratio", round(col("crimson_total") * 100.0 / 199592, 2))

result3 = black_pt.join(crimson_pt, "playtime_range").orderBy("playtime_range")
result3.coalesce(1).write.mode("overwrite").csv("hdfs:///user/maria_dev/results/result3_playtime_pattern", header=True)

result5 = df_clean.groupBy("game_title", "language_region") \
    .agg(
        round(avg("playtime_forever"), 2).alias("avg_playtime_minutes"),
        round(avg("playtime_forever") / 60, 2).alias("avg_playtime_hours")
    ).orderBy("game_title", "language_region")

result5.coalesce(1).write.mode("overwrite").csv("hdfs:///user/maria_dev/results/result5_avg_playtime", header=True)

result4 = df_clean.filter(col("game_title") == "crimson_desert") \
    .withColumn("review_date", to_date(col("timestamp_created").cast("timestamp"))) \
    .withColumn("period",
        when(col("review_date") <= lit("2026-04-01"), "early(1month)")
        .otherwise("later")
    ) \
    .groupBy("period") \
    .agg(count("*").alias("total_reviews")) \
    .orderBy("period")

result4.coalesce(1).write.mode("overwrite").csv("hdfs:///user/maria_dev/results/result4_timeline", header=True)

result2 = df_clean.groupBy("game_title", "language") \
    .agg(
        count("*").alias("total"),
        round(spark_sum(when(col("voted_up") == True, 1).otherwise(0)) * 100.0 / count("*"), 2).alias("positive_rate")
    ).orderBy("game_title", "positive_rate", ascending=False)

result2.coalesce(1).write.mode("overwrite").csv("hdfs:///user/maria_dev/results/result2_language_rate", header=True)

df_corr = df_clean.withColumn(
    "playtime_score",
    when(col("playtime_range") == "0~10h", 1)
    .when(col("playtime_range") == "10~100h", 2)
    .otherwise(3)
).withColumn(
    "voted_up_int",
    when(col("voted_up") == True, 1).otherwise(0)
)

correlation = df_corr.stat.corr("playtime_score", "voted_up_int")
print("Total correlation:", correlation)

df_model = df_clean.withColumn(
    "region_index",
    when(col("language_region") == "East", 0).otherwise(1)
).withColumn(
    "playtime_index",
    when(col("playtime_range") == "0~10h", 1)
    .when(col("playtime_range") == "10~100h", 2)
    .otherwise(3)
).withColumn(
    "label",
    when(col("voted_up") == True, 1.0).otherwise(0.0)
)

assembler = VectorAssembler(inputCols=["region_index", "playtime_index"], outputCol="features")
df_ml = assembler.transform(df_model).select("features", "label", "game_title")

lr = LogisticRegression()
evaluator = BinaryClassificationEvaluator()

df_crimson_ml = df_ml.filter(col("game_title") == "crimson_desert")
train_c, test_c = df_crimson_ml.randomSplit([0.8, 0.2], seed=42)
model_crimson = lr.fit(train_c)
auc_crimson = evaluator.evaluate(model_crimson.transform(test_c))

df_black_ml = df_ml.filter(col("game_title") == "black_desert")
train_b, test_b = df_black_ml.randomSplit([0.8, 0.2], seed=42)
model_black = lr.fit(train_b)
auc_black = evaluator.evaluate(model_black.transform(test_b))

auc_df = spark.createDataFrame(
    [("crimson_desert", auc_crimson), ("black_desert", auc_black)],
    ["game_title", "auc_score"]
)
auc_df.coalesce(1).write.mode("overwrite").csv("hdfs:///user/maria_dev/results/result7_model_auc", header=True)
model_crimson.save("hdfs:///user/maria_dev/models/crimson_model")
model_black.save("hdfs:///user/maria_dev/models/black_model")
spark.stop()