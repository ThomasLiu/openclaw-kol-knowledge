#!/usr/bin/env python3
"""
OpenClaw KOL 任务队列系统 (本地版)
==========================
耗时的任务放入队列，后台逐个执行，不阻塞主流程

队列文件: ~/.openclaw/workspace/kol-task-queue.json

任务类型:
- download: 下载视频
- transcribe: 转写音频
- translate: 翻译内容
- analyze: 分析内容

队列状态:
- pending: 待处理
- running: 执行中
- completed: 已完成
- failed: 失败
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from enum import Enum

# ==================== 配置 ====================
QUEUE_FILE = os.path.expanduser("~/.openclaw/workspace/kol-task-queue.json")
GITHUB_DIR = os.path.expanduser("~/openclaw-kol-knowledge")

# ==================== 任务队列 ====================
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(Enum):
    DOWNLOAD = "download"
    TRANSCRIBE = "transcribe"
    TRANSLATE = "translate"
    ANALYZE = "analyze"

def load_queue():
    """加载任务队列"""
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return {"tasks": []}

def save_queue(queue):
    """保存任务队列"""
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def add_task(name, task_type, priority="中", metadata=None):
    """添加任务"""
    queue = load_queue()
    
    task = {
        "id": f"task_{len(queue['tasks']) + 1}_{int(datetime.now().timestamp())}",
        "name": name,
        "type": task_type,
        "priority": priority,
        "status": TaskStatus.PENDING.value,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "result": None
    }
    
    queue["tasks"].append(task)
    save_queue(queue)
    
    print(f"✅ 任务已添加: {name} ({task_type})")
    return task["id"]

def get_next_task():
    """获取下一个待处理任务"""
    queue = load_queue()
    
    # 按优先级和创建时间排序
    priority_order = {"高": 0, "中": 1, "低": 2}
    
    pending_tasks = [
        t for t in queue["tasks"] 
        if t["status"] == TaskStatus.PENDING.value
    ]
    
    if not pending_tasks:
        return None
    
    # 按优先级排序
    pending_tasks.sort(key=lambda x: (
        priority_order.get(x["priority"], 1),
        x["created_at"]
    ))
    
    return pending_tasks[0]

def update_task(task_id, status, result=None):
    """更新任务状态"""
    queue = load_queue()
    
    for task in queue["tasks"]:
        if task["id"] == task_id:
            task["status"] = status.value if isinstance(status, TaskStatus) else status
            
            if status == TaskStatus.RUNNING:
                task["started_at"] = datetime.now().isoformat()
            elif status == TaskStatus.COMPLETED or status == TaskStatus.FAILED:
                task["completed_at"] = datetime.now().isoformat()
                task["result"] = result
            
            break
    
    save_queue(queue)

def list_tasks(status=None):
    """列出任务"""
    queue = load_queue()
    
    if status:
        tasks = [t for t in queue["tasks"] if t["status"] == status]
    else:
        tasks = queue["tasks"]
    
    return tasks

# ==================== Worker ====================
def run_worker():
    """Worker 主循环"""
    print("=" * 50)
    print("🚀 KOL 任务队列 Worker 启动")
    print("=" * 50)
    
    while True:
        # 获取下一个任务
        task = get_next_task()
        
        if not task:
            print("📭 没有待处理任务，退出")
            break
        
        task_id = task["id"]
        task_name = task["name"]
        task_type = task["type"]
        
        print(f"\n📥 获取任务: {task_name} ({task_type})")
        
        # 更新状态为执行中
        update_task(task_id, TaskStatus.RUNNING)
        
        # 执行任务
        success = False
        result = None
        
        try:
            if task_type == TaskType.DOWNLOAD.value:
                success, result = execute_download(task)
            elif task_type == TaskType.TRANSCRIBE.value:
                success, result = execute_transcribe(task)
            elif task_type == TaskType.TRANSLATE.value:
                success, result = execute_translate(task)
            elif task_type == TaskType.ANALYZE.value:
                success, result = execute_analyze(task)
            else:
                print(f"❌ 未知任务类型: {task_type}")
                success = False
                result = "未知任务类型"
        except Exception as e:
            print(f"❌ 执行出错: {e}")
            success = False
            result = str(e)
        
        # 更新任务状态
        if success:
            update_task(task_id, TaskStatus.COMPLETED, result)
            print(f"✅ 任务完成: {task_name}")
        else:
            update_task(task_id, TaskStatus.FAILED, result)
            print(f"❌ 任务失败: {task_name}")
    
    print("\n👋 Worker 退出")

# ==================== 任务执行器 ====================
def execute_download(task):
    """执行下载任务"""
    print("  📥 开始下载视频...")
    metadata = task.get("metadata", {})
    video_url = metadata.get("url", "")
    platform = metadata.get("platform", "youtube")
    
    if not video_url:
        return False, "缺少视频 URL"
    
    # TODO: 实现下载逻辑
    return True, f"下载完成: {video_url}"

def execute_transcribe(task):
    """执行转写任务"""
    print("  🎤 开始转写音频...")
    metadata = task.get("metadata", {})
    video_id = metadata.get("video_id", "")
    
    if not video_id:
        return False, "缺少视频 ID"
    
    # 调用 Whisper 转写
    audio_path = f"{GITHUB_DIR}/data/youtube/{video_id}/audio.mp3"
    
    if not os.path.exists(audio_path):
        return False, f"音频文件不存在: {audio_path}"
    
    # 转写
    cmd = f'''
export KMP_DUPLICATE_LIB_OK=TRUE
source /usr/local/Caskroom/miniconda/base/etc/profile.d/conda.sh && conda activate whisper && python3 -c "
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from faster_whisper import WhisperModel
model = WhisperModel('base', device='cpu', compute_type='int8')
segments, info = model.transcribe('{audio_path}')
text = ''
for segment in segments:
    text += segment.text + ' '
with open('{GITHUB_DIR}/data/youtube/{video_id}/transcript.txt', 'w') as f:
    f.write(text)
print('Done')
"
'''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        return True, f"转写完成: {video_id}"
    else:
        return False, result.stderr[:200]

def execute_translate(task):
    """执行翻译任务"""
    print("  🌐 开始翻译...")
    # TODO: 实现翻译逻辑
    return True, "翻译完成"

def execute_analyze(task):
    """执行分析任务"""
    print("  📝 开始分析...")
    # TODO: 实现分析逻辑
    return True, "分析完成"

# ==================== 主入口 ====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KOL 任务队列")
    parser.add_argument("action", choices=["add", "worker", "list", "status"], help="操作类型")
    parser.add_argument("--name", help="任务名称")
    parser.add_argument("--type", help="任务类型: download/transcribe/translate/analyze")
    parser.add_argument("--priority", default="中", help="优先级: 高/中/低")
    parser.add_argument("--url", help="视频URL (download)")
    parser.add_argument("--video-id", help="视频ID (transcribe)")
    
    args = parser.parse_args()
    
    if args.action == "add":
        if not args.name or not args.type:
            print("用法:")
            print("  添加下载任务: task_queue.py add --name <名称> --type download --url <URL>")
            print("  添加转写任务: task_queue.py add --名称> --type transcribe --video-id <ID>")
            sys.exit(1)
        
        metadata = {}
        if args.url:
            metadata["url"] = args.url
        if args.video_id:
            metadata["video_id"] = args.video_id
        
        add_task(args.name, args.type, args.priority, metadata)
    
    elif args.action == "worker":
        run_worker()
    
    elif args.action == "list":
        tasks = list_tasks()
        print(f"任务列表 (共 {len(tasks)} 个):")
        for t in tasks:
            print(f"  [{t['status']}] {t['name']} ({t['type']}) - {t['priority']}优先级")
    
    elif args.action == "status":
        queue = load_queue()
        pending = len([t for t in queue["tasks"] if t["status"] == "pending"])
        running = len([t for t in queue["tasks"] if t["status"] == "running"])
        completed = len([t for t in queue["tasks"] if t["status"] == "completed"])
        failed = len([t for t in queue["tasks"] if t["status"] == "failed"])
        
        print(f"队列状态:")
        print(f"  ⏳ 待处理: {pending}")
        print(f"  🔄 执行中: {running}")
        print(f"  ✅ 已完成: {completed}")
        print(f"  ❌ 失败: {failed}")
