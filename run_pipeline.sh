#!/bin/bash
SANDBOX_USER="maria_dev"
SANDBOX_HOST="localhost"
SANDBOX_PORT="2222"
SSH_KEY="$HOME/.ssh/id_rsa"
SSH_CMD="ssh -i $SSH_KEY -o StrictHostKeyChecking=no -p $SANDBOX_PORT $SANDBOX_USER@$SANDBOX_HOST"
SCP_CMD="scp -i $SSH_KEY -o StrictHostKeyChecking=no -P $SANDBOX_PORT"
echo "[1/6] 데이터 수집 시작..."
python3 collect_reviews.py
echo "[2/6] HDFS 업로드..."
$SCP_CMD crimson_desert_reviews.csv $SANDBOX_USER@$SANDBOX_HOST:~/
$SCP_CMD black_desert_reviews.csv $SANDBOX_USER@$SANDBOX_HOST:~/
$SCP_CMD hive_setup.hql $SANDBOX_USER@$SANDBOX_HOST:~/
$SCP_CMD spark_analysis.py $SANDBOX_USER@$SANDBOX_HOST:~/
$SSH_CMD "hdfs dfs -mkdir -p /user/maria_dev/steam/raw"
$SSH_CMD "hdfs dfs -put -f ~/crimson_desert_reviews.csv /user/maria_dev/steam/raw/"
$SSH_CMD "hdfs dfs -put -f ~/black_desert_reviews.csv /user/maria_dev/steam/raw/"
$SSH_CMD "hdfs dfs -chmod -R 777 /user/maria_dev/steam"
$SSH_CMD "hdfs dfs -mkdir -p /user/maria_dev/results"
$SSH_CMD "hdfs dfs -chmod -R 777 /user/maria_dev/results" || true
echo "[3/6] Hive 분석 시작..."
$SSH_CMD "hive -f ~/hive_setup.hql"
echo "[4/6] Spark 분석 시작..."
$SSH_CMD "spark-submit ~/spark_analysis.py"
echo "[5/6] 결과 다운로드..."
$SSH_CMD "hdfs dfs -get -f /user/maria_dev/results ~/results"
$SSH_CMD "hdfs dfs -get -f /tmp/hive_result1_region_rate ~/results/"
$SSH_CMD "hdfs dfs -get -f /tmp/hive_result2_playtime_rate ~/results/"
$SSH_CMD "hdfs dfs -get -f /tmp/hive_result3_playtime_dist ~/results/"
mkdir -p results
$SCP_CMD -r $SANDBOX_USER@$SANDBOX_HOST:~/results ./results
echo "[6/6] 시각화..."
cp visualization.py ./results/
cd results
python3 visualization.py
cd ..
echo "파이프라인 완료! charts/ 폴더에서 결과 확인하세요."