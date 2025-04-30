import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import numpy as np

#1.Lấy dữ liệu cầu thủ

url_players = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"

options1 = uc.ChromeOptions()
options1.add_argument("--no-sandbox")
options1.add_argument("--disable-dev-shm-usage")
options1.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options1, headless=False) as driver:
    driver.get(url_players)
    time.sleep(5)
    html_players = driver.page_source

player_columns = {
    'player': 'Player',
    'nationality': 'Nationality',
    'team': 'Team',
    'position': 'Position',
    'age': 'Age',
    'games': 'MP',
    'games_starts': 'Starts',
    'minutes': 'Mins',
    'goals': 'Goal',
    'assists': 'Assists',
    'cards_yellow': 'Yellow cards',
    'cards_red': 'Red_cards',
    'xg': 'xG',
    'xg_assist': 'xGA',
    'progressive_carries': 'PrgC',
    'progressive_passes': 'PrgP',
    'progressive_passes_received': 'PrgR',
    'goals_per90': 'Gls',
    'assists_per90': 'Ast',
    'xg_per90': 'xG/90',
    'xg_assist_per90': 'xGA/90'
}

# Parse HTML
soup = bs(html_players, 'html.parser')
div = soup.find('div', id="div_stats_standard")
table = div.find('table', id='stats_standard')
tbody = table.find('tbody')
rows = tbody.find_all('tr')

# Thu thập dữ liệu
players_data = []

for row in rows:
    player = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in player_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            if stat == 'nationality':
                parts = val.split()
                val = parts[-1] if parts else ''
            player[stat] = val

    try:
        minutes = int(player.get('minutes', '0').replace(',', ''))
        if minutes >= 90:
            players_data.append(player)
    except:
        continue

df_players = pd.DataFrame(players_data)

#2.Lấy dữ liệu thủ môn

url_keepers = "https://fbref.com/en/comps/9/keepers/Premier-League-Stats"

options2 = uc.ChromeOptions()
options2.add_argument("--no-sandbox")
options2.add_argument("--disable-dev-shm-usage")
options2.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options2, headless=False) as driver:
    driver.get(url_keepers)
    time.sleep(5)
    html_keepers = driver.page_source

soup_keepers = bs(html_keepers, 'html.parser')
div_keepers = soup_keepers.find('div', id='div_stats_keeper')
table_keepers = div_keepers.find('table', id='stats_keeper')
body_keepers = table_keepers.find('tbody')
rows_keepers = body_keepers.find_all('tr')

keeper_columns = {
    'player': 'Player',
    'gk_minutes': 'Mins',
    'gk_goals_against_per90': 'GA90',
    'gk_save_pct': 'Save%',
    'gk_clean_sheet_pct': 'CS%',
    'gk_pens_save_pct': 'Penalty Save%'
}

keepers_data = []

for row in rows_keepers:
    player_data = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in keeper_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            player_data[stat] = val

    try:
        minutes = int(player_data.get('gk_minutes', '0').replace(',', ''))
        if minutes >= 90:
            keepers_data.append(player_data)
    except:
        continue

df_keepers = pd.DataFrame(keepers_data)

# ========== 3. Sửa phần lấy dữ liệu shooting ==========
url_shooting = "https://fbref.com/en/comps/9/shooting/Premier-League-Stats"

# Sửa URL trong driver.get()
options3 = uc.ChromeOptions()
options3.add_argument("--no-sandbox")
options3.add_argument("--disable-dev-shm-usage")
options3.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options3, headless=False) as driver:
    driver.get(url_shooting) 
    time.sleep(5)
    html_shooting = driver.page_source

shooting_columns = {
    'player': 'Player',
    'shots_on_target_pct': 'SoT%',
    'shots_on_target_per90': 'SoT/90',
    'goals_per_shot': 'G/Sh',
    'average_shot_distance': 'Dist'
}

# Parse HTML shooting
soup_shooting = bs(html_shooting, 'html.parser')
div_shooting = soup_shooting.find('div', id='div_stats_shooting')
table_shooting = div_shooting.find('table', id='stats_shooting')
tbody_shooting = table_shooting.find('tbody')
rows_shooting = tbody_shooting.find_all('tr')

# Thu thập dữ liệu shooting
shooting_data = []

for row in rows_shooting:
    player_data = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in shooting_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            player_data[stat] = val

    try:
        # Sửa thành check minute
        # s của shooting (data-stat='minutes')
        shooting_data.append(player_data)
    except:
        continue

df_shooting = pd.DataFrame(shooting_data)

url_passing = 'https://fbref.com/en/comps/9/passing/Premier-League-Stats'

# Sửa URL trong driver.get()
options4 = uc.ChromeOptions()
options4.add_argument("--no-sandbox")
options4.add_argument("--disable-dev-shm-usage")
options4.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options4, headless=False) as driver:
    driver.get(url_passing)
    time.sleep(5)
    html_passing = driver.page_source  

passing_columns = {
    'player': 'Player',
    'passes_completed': 'total passes completed (Cmp)',
    'passes_pct': 'Total pass completion (Cmp%)',
    'passes_total_distance': ' progressive passing distance (TotDist)',
    'passes_pct_short': 'Short pass completion (Cmp%)',
    'passes_pct_medium': 'Medium pass completion (Cmp%)',
    'passes_pct_long': 'Long pass completion (Cmp%)',
    'assisted_shots': 'KP',
    'passes_into_final_third': 'pass into final third',
    'passes_into_penalty_area': 'PPA',
    'crosses_into_penalty_area': 'CrsPA',
    'progressive_passes': 'PrgP'
}

soup_passing = bs(html_passing, 'html.parser')
div_passing = soup_passing.find('div', id='div_stats_passing')
table_passing = div_passing.find('table', id='stats_passing')
tbody_passing = table_passing.find('tbody')
rows_passing = tbody_passing.find_all('tr')

passing_data = []

for row in rows_passing:
    player_data = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in passing_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            player_data[stat] = val
    try:
        passing_data.append(player_data)
    except:
        continue

df_passing = pd.DataFrame(passing_data)

import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import time
import pandas as pd

url_GoalShot = 'https://fbref.com/en/comps/9/gca/Premier-League-Stats'

options5 = uc.ChromeOptions()
options5.add_argument("--no-sandbox")
options5.add_argument("--disable-dev-shm-usage")
options5.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options5, headless=False) as driver:
    driver.get(url_GoalShot) 
    time.sleep(5)
    html_GoalShot = driver.page_source 

GoalShot_columns = {
    'player': 'Player',
    'sca': ' SCA',
    'sca_per90': 'SCA90',
    'gca': 'GCA',
    'gca_per90': 'GCA90',
}

soup_GoalShot = bs(html_GoalShot, 'html.parser')
div_GoalShot = soup_GoalShot.find('div', id='div_stats_gca')
table_GoalShot = div_GoalShot.find('table', id='stats_gca')
tbody_GoalShot = table_GoalShot.find('tbody')
rows_GoalShot = tbody_GoalShot.find_all('tr')

# Thu thập dữ liệu GoalShot
GoalShot_data = []

for row in rows_GoalShot:
    player_data = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in GoalShot_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            player_data[stat] = val

    try:
        GoalShot_data.append(player_data)
    except:
        continue

df_GoalShot = pd.DataFrame(GoalShot_data)

#6. Def Stat:

url_Defense = 'https://fbref.com/en/comps/9/defense/Premier-League-Stats'

# Sửa URL trong driver.get()
options6 = uc.ChromeOptions()
options6.add_argument("--no-sandbox")
options6.add_argument("--disable-dev-shm-usage")
options6.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options6, headless=False) as driver:
    driver.get(url_Defense) 
    time.sleep(5)
    html_Defense = driver.page_source 

Defense_columns = {
    'player': 'Player',
    'tackles': 'Def_Tkl',
    'tackles_won': 'Def_TklW',
    'challenges': 'Def_Att',
    'blocks': 'Def_Blocks',
    'blocked_shots': 'Def_Sh',
    'blocked_passes': 'Def_Pass',
    'interceptions': 'Def_Int'
}

soup_Defense = bs(html_Defense, 'html.parser')
div_Defense = soup_Defense.find('div', id='div_stats_defense')
table_Defense = div_Defense.find('table', id='stats_defense')
tbody_Defense = table_Defense.find('tbody')
rows_Defense = tbody_Defense.find_all('tr')

# Thu thập dữ liệu Defense
Defense_data = []

for row in rows_Defense:
    player_data = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in Defense_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            player_data[stat] = val

    try:
        Defense_data.append(player_data)
    except:
        continue

df_Defense = pd.DataFrame(Defense_data)

#7. Poss stat:

url_Possession = 'https://fbref.com/en/comps/9/possession/Premier-League-Stats'

# Sửa URL trong driver.get()
options7 = uc.ChromeOptions()
options7.add_argument("--no-sandbox")
options7.add_argument("--disable-dev-shm-usage")
options7.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options7, headless=False) as driver:
    driver.get(url_Possession)
    time.sleep(5)
    html_Possession = driver.page_source 

Possession_columns = {
    'player': 'Player',
    'touches': ' Touches',
    'touches_def_pen_area': 'Def Pen',
    'touches_def_3rd': 'Def 3rd',
    'touches_mid_3rd': 'Mid 3rd',
    'touches_att_3rd': 'Att 3rd',
    'touches_att_pen_area': 'Att Pen ',
    'take_ons': 'Att',
    'take_ons_won_pct': 'Succ%',
    'take_ons_tackled_pct': 'Tkld%',
    'carries': 'Carries',
    'carries_progressive_distance': 'ProDist',
    'progressive_carries': 'ProgC',
    'carries_into_final_third': 'Carries 1/3',
    'carries_into_penalty_area': 'CPA',
    'miscontrols': 'Mis',
    'dispossessed': 'Dis',
    'passes_received': 'Rec',
    'progressive_passes_received': 'PrgR ',
}

soup_Possession = bs(html_Possession, 'html.parser')
div_Possession = soup_Possession.find('div', id='div_stats_possession')
table_Possession = div_Possession.find('table', id='stats_possession')
tbody_Possession = table_Possession.find('tbody')
rows_Possession = tbody_Possession.find_all('tr')

# Thu thập dữ liệu Possession
Possession_data = []

for row in rows_Possession:
    player_data = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in Possession_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            player_data[stat] = val

    try:
        Possession_data.append(player_data)
    except:
        continue

df_Possession = pd.DataFrame(Possession_data)

#8. Miscellaneous stat:

url_Miscel_Stats = 'https://fbref.com/en/comps/9/misc/Premier-League-Stats'

# Sửa URL trong driver.get()
options7 = uc.ChromeOptions()
options7.add_argument("--no-sandbox")
options7.add_argument("--disable-dev-shm-usage")
options7.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options7, headless=False) as driver:
    driver.get(url_Miscel_Stats) 
    time.sleep(5)
    html_Miscel_Stats = driver.page_source 

Miscel_Stats_columns = {
    'player': 'Player',
    'fouls': 'Fls',
    'fouled': 'Fld',
    'offsides': 'Off',
    'crosses': 'Crs',
    'ball_recoveries': 'Recov',
    'aerials_won': 'Duel_Won',
    'aerials_lost': 'Duel_Lost',
    'aerials_won_pct': 'Duel_Won%',
}

soup_Miscel_Stats = bs(html_Miscel_Stats, 'html.parser')
div_Miscel_Stats = soup_Miscel_Stats.find('div', id='div_stats_misc')
table_Miscel_Stats = div_Miscel_Stats.find('table', id='stats_misc')
tbody_Miscel_Stats = table_Miscel_Stats.find('tbody')
rows_Miscel_Stats = tbody_Miscel_Stats.find_all('tr')

# Thu thập dữ liệu Miscel_Stats
Miscel_Stats_data = []

for row in rows_Miscel_Stats:
    player_data = {}
    cols = row.find_all('td')
    if not cols:
        continue

    for col in cols:
        stat = col.get('data-stat')
        if stat in Miscel_Stats_columns:
            val = col.text.strip()
            if val == '':
                val = 'N/a'
            player_data[stat] = val
    try:
        Miscel_Stats_data.append(player_data)
    except:
        continue

df_Miscel_Stats = pd.DataFrame(Miscel_Stats_data)

# ========== Merge tất cả dữ liệu ==========
# Đổi tên các dataframe trước
df_keepers.rename(columns=keeper_columns, inplace=True)
df_players.rename(columns=player_columns, inplace=True)
df_shooting.rename(columns=shooting_columns, inplace=True)
df_passing.rename(columns=passing_columns, inplace=True)
df_GoalShot.rename(columns=GoalShot_columns, inplace=True)
df_Defense.rename(columns=Defense_columns, inplace=True)
df_Possession.rename(columns=Possession_columns, inplace=True)
df_Miscel_Stats.rename(columns=Miscel_Stats_columns, inplace=True)

#Xử lý trước Merge:

df_keepers = df_keepers.drop_duplicates(subset=["Player"])
df_shooting = df_shooting.drop_duplicates(subset=["Player"])
df_passing = df_passing.drop_duplicates(subset=["Player"])
df_GoalShot = df_GoalShot.drop_duplicates(subset=["Player"])
df_Defense = df_Defense.drop_duplicates(subset=["Player"])
df_Possession = df_Possession.drop_duplicates(subset=["Player"])
df_Miscel_Stats = df_Miscel_Stats.drop_duplicates(subset=["Player"])


# Merge từng bước
merged_df = pd.merge(df_players, df_keepers, on="Player", how="left")
merged_df = pd.merge(merged_df, df_shooting, on="Player", how="left")
merged_df = pd.merge(merged_df, df_passing, on="Player", how="left")
merged_df = pd.merge(merged_df, df_GoalShot, on="Player", how="left")
merged_df = pd.merge(merged_df, df_Defense, on="Player", how="left")
merged_df = pd.merge(merged_df, df_Possession, on="Player", how="left")
merged_df = pd.merge(merged_df, df_Miscel_Stats, on="Player", how="left")

# Thêm cột First_Name và sắp xếp theo đó
merged_df['First_Name'] = merged_df['Player'].apply(lambda x: x.split()[0] if isinstance(x, str) else '')
merged_df.sort_values(by='First_Name', inplace=True)
merged_df.drop(columns=['First_Name'], inplace=True)

# Xử lý giá trị thiếu và lưu CSV
merged_df.fillna("N/a", inplace=True)
merged_df.to_csv("premier_league_players_full.csv", index=False)

print("Xuất file CSV thành công với đầy đủ dữ liệu!")