#!/usr/bin/env python3
"""
OpenClaw KOL 知识库自动更新脚本 v2
每 4 小时运行一次
自动搜索、转写、翻译、分析、存库
"""
import os
import sys
import json
import subprocess
import re
from datetime import datetime

# 如果需要 requests，用 subprocess 调用 curl
import re

# 配置
GITHUB_DIR = os.path.expanduser("~/openclaw-kol-knowledge")
DATA_DIR = os.path.join(GITHUB_DIR, "data")
NOTION_KEY = "ntn_b7586668500EIA1TPn8XabewPj7LrwiUztjxXK3uPqU9xX"
# 视频库 data_source_id
NOTION_VIDEO_DS_ID = "3231c433-5fd4-807b-b134-000b244dd7c5"

# 搜索关键词 - 更精准
YOUTUBE_KEYWORDS = ["OpenClaw"]
BILIBILI_KEYWORDS = ["OpenClaw"]
MIN_VIEWS = 5000  # 最低播放量
MAX_VIDEOS_PER_PLATFORM = 10  # 每个平台最多收录

# 过滤关键词（初级/科普内容）
FILTER_KEYWORDS = [
    "零基础", "入门", "新手", "教程", "初学者", "保姆级",
    "什么是", "科普", "介绍", "一小时", "5分钟",
    "day1", "beginner", "tutorial", "getting started",
    "crash course", " basics", " basics"
]

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "youtube"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "bilibili"), exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_cmd(cmd, capture=True):
    """运行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        log(f"❌ 命令失败: {cmd}")
        log(f"   {result.stderr[:200]}")
        return None
    return result.stdout if capture else True

def get_video_id(url):
    """从 URL 提取视频 ID"""
    # YouTube: https://youtube.com/watch?v=VIDEO_ID 或 https://youtu.be/VIDEO_ID
    # Bilibili: https://bilibili.com/video/BVxxx 或 avxxxxx
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'bilibili\.com/video/(BV[\w]+|av\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url.split('/')[-1].split('?')[0][:20]

def should_filter_video(title):
    """过滤初级/科普内容"""
    title_lower = title.lower()
    for kw in FILTER_KEYWORDS:
        if kw.lower() in title_lower:
            return True
    return False

def search_youtube_videos(keywords, limit=10):
    """搜索 YouTube 视频"""
    log("🔍 搜索 YouTube...")
    videos = []
    
    for kw in keywords:
        # 使用 yt-dlp 搜索
        cmd = f'yt-dlp --flat-playlist "ytsearch{limit}:{kw}" --dump-json'
        output = run_cmd(cmd)
        if not output:
            continue
            
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                view_count = data.get('view_count', 0)
                if view_count >= MIN_VIEWS:
                    videos.append({
                        'platform': 'youtube',
                        'id': data.get('id', ''),
                        'title': data.get('title', ''),
                        'uploader': data.get('uploader', ''),
                        'view_count': view_count,
                        'url': data.get('webpage_url', ''),
                        'duration': data.get('duration', 0),
                        'upload_date': data.get('upload_date', ''),
                    })
            except:
                continue
    
    # 去重并按播放量排序
    seen = set()
    unique_videos = []
    for v in videos:
        if v['id'] not in seen:
            seen.add(v['id'])
            unique_videos.append(v)
    
    unique_videos.sort(key=lambda x: x['view_count'], reverse=True)
    return unique_videos[:limit]

def search_bilibili_videos(keywords, limit=10):
    """搜索 Bilibili 视频 - 使用 API"""
    log("🔍 搜索 Bilibili...")
    videos = []
    
    for kw in keywords:
        import urllib.request
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={kw}&order=click&jsonp=jsonp"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('code') == 0:
                    for item in data.get('data', {}).get('result', [])[:limit*2]:
                        title = item.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
                        view_count = item.get('play', 0)
                        
                        if view_count >= MIN_VIEWS:
                            videos.append({
                                'platform': 'bilibili',
                                'id': item.get('bvid', ''),
                                'title': title,
                                'uploader': item.get('author', ''),
                                'view_count': view_count,
                                'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                                'duration': item.get('duration', 0),
                                'upload_date': '',
                            })
        except Exception as e:
            log(f"  ❌ Bilibili 搜索失败: {e}")
    
    # 去重并按播放量排序
    seen = set()
    unique_videos = []
    for v in videos:
        if v['id'] and v['id'] not in seen:
            seen.add(v['id'])
            unique_videos.append(v)
    
    unique_videos.sort(key=lambda x: x['view_count'], reverse=True)
    return unique_videos[:limit]

def load_existing_videos():
    """加载已收录的视频列表"""
    existing = {}
    for platform in ['youtube', 'bilibili']:
        platform_dir = os.path.join(DATA_DIR, platform)
        if not os.path.exists(platform_dir):
            continue
        for video_id in os.listdir(platform_dir):
            meta_file = os.path.join(platform_dir, video_id, 'metadata.json')
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        existing[data['id']] = data
                except:
                    pass
    return existing

def is_video_processed(video_id):
    """检查视频是否已处理完成"""
    for platform in ['youtube', 'bilibili']:
        transcript_file = os.path.join(DATA_DIR, platform, video_id, 'transcript.md')
        if os.path.exists(transcript_file):
            return True
    return False

def download_audio(video_info):
    """下载视频音频 - 暂时跳过，等有代理再处理"""
    video_id = video_info['id']
    platform = video_info['platform']
    video_dir = os.path.join(DATA_DIR, platform, video_id)
    os.makedirs(video_dir, exist_ok=True)
    
    log(f"  ⏭️ 跳过下载 (YouTube 被限制): {video_info['title'][:30]}...")
    return None

def transcribe_audio(audio_path, language=None):
    """用 Whisper 转写"""
    log(f"  🎤 转写中...")
    
    # 激活 conda whisper 环境
    cmd = f'''
source /usr/local/Caskroom/miniconda/base/etc/profile.d/conda.sh && \
conda run -n whisper python -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('{audio_path}', language={repr(language)})
print(result['text'])
"
'''
    output = run_cmd(cmd)
    if output:
        return output.strip()
    return None

def translate_to_chinese(text):
    """翻译为中文（调用 MiniMax API）"""
    log(f"  🌐 翻译为中文...")
    # TODO: 实现翻译
    return text

def analyze_transcript(transcript, title):
    """分析转写内容"""
    log(f"  📝 分析内容...")
    # TODO: 用 LLM 分析
    return {
        'summary': '待分析',
        'highlights': [],
        'tags': [],
        'why_good': '待分析'
    }

def save_video_data(video_info, transcript=None, transcript_zh=None, analysis=None):
    """保存视频数据到 GitHub"""
    video_id = video_info['id']
    platform = video_info['platform']
    video_dir = os.path.join(DATA_DIR, platform, video_id)
    os.makedirs(video_dir, exist_ok=True)
    
    # 更新元数据
    metadata = {
        'id': video_id,
        'platform': platform,
        'title': video_info['title'],
        'uploader': video_info['uploader'],
        'view_count': video_info['view_count'],
        'url': video_info['url'],
        'duration': video_info['duration'],
        'upload_date': video_info['upload_date'],
        'last_updated': datetime.now().isoformat(),
        'processed': transcript is not None
    }
    
    with open(os.path.join(video_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    if transcript:
        with open(os.path.join(video_dir, 'transcript.md'), 'w', encoding='utf-8') as f:
            f.write(transcript)
    
    if transcript_zh:
        with open(os.path.join(video_dir, 'transcript_zh.md'), 'w', encoding='utf-8') as f:
            f.write(transcript_zh)
    
    if analysis:
        with open(os.path.join(video_dir, 'analysis.json'), 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    log(f"  ✅ 已保存: {video_id}")

def save_to_notion(video_info, transcript_data, analysis):
    """保存到 Notion"""
    if not NOTION_VIDEO_DS_ID:
        log("  ⚠️ Notion 数据库未配置，跳过")
        return False
    
    log("  💾 保存到 Notion...")
    
    import urllib.request
    import urllib.error
    
    # 构建标题（包含关键信息）
    title = f"{video_info.get('title', 'Untitled')[:60]} | {video_info.get('uploader', 'Unknown')} | {video_info.get('view_count', 0)} views | {video_info.get('platform', '')}"
    
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"data_source_id": NOTION_VIDEO_DS_ID},
        "properties": {
            "名称": {"title": [{"text": {"content": title}}]}
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {NOTION_KEY}',
            'Notion-Version': '2025-09-03',
            'Content-Type': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            log(f"  ✅ 已添加到 Notion")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        log(f"  ❌ Notion API 错误: {e.code} - {error_body[:100]}")
        return False
    except Exception as e:
        log(f"  ❌ 保存失败: {str(e)[:50]}")
        return False

def git_commit_and_push():
    """提交到 GitHub"""
    log("📤 提交到 GitHub...")
    
    # 检查是否有更改
    cmd = 'cd ~/openclaw-kol-knowledge && git status --porcelain'
    if not run_cmd(cmd):
        return
    
    # 添加并提交
    run_cmd('cd ~/openclaw-kol-knowledge && git add -A')
    run_cmd(f'cd ~/openclaw-kol-knowledge && git commit -m "KOL update {datetime.now().strftime("%Y-%m-%d %H:%M")}"')
    run_cmd('cd ~/openclaw-kol-knowledge && git push')
    
    log("  ✅ 已推送到 GitHub")

def main():
    log("=" * 60)
    log(f"🆕 OpenClaw KOL 更新开始 - {datetime.now()}")
    log("=" * 60)
    
    # 1. 加载已收录的视频
    existing = load_existing_videos()
    log(f"📚 已收录: {len(existing)} 个视频")
    
    # 2. 搜索新视频
    youtube_videos = search_youtube_videos(YOUTUBE_KEYWORDS, MAX_VIDEOS_PER_PLATFORM)
    bilibili_videos = search_bilibili_videos(BILIBILI_KEYWORDS, MAX_VIDEOS_PER_PLATFORM)
    
    log(f"🔍 YouTube: 找到 {len(youtube_videos)} 个视频")
    log(f"🔍 Bilibili: 找到 {len(bilibili_videos)} 个视频")
    
    # 3. 处理视频
    new_count = 0
    update_count = 0
    
    for video in youtube_videos + bilibili_videos:
        video_id = video['id']
        
        # 过滤初级内容
        if should_filter_video(video.get('title', '')):
            log(f"  ⏭️ 过滤初级内容: {video['title'][:30]}...")
            continue
        
        # 检查是否已处理
        if is_video_processed(video_id):
            # 已处理过，只更新播放量
            if video_id in existing:
                old_views = existing[video_id].get('view_count', 0)
                if video['view_count'] != old_views:
                    log(f"  🔄 更新播放量: {video['title'][:30]} ({old_views} → {video['view_count']})")
                    save_video_data(video)
                    update_count += 1
            continue
        
        # 新视频：完整处理
        log(f"\n📺 处理: {video['title'][:40]}")
        
        # 下载音频
        audio_path = download_audio(video)
        
        # 即使下载失败也保存元数据
        if True:  # 始终保存
            # 转写
            transcript = None
            if audio_path:
                transcript = transcribe_audio(audio_path)
            
            if not transcript:
                log(f"  ⏭️ 跳过转写: 无音频")
        
        # 翻译（非中文）
        transcript_zh = None
        # TODO: 检测语言
        
        # 分析
        analysis = analyze_transcript(transcript, video['title'])
        
        # 保存
        save_video_data(video, transcript, transcript_zh, analysis)
        
        # 尝试保存到 Notion
        save_to_notion(video, {'original': transcript, 'zh': transcript_zh}, analysis)
        
        new_count += 1
    
    log(f"\n✅ 处理完成: 新增 {new_count} 个，更新 {update_count} 个")
    
    # 4. 提交到 GitHub
    if new_count > 0 or update_count > 0:
        git_commit_and_push()
    
    log("🏁 完成!")

if __name__ == "__main__":
    main()
