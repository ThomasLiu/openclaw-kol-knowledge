#!/usr/bin/env python3
"""
OpenClaw KOL 视频转写脚本
用法: python transcribe.py <video_url> [output_dir]
"""
import os
import sys
import json
import subprocess
import whisper

# 配置
MODEL_SIZE = "base"  # base/small/medium/large
OUTPUT_DIR = os.path.expanduser("~/openclaw-kol-knowledge/data")

def download_audio(url, output_path):
    """用 yt-dlp 下载音频"""
    print(f"📥 下载音频: {url}")
    
    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", output_path,
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 下载失败: {result.stderr}")
        return None
    
    print(f"✅ 下载完成: {output_path}")
    return output_path

def transcribe(audio_path, language=None):
    """用 Whisper 转写"""
    print(f"🎤 开始转写: {audio_path}")
    
    model = whisper.load_model(MODEL_SIZE)
    result = model.transcribe(audio_path, language=language)
    
    print(f"✅ 转写完成，时长: {result['text'][:100]}...")
    return result

def main():
    if len(sys.argv) < 2:
        print("用法: python transcribe.py <video_url> [output_dir]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR
    
    # 生成视频ID
    video_id = url.split("/")[-1].split("?")[0][:20]
    video_dir = os.path.join(output_dir, video_id)
    os.makedirs(video_dir, exist_ok=True)
    
    audio_path = os.path.join(video_dir, "audio.mp3")
    
    # 1. 下载
    if not download_audio(url, audio_path):
        sys.exit(1)
    
    # 2. 转写
    result = transcribe(audio_path)
    
    # 3. 保存结果
    metadata = {
        "video_url": url,
        "language": result.get("language"),
        "duration": result.get("duration"),
    }
    
    with open(os.path.join(video_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(video_dir, "transcript.md"), "w", encoding="utf-8") as f:
        f.write(result["text"])
    
    print(f"✅ 已保存到: {video_dir}")

if __name__ == "__main__":
    main()
