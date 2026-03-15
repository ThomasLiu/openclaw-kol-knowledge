#!/usr/bin/env python3
"""导入所有视频到 Notion"""
import json
import urllib.request

NOTION_KEY = "ntn_b7586668500EIA1TPn8XabewPj7LrwiUztjxXK3uPqU9xX"
VIDEO_DS_ID = "26a21d45-1992-4adf-b355-bba74bd1c93c"

def add_video(title, uploader, views, url, platform, date_str="2026-03-15"):
    url_api = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"data_source_id": VIDEO_DS_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title[:80]}}]},
            "发布者": {"rich_text": [{"text": {"content": uploader}}]},
            "平台": {"select": {"name": platform}},
            "播放量": {"number": views},
            "链接": {"url": url},
            "状态": {"select": {"name": "待处理"}},
            "收录日期": {"date": {"start": date_str}}
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
        print(f"Error: {e}")
        return False

# YouTube 数据
youtube_videos = [
    ("AI Agents, Clearly Explained", "Jeff Su", 3951380, "https://www.youtube.com/watch?v=FwOTs4UxQS4"),
    ("From Zero to Your First AI Agent in 25 Minutes", "Futurepedia and AI Agent Lab", 3347545, "https://www.youtube.com/watch?v=EH5jx5qPabU"),
    ("How to Build & Sell AI Agents: Ultimate Guide", "Liam Ottley", 2193323, "https://www.youtube.com/watch?v=w0H1-b044KY"),
    ("The wild rise of OpenClaw", "Fireship", 1826702, "https://www.youtube.com/watch?v=ssYt09bCgUY"),
    ("OpenClaw Creator: Why 80% Of Apps Will Disappear", "Y Combinator", 800286, "https://www.youtube.com/watch?v=4uzGDAoNOZc"),
    ("Build an AI Agent From Scratch in Python", "Tech With Tim", 594162, "https://www.youtube.com/watch?v=ZaPbP9DwBOE"),
    ("Don't learn AI Agents without Learning these Fundamentals", "KodeKloud", 545607, "https://www.youtube.com/watch?v=ZaPbP9DwBOE"),
    ("AI Agents Explained: A Comprehensive Guide", "AI Alfie", 512446, "https://www.youtube.com/watch?v=hLJTcVHW8_I"),
    ("ClawdBot Full Tutorial for Beginners", "Mikey No Code", 442934, "https://www.youtube.com/watch?v=a63dUwXUgDo"),
    ("The Ultimate Beginner's Guide to OpenClaw", "Metics Media", 313798, "https://www.youtube.com/watch?v=st534T7-mdE"),
    ("【保姆级】OpenClaw 全网最细教学", "AI学长小林", 284057, "https://www.youtube.com/watch?v=2ZZCyHzo9as"),
    ("Agentic AI Engineering: Complete 4-Hour Workshop", "Jon Krohn", 202654, "https://www.youtube.com/watch?v=LSk5KaEGVk4"),
    ("大熱 OpenClaw「龍蝦」實測一個月", "Price.com.hk 香港格價網", 169833, "https://www.youtube.com/watch?v=NFjaGZSz6Xg"),
]

# Bilibili 数据
bilibili_videos = [
    ("一个视频搞懂OpenClaw！", "林亦LYi", 3746331, "https://www.bilibili.com/video/BV1jEAaz3E6K"),
    ("爆肝10亿token，我给OpenClaw做了个龙虾管家！", "秋芝2046", 2682106, "https://www.bilibili.com/video/BV1mYPSzmEkV"),
    ("【断网补全计划】妈祖换人真假，老高被罚五亿？", "瞎问虾猜丶", 1346190, "https://www.bilibili.com/video/BV1MBfTB2E3k"),
    ("全网疯抢的AI「小龙虾」到底割了多少打工人的韭菜？", "柳行长", 1144594, "https://www.bilibili.com/video/BV1PqPmzMEkG"),
    ("我让OpenClaw自动炒股， 最后赚钱了吗？", "是花子呀_", 1119570, "https://www.bilibili.com/video/BV1s4ZLBAE22"),
    ("【开箱】小米miclaw隐藏玩法？我家被AI占领了...", "陈抱一", 1053486, "https://www.bilibili.com/video/BV14vPfzMEwN"),
    ("为什么Mac mini糟全球疯抢？在mini使用3天OpenClaw之后", "大耳朵TV", 1052959, "https://www.bilibili.com/video/BV1sMFLzAE42"),
    ("警惕！全球已发现近15万个OpenClaw相关资产", "红衣大叔周鸿祎", 701816, "https://www.bilibili.com/video/BV1i1cRzPEKF"),
    ("⚡当我装了openclaw以后...⚡", "碧天蓝钻", 691554, "https://www.bilibili.com/video/BV1Hyc6zBEez"),
    ("OpenClaw小龙虾保姆级安装教程！小白10分钟搞定", "林粒粒呀", 826836, "https://www.bilibili.com/video/BV1UsP1zqEWc"),
]

count = 0

# 导入 YouTube
for title, uploader, views, url in youtube_videos:
    if add_video(title, uploader, views, url, "YouTube"):
        count += 1

# 导入 Bilibili
for title, uploader, views, url in bilibili_videos:
    if add_video(title, uploader, views, url, "Bilibili"):
        count += 1

print(f"✅ 总共导入 {count} 个视频到 Notion")
