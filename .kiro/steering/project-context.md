---
inclusion: always
---

# Daily UI Generator — Project Context

## คืออะไร
ระบบ auto-generate UI ใหม่ทุกวัน โดย Gemini AI คิด theme → Kiro สร้าง UI → Python push ขึ้น GitHub

## Workspace Structure
```
C:\Users\User\Documents\GitHub\Axon\
├── x-template\              ← repo หลัก (push GitHub ได้)
│   ├── src\                 ← Kiro แก้ไขไฟล์เหล่านี้ทุกวัน
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.css
│   ├── scripts\
│   │   ├── PLAN.md              ← แผนฉบับสมบูรณ์ อ่านถ้าต้องการรายละเอียด
│   │   ├── daily-context.json   ← INPUT: Kiro อ่านจากนี้เพื่อสร้าง UI
│   │   └── build-done.flag      ← OUTPUT: Kiro เขียนเมื่อ build สำเร็จ
│   └── .kiro\hooks\
│       ├── on-context-ready.json   ← Hook 1
│       └── on-build-done.json      ← Hook 2
│
└── ui-generator-tools\      ← Python scripts (ไม่ push GitHub เด็ดขาด — มี API keys)
    ├── generate_context.py  ← Python 1: เรียก Gemini → เขียน daily-context.json
    ├── push_to_github.py    ← Python 2: push ไฟล์ขึ้น GitHub ผ่าน REST API
    ├── theme-history.json   ← ประวัติ theme ที่ใช้ไปแล้ว
    └── .env                 ← GEMINI_API_KEY, GITHUB_PAT (ห้าม commit)
```

## Flow ทุกวัน
```
Task Scheduler
  → generate_context.py
      1. git clone x-template → x-template-NNN (ต้นฉบับไม่แตะ)
      2. Gemini สุ่ม theme → เขียน x-template-NNN/scripts/daily-context.json
          ↓ Kiro Hook: on-context-ready (fileCreated)
  → Kiro อ่าน context → สร้าง UI ใหม่ใน x-template-NNN → pnpm build → build-done.flag
          ↓ Kiro Hook: on-build-done (fileCreated)
  → push_to_github.py
      1. สร้าง GitHub repo ใหม่ชื่อ x-template-NNN
      2. git init + push ทั้ง folder
      3. Enable GitHub Pages
      → GitHub Actions deploy อัตโนมัติ
```

## สำคัญ: x-template คือต้นฉบับ ห้ามแก้ไข
- Kiro แก้ไข UI ใน **x-template-NNN** เท่านั้น ไม่ใช่ x-template
- ทุก repo ใหม่ clone มาจาก x-template เป็น base
- ชื่อ repo: `x-template-001`, `x-template-002`, ...

## หน้าที่ของ Kiro ในระบบนี้
เมื่อ Hook `on-context-ready` trigger (daily-context.json เปลี่ยน) ให้:
1. อ่าน `scripts/daily-context.json`
2. สร้าง UI ใหม่ทั้งหมดใน `src/App.tsx`, `src/App.css`, `src/index.css`
3. อัปเดต version ใน `package.json` ตามที่ JSON กำหนด
4. รัน `pnpm build`
5. ถ้า build สำเร็จ → เขียน `scripts/build-done.flag`

## daily-context.json Schema
```json
{
  "day": 1,
  "date": "YYYY-MM-DD",
  "version": "1.0.0",
  "theme": { "name": "...", "style": "...", "mood": "..." },
  "palette": {
    "background": "#hex", "surface": "#hex", "primary": "#hex",
    "accent": "#hex", "text": "#hex", "muted": "#hex"
  },
  "typography": { "heading": "font", "body": "font", "size": "small|medium|large" },
  "layout": { "structure": "centered|asymmetric|grid|split", "density": "...", "border_style": "..." },
  "animation": { "level": "none|minimal|moderate|high", "style": "..." },
  "components": {
    "hero_text": "MAIN HEADING",
    "subtitle": "subtitle text",
    "button_label": "button text",
    "badge_text": "badge text"
  },
  "commit_message": "feat: UI Day N — Theme Name"
}
```

## GitHub Repo
- Owner: `Ex2-Axon`
- Repo: `x-template`
- Live: https://ex2-axon.github.io/x-template/
- Branch: `main`

## GitHub Actions (trigger อัตโนมัติเมื่อ push)
- `deploy.yml` → Build + Deploy to GitHub Pages
- `discord-notify.yml` → แจ้ง Discord
- `bluesky-notify.yml` → โพสต์ Bluesky
- `screenshot.yml` → Screenshot + commit รูป + แจ้ง Discord + Bluesky
- ~~`x-notify.yml`~~ → ตัดออกแล้ว

## Stack
- React 19 + TypeScript + Vite 8
- Tailwind CSS 4 (ติดตั้งแล้ว แต่ใช้ CSS ปกติก็ได้)
- pnpm (package manager)
- Google Fonts ผ่าน @import ใน index.css

## สิ่งที่ต้องรู้เพิ่มเติม
- อ่าน `scripts/PLAN.md` สำหรับรายละเอียดทั้งหมด
- อ่าน `ui-generator-tools/generate_context.py` สำหรับ Gemini prompt logic
- อ่าน `ui-generator-tools/push_to_github.py` สำหรับ GitHub API logic
