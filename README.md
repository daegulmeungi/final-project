펄어비스의 글로벌 시장 확대 성과 분석
붉은사막 Steam 리뷰 데이터 기반 (vs 검은사막)

1. 문제 정의
펄어비스는 전작 검은사막(Black Desert)으로 글로벌 시장에 진출했으나, 서양권 반응이 상대적으로 약했다.
2026년 3월 신작 붉은사막(Crimson Desert) 출시 이후 Steam에서 약 20만 건의 리뷰가 누적되며
글로벌 시장에서 큰 주목을 받고 있다.
이 프로젝트는 두 게임의 Steam 리뷰 데이터를 빅데이터 파이프라인으로 수집·처리하여
"붉은사막 출시를 통해 펄어비스가 글로벌 시장 확대에 성공했는가" 를 데이터 기반으로 검증한다.

2. 분석 질문
붉은사막은 전작 검은사막 대비 서양권에서 더 좋은 반응을 얻었는가?
붉은사막에 대한 동양권과 서양권 유저의 긍정 평가 비율 차이는?
플레이 시간이 길수록 긍정 평가를 하는 경향이 있는가?
출시 이후 리뷰 수 증가 추이로 글로벌 확산이 확인되는가?

3. 수집 데이터
Steam 공개 API — 붉은사막 (App ID: 3321460)
Steam 공개 API — 검은사막 (App ID: 582660)
수집 항목: 언어, 긍부정 여부, 플레이 시간, 작성 날짜

3. 기술 스택
데이터 수집 : Python (requests) — Steam API 자동 수집
저장 : HDFS (Parquet 포맷)
전처리 : Apache Spark (DataFrame)
집계 분석 : Apache Hive (HiveQL)
심화 분석 : Apache Spark + Spark MLlib
시각화 : Matplotlib, Seaborn

4. 파이프라인
[수집]
Steam API 호출 → 붉은사막/검은사막 리뷰 CSV 저장
(재실행 가능한 Python 스크립트로 자동화)
↓
[적재]
CSV → Parquet 변환 후 HDFS 업로드
↓
[전처리 - Spark DataFrame]
- 언어 컬럼 기반 동양/서양 분류 (East/West)
- 결측치 제거
↓
[분석 - Hive]
- 게임별 × 언어권별 긍정률 집계 (GROUP BY)
- 플레이타임 구간별 긍정률 집계
- 동서양 플레이타임 분포 집계
↓
[분석 - Spark]
- 두 게임 언어권별 긍정률 변화 JOIN + 변화량 계산
- 두 게임 플레이타임 패턴 JOIN 비교
- 플레이타임 vs 긍정률 상관관계 분석 (MLlib)
- 언어별 상세 긍정률 분석
- 동서양 평균 플레이타임 비교
- 출시 초반 vs 이후 리뷰 수 변화 (timestamp)
↓
[시각화]
- 언어권별 긍정률 비교 막대 차트
- 검은사막 vs 붉은사막 반응 비교 그래프
- 플레이타임 vs 긍정률 그래프
- 출시 이후 리뷰 수 추이 그래프

5. 디렉토리 구조
   final-project/
├── README.md
├── run_pipeline.sh
├── data/
│   └── README.md
├── src/
│   ├── ingest/
│   │   └── collect_reviews.py
│   ├── pipeline/
│   │   ├── hive_setup.hql
│   │   └── spark_analysis.py
│   └── analyze/
│       └── visualization.py
└── results/
    ├── csv/
    │   └── (분석 결과 CSV 파일들)
    └── charts/
        └── (시각화 결과 이미지)

6. . 참고 자료
Steam API 문서: https://store.steampowered.com/api
Apache Spark: https://spark.apache.org/docs/latest/
Apache Hive: https://hive.apache.org/

7. AI Tool Usage
Claude: 파이프라인 설계 검토, 디버깅 보조, README 초안 작성 보조
