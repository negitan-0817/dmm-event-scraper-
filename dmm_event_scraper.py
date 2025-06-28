# dmm_event_scraper.py

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

URL = "https://www.dmm.co.jp/live/chat/-/avevent/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse_event_list():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    event_data = []
    events = soup.select("ul#eventList li")

    for event in events:
        try:
            link_tag = event.find("a")
            img_tag = event.find("img")
            name_tag = event.select_one(".name")
            time_tag = event.select_one(".time")

            event_link = "https://www.dmm.co.jp" + link_tag.get("href")
            img_url = img_tag.get("src")
            name = name_tag.text.strip()
            time_str = time_tag.text.strip()

            # 日時整形（例: "6/28(土) 22:00～"）
            today_year = datetime.today().year
            datetime_obj = datetime.strptime(f"{today_year} {time_str}", "%Y %m/%d(%a) %H:%M～")
            datetime_iso = datetime_obj.isoformat()

            event_data.append({
                "actress_name": name,
                "event_time": datetime_iso,
                "image_url": img_url,
                "event_link": event_link
            })

        except Exception as e:
            print("スキップされたイベント:", e)
            continue

    return event_data

def save_to_json(data):
    # スクリプトと同じディレクトリにある "public" フォルダに保存する
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "public")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "events.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{len(data)}件のイベントを保存しました → {output_path}")


if __name__ == "__main__":
    data = parse_event_list()
    save_to_json(data)


import os
import subprocess
from datetime import datetime

def git_commit_and_push():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    token = os.environ.get("GH_TOKEN")
    if not token:
        print("GitHub token (GH_TOKEN) が設定されていません。")
        return

    # リポジトリ情報
    repo_url = "https://github.com/negitan-0817/dmm-event-scraper.git"
    https_url = repo_url.replace("https://", f"https://{token}@")

    # Git 設定（初回のみ）
    subprocess.run(["git", "config", "--global", "user.email", "render@render.com"], check=True)
    subprocess.run(["git", "config", "--global", "user.name", "Render Bot"], check=True)

    try:
        os.chdir(repo_dir)

        # 念のため Git のキャッシュから一度削除してから再登録
        subprocess.run(["git", "rm", "--cached", "public/events.json"], check=False)
        subprocess.run(["git", "add", "public/events.json"], check=True)

        commit_message = f"Update events.json at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        subprocess.run(["git", "push", https_url, "HEAD:refs/heads/main"], check=True)
        print("✅ events.json を GitHub に push しました。")


    except subprocess.CalledProcessError as e:
        print("❌ Git 操作中にエラーが発生しました:", e)

# --- ここで呼び出し ---
git_commit_and_push()
