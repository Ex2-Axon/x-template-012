# Daily UI Automation — Master Plan

> แผนฉบับสมบูรณ์สำหรับระบบ auto-generate UI ทุกวัน
> เขียนไว้เพื่อให้ต่อได้ทุกเมื่อ แม้ token หมดกลางคัน

---

## ภาพรวม Flow

```
[Task Scheduler] ทุกวัน เวลาที่กำหนด
        ↓
[Python 1: generate_context.py]
  1. หา day number ถัดไปจาก theme-history.json
  2. git clone Ex2-Axon/x-template → x-template-NNN  (ต้นฉบับ ไม่แตะ)
  3. ลบ .git ของต้นฉบับออก
  4. เรียก Gemini API → generate context JSON
  5. เขียน x-template-NNN/scripts/daily-context.json
        ↓ (Kiro Hook: fileCreated → scripts/daily-context.json)
[Kiro: อ่าน context → สร้าง UI ใน x-template-NNN]
  - แก้ไข src/App.tsx
  - แก้ไข src/App.css
  - แก้ไข src/index.css
  - อัปเดต package.json version
  - รัน: pnpm build
  - เขียน scripts/build-done.flag (เมื่อ build สำเร็จ)
        ↓ (Kiro Hook: fileCreated → build-done.flag)
[Python 2: push_to_github.py]
  1. สร้าง GitHub repo ใหม่ชื่อ x-template-NNN ใต้ Ex2-Axon
  2. git init → git add → git commit → git push
  3. Enable GitHub Pages
  4. ลบ build-done.flag
        ↓ (GitHub Actions trigger อัตโนมัติ)
[GitHub Actions ใน repo ใหม่]
  - deploy.yml       → build + deploy to GitHub Pages
  - discord-notify   → แจ้ง Discord
  - bluesky-notify   → โพสต์ Bluesky
  - screenshot.yml   → screenshot + commit รูป + แจ้ง Discord + Bluesky
```

## ต้นฉบับ x-template
- **ไม่แตะเลย** — ใช้เป็น base template อย่างเดียว
- ทุก repo ใหม่ clone มาจากนี้
- ชื่อ repo ใหม่: `x-template-001`, `x-template-002`, ...

---

## โครงสร้างไฟล์ที่จะสร้าง

> **หมายเหตุ:** Python scripts อยู่แยก repo ต่างหาก ไม่ push GitHub เด็ดขาด

```
C:\Users\User\Documents\GitHub\Axon\
│
├── x-template\                     ← repo หลัก (push GitHub)
│   ├── scripts\
│   │   ├── PLAN.md                 ← ไฟล์นี้
│   │   ├── daily-context.json      ← Python 1 เขียนมาที่นี่ / Kiro อ่าน
│   │   └── build-done.flag         ← Kiro เขียนเมื่อ build สำเร็จ
│   ├── .kiro\
│   │   └── hooks\
│   │       ├── on-context-ready.json   ← Hook 1
│   │       └── on-build-done.json      ← Hook 2
│   └── src\ ...
│
└── ui-generator-tools\             ← Python workspace (ไม่ push ไหนเลย)
    ├── x-template.code-workspace
    ├── generate_context.py         ← Python 1
    ├── push_to_github.py           ← Python 2
    ├── theme-history.json          ← บันทึก theme ที่ใช้ไปแล้ว
    └── .env                        ← API keys ทั้งหมด (ปลอดภัย)
```

---

## รายละเอียด daily-context.json (Format ที่ Gemini ต้องสร้าง)

```json
{
  "day": 1,
  "date": "2026-05-29",
  "version": "1.0.0",
  "theme": {
    "name": "Brutalist Terminal",
    "style": "brutalist",
    "mood": "raw, aggressive, monochrome"
  },
  "palette": {
    "background": "#0a0a0a",
    "surface": "#111111",
    "primary": "#ffffff",
    "accent": "#ff3300",
    "text": "#cccccc",
    "muted": "#444444"
  },
  "typography": {
    "heading": "monospace",
    "body": "sans-serif",
    "size": "large"
  },
  "layout": {
    "structure": "centered",
    "density": "spacious",
    "border_style": "thick solid"
  },
  "animation": {
    "level": "minimal",
    "style": "none"
  },
  "components": {
    "hero_text": "INITIALIZE",
    "subtitle": "System ready. Awaiting input.",
    "button_label": "EXECUTE",
    "badge_text": "TERMINAL v1.0"
  },
  "commit_message": "feat: UI Day 1 — Brutalist Terminal"
}
```

---

## Python 1: generate_context.py

### Dependencies
```
pip install google-genai python-dotenv
```

### API ที่ใช้
- **Google GenAI SDK (ใหม่)**: `pip install google-genai`
- Import: `from google import genai`
- Client: `client = genai.Client(api_key=GEMINI_API_KEY)`
- Call: `client.models.generate_content(model="gemini-2.0-flash", contents=prompt)`

### Logic
1. โหลด `theme-history.json` (list ของ theme ที่ใช้ไปแล้ว)
2. สร้าง prompt ส่งให้ Gemini พร้อม previous themes
3. Gemini return JSON ตาม schema ด้านบน
4. validate JSON
5. เขียนลง `scripts/daily-context.json`
6. append theme name ลง `theme-history.json`

### Prompt Template สำหรับ Gemini
```
You are a creative UI designer. Generate a daily UI theme for a Vite + React template.

Rules:
- Must be completely different from previous themes
- Rotate through: brutalist, glassmorphism, neumorphism, retro-terminal, 
  vaporwave, minimal, material, bento-grid, swiss-design, dark-luxury, 
  neon-noir, paper-organic, aurora, cyberpunk, art-deco, memphis, 
  bauhaus, y2k, solarpunk, cottagecore-dark

Previous themes used: {previous_themes}
Day number: {day}
Today's date: {date}

Output ONLY valid JSON. No explanation. No markdown. No code blocks.
Use this exact schema: {schema}
```

---

## Python 2: push_to_github.py

### Dependencies
```
pip install requests python-dotenv
```

### API ที่ใช้: GitHub REST API v3

#### วิธีทำงาน (ใช้ GitHub API แทน git CLI)
เหตุผล: ไม่ต้องพึ่ง git credentials บนเครื่อง, ควบคุมได้ดีกว่า

#### Step 1: GET SHA ของไฟล์ที่จะอัปเดต
```
GET https://api.github.com/repos/{owner}/{repo}/contents/{path}
Headers:
  Authorization: Bearer {GITHUB_PAT}
  X-GitHub-Api-Version: 2022-11-28
Response: { "sha": "abc123...", "content": "base64..." }
```

#### Step 2: PUT อัปเดตไฟล์
```
PUT https://api.github.com/repos/{owner}/{repo}/contents/{path}
Headers:
  Authorization: Bearer {GITHUB_PAT}
  Content-Type: application/json
Body:
{
  "message": "feat: UI Day 1 — Brutalist Terminal",
  "content": "<base64 encoded file content>",
  "sha": "<sha จาก step 1>"
}
```

#### ไฟล์ที่ต้อง push
1. `src/App.tsx` — UI ใหม่จาก Kiro
2. `src/App.css` — CSS ใหม่จาก Kiro
3. `src/index.css` — CSS variables ใหม่
4. `package.json` — version ใหม่
5. `README.md` — อัปเดต screenshot badge + version

#### README Update Logic
- แทนที่ `![Screenshot](screenshot.png)` ด้วย URL รูปล่าสุดจาก `.github/screenshots/latest.png`
- อัปเดต version badge
- อัปเดต theme name ใน description

### GitHub PAT ที่ต้องการ
- Scope: `repo` (read/write contents)
- สร้างที่: GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
- Permissions ที่ต้องการ:
  - `Contents: Read and write`
  - `Metadata: Read`

---

## Kiro Hooks ที่ต้องสร้าง

### Hook 1: on-context-ready
```json
{
  "name": "Daily UI Context Ready",
  "version": "1.0.0",
  "description": "เมื่อ Python 1 เขียน daily-context.json เสร็จ ให้ Kiro สร้าง UI",
  "when": {
    "type": "fileEdited",
    "patterns": ["scripts/daily-context.json"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Read scripts/daily-context.json and create a completely new UI based on the theme specification. Update src/App.tsx, src/App.css, and src/index.css. Then run pnpm build. If build succeeds, write the text 'done' to scripts/build-done.flag"
  }
}
```

### Hook 2: on-build-done
```json
{
  "name": "Build Done — Trigger Push",
  "version": "1.0.0",
  "description": "เมื่อ Kiro build เสร็จ ให้รัน Python 2",
  "when": {
    "type": "fileCreated",
    "patterns": ["scripts/build-done.flag"]
  },
  "then": {
    "type": "runCommand",
    "command": "python scripts/push_to_github.py"
  }
}
```

---

## GitHub Actions Workflows (ที่จะมี)

| Workflow | Trigger | Action |
|---|---|---|
| `deploy.yml` | push to main | Build + Deploy to GitHub Pages |
| `discord-notify.yml` | push to main | แจ้ง Discord |
| `bluesky-notify.yml` | push to main | โพสต์ Bluesky |
| `screenshot.yml` | หลัง deploy สำเร็จ | Screenshot + commit รูป + แจ้ง Discord + Bluesky |
| ~~`x-notify.yml`~~ | ~~push to main~~ | **ตัดออก** |

---

## .env ที่ต้องการ (scripts/.env)

```env
# Gemini API (Python 1)
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub API (Python 2)
GITHUB_PAT=your_personal_access_token_here
GITHUB_OWNER=Ex2-Axon
GITHUB_REPO=x-template
GITHUB_BRANCH=main

# Git commit identity
GIT_AUTHOR_NAME=Axon Bot
GIT_AUTHOR_EMAIL=bot@axon.dev
```

---

## Windows Task Scheduler Setup

```
Task name: DailyUIGenerator
Trigger: Daily at 09:00
Action: Run program
  Program: python
  Arguments: scripts/generate_context.py
  Start in: C:\Users\User\Documents\GitHub\Axon\x-template
```

---

## สถานะการสร้าง (Checklist)

- [ ] `scripts/generate_context.py` — Python 1
- [ ] `scripts/push_to_github.py` — Python 2
- [ ] `scripts/theme-history.json` — ประวัติ theme
- [ ] `scripts/daily-context.json` — template เริ่มต้น
- [ ] `.kiro/hooks/on-context-ready.json` — Hook 1
- [ ] `.kiro/hooks/on-build-done.json` — Hook 2
- [ ] ลบ `.github/workflows/x-notify.yml`
- [ ] อัปเดต `README.md`
- [ ] Task Scheduler config (manual step)
- [ ] สร้าง GitHub PAT (manual step)
- [ ] ใส่ API keys ใน `scripts/.env` (manual step)

---

## API Keys ที่ต้องขอจากคุณ

เมื่อพร้อมจะ implement ต้องการ:

1. **GEMINI_API_KEY** — จาก Google AI Studio
2. **GITHUB_PAT** — Personal Access Token (scope: repo → contents read/write)
   - สร้างที่: https://github.com/settings/tokens

ไม่ต้องให้ตอนนี้ ใส่ใน `scripts/.env` เองได้เลยตอน implement

---

*แผนนี้เขียนเมื่อ 2026-05-29 — ต่อได้ทุกเมื่อจากไฟล์นี้*
