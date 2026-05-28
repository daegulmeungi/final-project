import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

os.makedirs('charts', exist_ok=True)

BLACK_COLOR = '#3A86FF'
CRIMSON_COLOR = '#FF006E'
EAST_COLOR = '#FB5607'
WEST_COLOR = '#8338EC'
playtime_order = ['0~10h', '10~100h', '100h+']
width = 0.35

def find_csv(name):
    patterns = [
        f"**/{name}**/part-*.csv",
        f"**/{name}**/000000_0",
        f"{name}",
        f"**/{name}"
    ]
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        if files:
            return files[0]
    return name

# ──────────────────────────────────────────────
# 차트 1: 검은사막 vs 붉은사막 언어권별 긍정률 + 변화량
# ──────────────────────────────────────────────
df1 = pd.read_csv(find_csv('result6_game_comparison'))

fig, ax = plt.subplots(figsize=(9, 6))
x = np.arange(len(df1))

bars1 = ax.bar(x - width/2, df1['black_rate'], width, label='Black Desert', color=BLACK_COLOR, alpha=0.85)
bars2 = ax.bar(x + width/2, df1['crimson_rate'], width, label='Crimson Desert', color=CRIMSON_COLOR, alpha=0.85)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{bar.get_height()}%', ha='center', fontsize=10, fontweight='bold')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{bar.get_height()}%', ha='center', fontsize=10, fontweight='bold')

for i, row in df1.iterrows():
    ax.annotate(f'+{row["change"]}%p',
                xy=(i + width/2, row['crimson_rate']),
                xytext=(i + width/2 + 0.15, row['crimson_rate'] + 3),
                fontsize=9, color='green', fontweight='bold')

ax.set_title('Positive Rate by Region: Black Desert vs Crimson Desert', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Language Region', fontsize=11)
ax.set_ylabel('Positive Rate (%)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(df1['language_region'], fontsize=11)
ax.set_ylim(0, 105)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/chart1_region_comparison.png', dpi=150)
plt.close()
print("chart1 완료")

# ──────────────────────────────────────────────
# 차트 2: 붉은사막 플레이타임별 긍정률
# ──────────────────────────────────────────────
df2_raw = pd.read_csv(find_csv('hive_result2_playtime_rate'), header=None,
                      names=['playtime_range', 'total', 'positive', 'positive_rate'])
first_row2 = pd.DataFrame([['0~10h', 13460, 5543, 41.18]],
                           columns=['playtime_range', 'total', 'positive', 'positive_rate'])
df2 = pd.concat([first_row2, df2_raw], ignore_index=True)
df2 = df2.drop_duplicates(subset=['playtime_range'])
df2 = df2.set_index('playtime_range').reindex(playtime_order).reset_index()

colors2 = ['#FF6B6B', '#FFA94D', '#51CF66']
fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(df2['playtime_range'], df2['positive_rate'], color=colors2, alpha=0.85, width=0.5)

for bar, rate in zip(bars, df2['positive_rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{rate}%', ha='center', fontsize=11, fontweight='bold')

ax.set_title('Crimson Desert: Positive Rate by Playtime', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Playtime Range', fontsize=11)
ax.set_ylabel('Positive Rate (%)', fontsize=11)
ax.set_ylim(0, 105)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/chart2_playtime_rate.png', dpi=150)
plt.close()
print("chart2 완료")

# ──────────────────────────────────────────────
# 차트 3: 동서양 플레이타임 분포
# ──────────────────────────────────────────────
df3_raw = pd.read_csv(find_csv('hive_result3_playtime_dist'), header=None,
                      names=['language_region', 'playtime_range', 'total', 'ratio'])
first_row3 = pd.DataFrame([['East', '0~10h', 3826, 7.88]],
                           columns=['language_region', 'playtime_range', 'total', 'ratio'])
df3 = pd.concat([first_row3, df3_raw], ignore_index=True)
df3 = df3.drop_duplicates(subset=['language_region', 'playtime_range'])

east = df3[df3['language_region'] == 'East'].set_index('playtime_range').reindex(playtime_order).reset_index()
west = df3[df3['language_region'] == 'West'].set_index('playtime_range').reindex(playtime_order).reset_index()

x = np.arange(3)
fig, ax = plt.subplots(figsize=(9, 6))
bars1 = ax.bar(x - width/2, east['ratio'], width, label='East', color=EAST_COLOR, alpha=0.85)
bars2 = ax.bar(x + width/2, west['ratio'], width, label='West', color=WEST_COLOR, alpha=0.85)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{bar.get_height()}%', ha='center', fontsize=9, fontweight='bold')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{bar.get_height()}%', ha='center', fontsize=9, fontweight='bold')

ax.set_title('Crimson Desert: Playtime Distribution by Region', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Playtime Range', fontsize=11)
ax.set_ylabel('Ratio (%)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(playtime_order, fontsize=11)
ax.set_ylim(0, 65)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/chart3_playtime_dist.png', dpi=150)
plt.close()
print("chart3 완료")

# ──────────────────────────────────────────────
# 차트 4: 두 게임 플레이타임 패턴 비교
# ──────────────────────────────────────────────
df4 = pd.read_csv(find_csv('result3_playtime_pattern'))
df4 = df4.drop_duplicates(subset=['playtime_range'])
df4 = df4.set_index('playtime_range').reindex(playtime_order).reset_index()

x = np.arange(3)
fig, ax = plt.subplots(figsize=(9, 6))
bars1 = ax.bar(x - width/2, df4['black_ratio'], width, label='Black Desert', color=BLACK_COLOR, alpha=0.85)
bars2 = ax.bar(x + width/2, df4['crimson_ratio'], width, label='Crimson Desert', color=CRIMSON_COLOR, alpha=0.85)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{bar.get_height()}%', ha='center', fontsize=9, fontweight='bold')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{bar.get_height()}%', ha='center', fontsize=9, fontweight='bold')

ax.set_title('Playtime Pattern: Black Desert vs Crimson Desert', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Playtime Range', fontsize=11)
ax.set_ylabel('Ratio (%)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(playtime_order, fontsize=11)
ax.set_ylim(0, 65)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/chart4_playtime_pattern.png', dpi=150)
plt.close()
print("chart4 완료")

# ──────────────────────────────────────────────
# 차트 5: 동서양 평균 플레이타임 비교
# ──────────────────────────────────────────────
df5 = pd.read_csv(find_csv('result5_avg_playtime'))

east_hours = df5[df5['language_region'] == 'East']['avg_playtime_hours'].values
west_hours = df5[df5['language_region'] == 'West']['avg_playtime_hours'].values
games = ['Black Desert', 'Crimson Desert']

x = np.arange(2)
fig, ax = plt.subplots(figsize=(9, 6))
bars1 = ax.bar(x - width/2, east_hours, width, label='East', color=EAST_COLOR, alpha=0.85)
bars2 = ax.bar(x + width/2, west_hours, width, label='West', color=WEST_COLOR, alpha=0.85)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'{bar.get_height():.0f}h', ha='center', fontsize=9, fontweight='bold')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'{bar.get_height():.0f}h', ha='center', fontsize=9, fontweight='bold')

ax.set_title('Average Playtime by Region (hours)', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Game', fontsize=11)
ax.set_ylabel('Average Playtime (hours)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(games, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/chart5_avg_playtime.png', dpi=150)
plt.close()
print("chart5 완료")

# ──────────────────────────────────────────────
# 차트 6: 출시 초반 vs 이후 리뷰 수
# ──────────────────────────────────────────────
df6 = pd.read_csv(find_csv('result4_timeline'))

fig, ax = plt.subplots(figsize=(8, 6))
colors_tl = ['#FF6B6B', '#51CF66']
bars = ax.bar(df6['period'], df6['total_reviews'], color=colors_tl, alpha=0.85, width=0.4)

for bar, val in zip(bars, df6['total_reviews']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
            f'{val:,}', ha='center', fontsize=11, fontweight='bold')

ax.set_title('Crimson Desert: Review Count (Early vs Later)', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Period', fontsize=11)
ax.set_ylabel('Number of Reviews', fontsize=11)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/chart6_timeline.png', dpi=150)
plt.close()
print("chart6 완료")

# ──────────────────────────────────────────────
# 차트 7: 모델 AUC 비교
# ──────────────────────────────────────────────
df7 = pd.read_csv(find_csv('result7_model_auc'))

fig, ax = plt.subplots(figsize=(8, 6))
colors_auc = [CRIMSON_COLOR, BLACK_COLOR]
bars = ax.bar(df7['game_title'], df7['auc_score'], color=colors_auc, alpha=0.85, width=0.4)

for bar, val in zip(bars, df7['auc_score']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
            f'{val:.3f}', ha='center', fontsize=11, fontweight='bold')

ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, label='Random (0.5)')
ax.set_title('Logistic Regression AUC: Black Desert vs Crimson Desert', fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Game', fontsize=11)
ax.set_ylabel('AUC Score', fontsize=11)
ax.set_ylim(0, 0.85)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/chart7_model_auc.png', dpi=150)
plt.close()
print("chart7 완료")

print("\n모든 차트 저장 완료! charts/ 폴더 확인하세요.")