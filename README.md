# code-dude

`code-dude` 是一个给 Codex 使用的通用工程自动化 skill，用来在具体仓库中围绕一个明确目标持续迭代：理解代码、直接修改实现、编译或运行、调用验证入口、记录实验与问题，并产出最终行动总结。

它适合这类场景：

- 修复某个 bug，直到验证通过
- 调整项目配置或实现，直到流程跑通
- 做性能或效果优化，直到达到目标指标
- 在本地、远程、容器或远程容器环境中执行同类任务

## 主要能力

- 用 `.code-dude/config.yaml` 统一描述目标、验证入口、环境和注意事项
- 在 `.code-dude/` 下维护场景建模、当前状态、未解决问题、经验记录和最终报告
- 检查验证脚本是否支持独立实验输出目录
- 汇总实验目录并给出清理建议
- 根据用户偏好调整执行方式，尤其记录用户明确禁止的操作

## 目录结构

```text
code-dude/
├── SKILL.md
├── README.md
├── agents/
├── assets/project-template/.code-dude/
├── references/
└── scripts/
```

项目初始化后，目标仓库中会出现：

```text
.code-dude/
├── config.yaml
├── current-status/
├── lessons/
├── reports/
├── scenario-models/
├── unresolved-issues/
└── user-profile/
```

## 初始化项目工作区

在目标仓库根目录执行：

```bash
python3 /path/to/code-dude/scripts/init_project.py --root .
```

然后填写 `.code-dude/config.yaml`，至少补充：

- `goal.summary`
- `goal.success_definition`
- `verification.entrypoint`
- `runtime.type`
- `attention_points`

## 使用方式

安装到 `~/.codex/skills/code-dude` 后，可以在和 Codex 的对话里直接提到：

```text
使用 $code-dude 处理这个仓库，目标写在 .code-dude/config.yaml 里。
```

典型流程是：

1. Codex 读取配置和仓库，建立场景理解
2. 直接修改相关代码并运行验证
3. 持续更新 `current-status`、`lessons` 和 `unresolved-issues`
4. 达成目标后生成简洁报告

## 辅助脚本

- `scripts/init_project.py`: 初始化项目侧 `.code-dude/`
- `scripts/check_verifier.py`: 检查验证入口是否支持隔离实验目录
- `scripts/manage_trials.py`: 汇总实验目录并给出清理建议
- `scripts/render_report.py`: 生成最终报告草稿

## 说明

`README.md` 面向人阅读，帮助快速理解这个 skill 是做什么的。

真正给 Codex 使用的行为规则在 `SKILL.md` 中。
