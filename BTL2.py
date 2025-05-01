from bs4 import BeautifulSoup
print("BeautifulSoup đã cài thành công!")
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import Counter

# PHẦN 1: TÍNH TOÁN VÀ LƯU FILE results2.csv

# Đọc dữ liệu
df = pd.read_csv("premier_league_players_full.csv")

# Lọc các cột số học theo đúng thứ tự xuất hiện ban đầu
numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

# Gộp các đội trùng tên bằng cách chuẩn hóa
df['Team'] = df['Team'].str.strip().str.lower().str.title()

# Tính toán thống kê cho toàn giải
medians = df[numeric_cols].median().to_frame().T
medians.index = ["all"]
means_all = df[numeric_cols].mean().to_frame().T
means_all.index = ["all"]
stds_all = df[numeric_cols].std().to_frame().T
stds_all.index = ["all"]

# Tính toán cho từng đội
means_team = df.groupby("Team")[numeric_cols].mean()
stds_team = df.groupby("Team")[numeric_cols].std()
medians_team = df.groupby("Team")[numeric_cols].median()

# Hàm tạo tên cột
def format_cols(stat_type, cols):
    return [f"{stat_type} of {col}" for col in cols]

# Hàm tạo DataFrame cho mỗi nhóm
def prepare_stat_df(stat_df, stat_type):
    stat_df.columns = format_cols(stat_type, stat_df.columns)
    stat_df.insert(0, "Team", stat_df.index)
    return stat_df.reset_index(drop=True)

# Tạo bảng cho dòng "all"
df_all = pd.concat([
    prepare_stat_df(medians, "Median"),
    prepare_stat_df(means_all, "Mean"),
    prepare_stat_df(stds_all, "Std")
], axis=1)

df_all = df_all.loc[:, ~df_all.columns.duplicated()]
df_all = df_all.iloc[:1]

# Tạo bảng cho các đội
df_team = pd.concat([
    prepare_stat_df(means_team, "Mean"),
    prepare_stat_df(stds_team, "Std")
], axis=1)

df_team = df_team.loc[:, ~df_team.columns.duplicated()]
df_team_median = prepare_stat_df(medians_team, "Median")
df_team = df_team.merge(df_team_median, on="Team")

# Sắp xếp thứ tự cột theo CSV gốc
ordered_cols = []
for col in numeric_cols:
    ordered_cols += [
        f"Median of {col}",
        f"Mean of {col}",
        f"Std of {col}"
    ]

final_df = pd.concat([df_all, df_team], ignore_index=True)
final_df = final_df[["Team"] + ordered_cols]
final_df.to_csv("results2.csv", index=False)

# PHẦN 2: VẼ HISTOGRAM

# Tạo thư mục nếu chưa có
os.makedirs("histograms", exist_ok=True)

# Vẽ cho toàn giải
for col in numeric_cols:
    plt.figure(figsize=(8, 5))
    plt.hist(df[col].dropna(), bins=20, color='skyblue', edgecolor='black')
    plt.title(f'Distribution of {col} (All Players)')
    plt.xlabel(col)
    plt.ylabel('Number of Players')
    plt.grid(True)
    plt.tight_layout()
    safe_col = col.replace("/", "_").replace("\\", "_").replace(":", "_")
    plt.savefig(f"histograms/all_{safe_col}.png")
    plt.close()

# Vẽ cho từng đội
teams = df['Team'].dropna().unique()
for team in teams:
    team_df = df[df['Team'] == team]
    for col in numeric_cols:
        plt.figure(figsize=(8, 5))
        plt.hist(team_df[col].dropna(), bins=20, color='lightgreen', edgecolor='black')
        plt.title(f'Distribution of {col} ({team})')
        plt.xlabel(col)
        plt.ylabel('Number of Players')
        plt.grid(True)
        plt.tight_layout()
        team_filename = team.replace(" ", "_")
        safe_col = col.replace("/", "_").replace("\\", "_").replace(":", "_")
        plt.savefig(f"histograms/{team_filename}_{safe_col}.png")
        plt.close()

# PHẦN 3: TÌM ĐỘI MẠNH NHẤT

# Tính trung bình các chỉ số theo đội
team_means = df.groupby("Team")[numeric_cols].mean()

# Xác định đội đứng đầu từng chỉ số
top_teams = {}
for col in numeric_cols:
    top_team = team_means[col].idxmax()
    top_score = team_means[col].max()
    top_teams[col] = (top_team, top_score)

# Đếm số lần mỗi đội đứng đầu
top_counts = Counter(team for team, _ in top_teams.values())
best_team = top_counts.most_common(1)[0]

# Ghi kết quả ra file
with open("best_team_stats.txt", "w", encoding="utf-8") as f:
    f.write("Top team for each statistic:\n")
    for col, (team, score) in top_teams.items():
        f.write(f"{col}: {team} ({score:.2f})\n")
    f.write("\nTeam with the most top stats:\n")
    f.write(f"{best_team[0]} with {best_team[1]} top scores.\n")
