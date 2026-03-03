# Driving Test Notes - Project Instructions

## Project Context
Spanish driving licence (DGT) exam prep. User sends wrong/doubtful questions, Claude explains and archives them.

## Files
- `REVIEW.md` — master review doc, categorized by error type
- `wrong/NNN-slug.md` — detailed analysis per question
- `tmp-session.md` — temporary buffer during a session (local only, gitignored)
- `textbook.pdf` — local only, NOT in repo (copyright). Path: `/Users/qingtong/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_5danumxh2jpt21_367a/business/favorite/temp/英文版-中文翻译.pdf`

## Session Workflow

### Phase 1: Explain Mode (user is sending questions)
```
User sends screenshot → Explain immediately in chat → Append to tmp-session.md → Done, wait for next
```
- **NO committing, NO pushing during this phase**
- Save to `tmp-session.md` with a quick block (number + key points)
- Keep explanations concise, focus on why the answer is right/wrong
- If user says "我有疑问" (doubt, not necessarily wrong) → still explain + save

### Phase 2: Archive Mode (user says "存档" / "好了" / "全部发完了")
```
Read tmp-session.md → Create wrong/NNN files → Update REVIEW.md → Commit + Push → Delete tmp-session.md
```

## tmp-session.md Format
```markdown
## #NNN slug
**Q**: [question summary]
**Wrong**: [wrong answer] | **Correct**: [correct answer]
**Why**: [key explanation]
**Category**: [标志误读/英文理解/规则混淆/审题陷阱/程序顺序]
```

## REVIEW.md Categories
1. **一、标志图案误读类** — misread sign details or colors
2. **二、英文理解类** — English language traps, parse original text
3. **三、规则混淆类** — confused similar rules, incomplete rule knowledge
4. **四、审题陷阱类** — "ONLY/but/also" traps in options
5. **五、程序顺序类** — skipped mandatory intermediate steps

## wrong/NNN File Template
```markdown
# [Title]
## Question
## Options
- **A) ...** ✅ / ❌ (my answer)
## Correct Answer
## Why I Got It Wrong
## Key Rule
## Key Vocabulary
```

## Numbering
Next question number: check `ls wrong/` and increment. Current max: #012.

## Language
- Explanations: Chinese (中文)
- File names: English slugs
- Key English phrases: always quote original, then explain in Chinese
