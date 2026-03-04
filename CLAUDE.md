# Driving Test Notes - Project Instructions

## Project Context
Spanish driving licence (DGT) exam prep. User sends wrong/doubtful questions, Claude explains and archives them.

## Detailed Guides
- `docs/AGENT_GUIDE.md` — 完整 Agent 行为规范（查询、解释、归档的详细流程）
- `docs/USAGE.md` — 项目完整使用说明

## Files
- `REVIEW.md` — master review doc, categorized by error type
- `PROGRESS.md` — mock test progress tracking (error counts, trends per category)
- `wrong/NNN-slug.md` — detailed analysis per question
- `tmp-session.md` — temporary buffer during a session (local only, gitignored)
- `textbook_kb/` — 本地知识库（SQLite FTS + 章节 Markdown + 页面图片）
- `scripts/query_textbook_kb.py` — 知识库查询工具
- `scripts/pass_probability.py` — 通过概率统计工具

## Textbook KB Query（核心）

**绝对不要直接读 PDF。** 先查知识库，再只打开命中的页。

### 查规则文字
```bash
cd /Users/qingtong/project/drive/driving-test-notes
python3 scripts/query_textbook_kb.py \
  --db ./textbook_kb/textbook.sqlite \
  --query 'KEYWORD' \
  --limit 5
```

### 查询词选取
- 规则名：`酒精测试`、`right of way`
- 图示主题：`路标`、`地面标线`
- 动作/现象：`overtaking`、`雨天 刹车距离`
- 章节关键词：`lighting`、`speed`

### 何时开图页
文字命中后，以下情况还要打开对应 `page_images/*.jpg`：
- 路标、地面标线、车道箭头
- 灯光图、仪表图
- 题目本身依赖图形细节

查询结果会输出图片绝对路径，直接 Read 该 JPG 即可。

## Source Priority
1. 用户当前发来的题目、截图、上下文
2. `textbook_kb/textbook.sqlite`（查规则文字）
3. `textbook_kb/page_images/*.jpg`（查图页）
4. `REVIEW.md`（已总结的误区）
5. `wrong/*.md`（旧题详细解释）
6. `PROGRESS.md`（仅 mock test 场景）

## Session Workflow

### Phase 1: Explain Mode (user is sending questions)
```
User sends screenshot → 查 KB 取证 → Explain immediately in chat → Append to tmp-session.md → Done, wait for next
```
- **NO committing, NO pushing during this phase**
- Save to `tmp-session.md` with a quick block (number + key points)
- Keep explanations concise, focus on why the answer is right/wrong
- If user says "我有疑问" (doubt, not necessarily wrong) → still explain + save

### Phase 2: Archive Mode (user says "存档" / "好了" / "全部发完了")
```
Read tmp-session.md → Create wrong/NNN files → Update REVIEW.md → Update PROGRESS.md → Run stats → Commit + Push → Delete tmp-session.md
```
- **Stats step**: If this session was a mock test, update `TEST_ERRORS` in `scripts/pass_probability.py` with the error count, then run `python3 scripts/pass_probability.py` and show results to user

### Progress Tracking (PROGRESS.md)
Each mock test session gets a row in the summary table:
- Date, total wrong count, breakdown by category
- Compare with previous sessions to identify trends
- Categories: 标志误读 | 英文理解 | 规则混淆 | 审题陷阱 | 程序顺序 | 数字记忆
- Note improvements (category errors decreasing) and persistent weaknesses

## Explain Answer Structure

1. 先给结论（正确答案是 X）
2. 再说为什么正确（引用教材规则原文）
3. 再说为什么其他理解容易错
4. 必要时补一个记忆点

风格：中文解释为主 | 关键英文原文要引用 | 解释短，重点清楚 | 不要大段抄教材

## tmp-session.md Format
```markdown
## #NNN slug
**Q**: [question summary]
**Wrong**: [wrong answer] | **Correct**: [correct answer]
**Why**: [key explanation]
**Category**: [标志误读/英文理解/规则混淆/审题陷阱/程序顺序/数字记忆]
```

## REVIEW.md Categories
1. **一、标志图案误读类** — misread sign details or colors
2. **二、英文理解类** — English language traps, parse original text
3. **三、规则混淆类** — confused similar rules, incomplete rule knowledge
4. **四、审题陷阱类** — "ONLY/but/also" traps in options, ignored qualifiers
5. **五、程序顺序类** — skipped mandatory intermediate steps
6. **六、数字记忆类** — pure number/date memory, no logic to derive

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
Next question number: check `ls wrong/` and increment. Current max: #025.

## Language
- Explanations: Chinese (中文)
- File names: English slugs
- Key English phrases: always quote original, then explain in Chinese

## Key Rules (DO NOT)
- 不要直接读 PDF → 先查 `textbook_kb`
- 不要在 Explain Mode 提前 commit / push
- 不要把散题当成 mock test 记入 PROGRESS.md 和 TEST_ERRORS
- 不要只凭 REVIEW.md 回答规则原文题 → 查 KB 取证
- 不要遇到图示题只看文字不看图 → 查完文字再开图页
- 不要改掉用户已有的错题编号体系
- 不要一题一 commit → Phase 2 统一归档
