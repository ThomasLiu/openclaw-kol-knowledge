#!/usr/bin/env python3
"""导入 KOL 到 Notion"""
import json
import urllib.request

NOTION_KEY = "ntn_b7586668500EIA1TPn8XabewPj7LrwiUztjxXK3uPqU9xX"
KOL_DS_ID = "8f971d73-5b46-4aa5-b710-0bf66cccfcd3"

def add_kol(name, platform, url):
    url_api = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"data_source_id": KOL_DS_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": name}}]},
            "平台": {"select": {"name": platform}},
            "主页链接": {"url": url}
        }
    }
    
    req = urllib.request.Request(
        url_api,
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {NOTION_KEY}',
            'Notion-Version': '2026-03-11',
            'Content-Type': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return True
    except Exception as e:
        print(f"Error: {name} - {e}")
        return False

# YouTube KOL
youtube_kols = [
    ("Jeff Su", "YouTube", "https://www.youtube.com/@jeffsu"),
    ("Fireship", "YouTube", "https://www.youtube.com/@fireship"),
    ("Futurepedia", "YouTube", "https://www.youtube.com/@futurepedia"),
    ("Liam Ottley", "YouTube", "https://www.youtube.com/@LiamOttley"),
    ("Y Combinator", "YouTube", "https://www.youtube.com/@YCombinator"),
    ("Tech With Tim", "YouTube", "https://www.youtube.com/@TechWithTim"),
    ("KodeKloud", "YouTube", "https://www.youtube.com/@KodeKloud"),
    ("Mikey No Code", "YouTube", "https://www.youtube.com/@MikeyNoCode"),
    ("Jon Krohn", "YouTube", "https://www.youtube.com/@JonKrohn"),
    ("AI Alfie", "YouTube", "https://www.youtube.com/@AIAlfie"),
]

# Bilibili KOL  
bilibili_kols = [
    ("林亦LYi", "Bilibili", "https://space.bilibili.com/lya"),
    ("秋芝2046", "Bilibili", "https://space.bilibili.com/"),
    ("瞎问虾猜丶", "Bilibili", "https://space.bilibili.com/"),
    ("柳行长", "Bilibili", "https://space.bilibili.com/"),
    ("陈抱一", "Bilibili", "https://space.bilibili.com/"),
    ("大耳朵TV", "Bilibili", "https://space.bilibili.com/"),
    ("红衣大叔周鸿祎", "Bilibili", "https://space.bilibili.com/"),
    ("碧天蓝钻", "Bilibili", "https://space.bilibili.com/"),
    ("林粒粒呀", "Bilibili", "https://space.bilibili.com/"),
    ("是花子呀_", "Bilibili", "https://space.bilibili.com/"),
]

count = 0

# 添加 YouTube KOL
for name, platform, url in youtube_kols:
    if add_kol(name, platform, url):
        count += 1
        print(f"✓ {name}")

# 添加 Bilibili KOL
for name, platform, url in bilibili_kols:
    if add_kol(name, platform, url):
        count += 1
        print(f"✓ {name}")

print(f"\n✅ 总共添加 {count} 个 KOL")
