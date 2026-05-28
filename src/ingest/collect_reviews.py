import requests
import csv
import time

GAMES = {
    "crimson_desert": (3321460, 200000),
    "black_desert": (582660, 50000)
}

for game_title, (app_id, limit) in GAMES.items():
    cursor = "*"
    total = 0
    filename = f"{game_title}_reviews.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["review_id", "language", "voted_up", "playtime_forever",
                         "timestamp_created", "review", "game_title"])
        while True:
            response = requests.get(
                f"https://store.steampowered.com/appreviews/{app_id}",
                params={
                    "json": 1,
                    "num_per_page": 100,
                    "language": "all",
                    "cursor": cursor,
                    "review_type": "all",
                    "purchase_type": "all"
                }
            )
            if response.status_code != 200 or not response.text.strip():
                print(f"빈 응답, 재시도...")
                time.sleep(2)
                continue
            data = response.json()
            reviews = data.get("reviews", [])
            if not reviews:
                break
            for r in reviews:
                writer.writerow([
                    r["recommendationid"],
                    r["language"],
                    r["voted_up"],
                    r["author"]["playtime_forever"],
                    r["timestamp_created"],
                    r["review"].replace("\n", " "),
                    game_title
                ])

            total += len(reviews)
            cursor = data["cursor"]
            print(f"[{game_title}] 수집 중... {total}개")
            time.sleep(0.5)

            if total >= limit:
                break

    print(f"[{game_title}] 완료! 총 {total}개 → {filename}")