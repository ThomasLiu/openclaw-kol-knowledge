# OpenClaw KOL 知识库

> 收录 OpenClaw 相关的优质内容，自动转写、分析、打标签

## 数据结构

```
data/
├── youtube/
│   └── [视频ID]/
│       ├── metadata.json      # 元数据（标题、播放量、链接等）
│       ├── transcript.md      # 原始转写
│       ├── transcript_zh.md   # 中文翻译（仅外语）
│       ├── analysis.md        # 分析总结
│       └── tags.json          # 标签
└── bilibili/
    └── [视频ID]/
        └── ...
```

## 收录规则

- **来源**: YouTube、Bilibili
- **筛选**: 播放量 > 5000
- **内容**: 与 OpenClaw、AI Agent 相关

## 更新频率

每 4 小时自动更新

## 技术栈

- 搜索: yt-dlp + agent-browser
- 转写: Whisper
- 翻译: MiniMax API
- 存储: Notion + GitHub
