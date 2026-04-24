# code-dude

`code-dude` 是一个给 Codex 使用的通用工程自动化 skill，用来在具体仓库中围绕一个明确目标持续迭代：理解代码、直接修改实现、编译或运行、调用验证入口、记录实验与问题，并产出最终行动总结。

它适合这类场景：

- 修复某个 bug，直到验证通过
- 调整项目配置或实现，直到流程跑通
- 做性能或效果优化，直到达到目标指标
- 在本地、远程、容器或远程容器环境中执行同类任务

## 主要能力

- 用任务目录内的 `config.yaml` 描述该任务的目标、验证入口、环境和注意事项
- 在 `.code-dude/` 下区分共享信息与任务工作区，避免多任务时互相污染
- 在根目录长期积累仓库级共享信息，而不是把这类信息混进单个任务记录里
- 检查验证脚本是否支持独立实验输出目录
- 汇总实验目录并给出清理建议
- 根据用户偏好调整执行方式，尤其记录用户明确禁止的操作

## 目录结构

```text
code-dude/
├── SKILL.md
├── README.md
├── agents/
├── references/
└── scripts/
```

项目初始化后，目标仓库中会出现：

```text
.code-dude/
├── lessons/
│   └── .gitkeep
├── project-notes/
│   └── .gitkeep
├── tasks/
│   ├── .gitkeep
│   ├── .task-config-template.yaml
│   └── <task-id>/
│       ├── config.yaml
│       ├── current-status.md
│       ├── reports/
│       ├── scenario-model.md
│       └── unresolved-issues.md
└── user-profile.md
```

任务完成并得到用户明确确认后，对应目录应重命名为 `tasks/<task-id>_done/`。

## 初始化项目工作区

在目标仓库根目录执行：

```bash
python3 /path/to/code-dude/scripts/init_project.py --root .
```

该脚本会直接创建目录结构并写入默认占位文件，不再依赖仓库内的模板目录。

然后创建任务目录并写入真实任务文件初始内容：

```bash
python3 /path/to/code-dude/scripts/init_task.py --root . --task-id 20260424_fix_login_bug
```

再填写 `.code-dude/tasks/<task-id>/config.yaml`，至少补充：

- `goal.summary`
- `goal.success_definition`
- `verification.entrypoint`
- `runtime.type`
- `attention_points`

## 使用方式

安装到 `~/.codex/skills/code-dude` 后，可以在和 Codex 的对话里直接提到：

```text
使用 $code-dude 处理这个仓库，目标写在当前任务目录的 config.yaml 里。
```

典型流程是：

1. Codex 读取配置和仓库，确定或创建当前任务目录并建立场景理解
2. 直接修改相关代码并运行验证
3. 持续更新当前任务目录下的 `current-status.md` 和 `unresolved-issues.md`，并把经验教训沉淀到根目录的 `lessons/`，把仓库背景信息沉淀到 `project-notes/`
4. 达成目标后生成简洁报告，并在用户明确确认完成时把任务目录重命名为 `<task-id>_done`

## 辅助脚本

- `scripts/init_project.py`: 初始化项目侧 `.code-dude/`
- `scripts/init_task.py`: 初始化某个任务工作区及其实际 markdown 文件
- `scripts/check_verifier.py`: 检查验证入口是否支持隔离实验目录
- `scripts/manage_trials.py`: 汇总实验目录并给出清理建议
- `scripts/render_report.py`: 生成最终报告草稿

## 说明

`README.md` 面向人阅读，帮助快速理解这个 skill 是做什么的。

真正给 Codex 使用的行为规则在 `SKILL.md` 中。
