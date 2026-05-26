# Domain Docs

工程类技能在探索代码库时，应如何消费本仓库的领域文档。

## 探索前先阅读这些

- **`CONTEXT.md`**（仓库根目录），或者
- **`CONTEXT-MAP.md`**（仓库根目录）— 如果存在，它指向每个上下文的 `CONTEXT.md`。阅读与当前主题相关的每一个。
- **`docs/adr/`** — 阅读涉及你即将工作的领域的 ADR。多上下文仓库中，还需检查 `src/<context>/docs/adr/` 中的上下文级决策。

如果上述任何文件不存在，**静默跳过**。不要提醒用户缺失，不要主动建议创建。生产者技能（`/grill-with-docs`）会在术语或决策实际确定时惰性创建它们。

## 文件结构

单上下文仓库（大多数仓库）：

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文仓库（根目录存在 `CONTEXT-MAP.md` 时）：

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← 上下文级决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用术语表中的词汇

当你的输出涉及领域概念（问题标题、重构建议、假设、测试名称），请使用 `CONTEXT.md` 中定义的术语。不要漂移到术语表明确避免的同义词。

如果你需要的概念尚未出现在术语表中，这是一个信号 — 要么你在发明项目不使用的语言（重新考虑），要么确实存在空白（记录给 `/grill-with-docs`）。

## 标记 ADR 冲突

如果你的输出与现有 ADR 矛盾，请明确指出而非静默覆盖：

> _与 ADR-0007（事件溯源订单）矛盾 — 但值得重新讨论，因为…_
