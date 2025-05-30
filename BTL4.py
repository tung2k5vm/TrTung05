import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

existing_players_df = pd.read_csv("premier_league_players_full.csv")
existing_players = set(existing_players_df['Player'].str.lower().str.strip())

data = []

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options, headless=False) as driver:
    for page in range(1, 23):
        url = f"https://www.footballtransfers.com/en/values/players/most-valuable-players/playing-in-uk-premier-league/{page}"
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except Exception:
            continue

        html = driver.page_source
        soup = bs(html, 'html.parser')
        table = soup.find('table', class_='table table-hover no-cursor table-striped leaguetable mvp-table mb-0')

        if not table:
            continue

        rows = table.find('tbody').find_all('tr')
        for row in rows:
            player_td = row.find('td', class_='td-player')
            row_value = row.find_all('td', class_='text-center')
            value_td = row_value[1].find('span', class_='player-tag') if len(row_value) > 1 else None

            if player_td:
                name_tag = player_td.find('a')
                player_name = name_tag.get_text(strip=True).lower() if name_tag else 'n/a'
                value = value_td.get_text(strip=True) if value_td else 'n/a'

                if player_name in existing_players:
                    data.append({
                        'Player': player_name.title(),  
                        'Transfer Value': value
                    })

        time.sleep(5)  # Giúp tránh bị chặn IP

# Lưu kết quả ra CSV
df = pd.DataFrame(data)
df.to_csv("BTL4.csv", index=False)

