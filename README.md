# z-cicd-delivery

**让 AI 把 CI/CD 从“脚本能执行”推进到“发布状态可确认、验收证据可追溯”。** 面向维护流水线的开发者、测试与运维人员，提供设计、实施、故障诊断、发布恢复和复盘方法。

## 背景：为什么做这个 Skill

它源于一次真实多服务 Kubernetes 项目的交付实践：从运维配置手册与逐项问题复盘中，重新提炼可迁移的判断。接入共享 Runner 后，问题并不只在 YAML：干净 checkout 缺构建产物、测试依赖主机数据、executor 的数据库差异、SDK 时间预算、数据库行锁与租约、SSH 流尾截断、部署确认丢失和验收路径都曾需要分别处理。

反复重跑完整流水线会放大等待，却未必提供区分根因的证据。因此这个 Skill 优先教 Agent：**先确认失败阶段与外部副作用，再做最小实验和修复，最后对同一候选验收。**

本仓库全部重新编写为通用方法、合成案例和独立安装器；不包含原公司项目代码、原始日志、内部域名、主机地址、用户数据或凭据。案例中的 sample-service、r42 和 image-v1/v2 均为虚构标记。

## 解决了什么问题

| 常见做法 | Skill 要改变的决定 |
| --- | --- |
| job红了就重发、重建或回滚 | 先区分未执行、未知、部分更新、已更新未验收 |
| 本机能跑就上完整CI | 先验证clean checkout、fixture和Runner实际能力 |
| 遇到网络超时就延长或关TLS | 分层验证路由、认证、TLS、字节完整性与背压 |
| 测试偶发失败就加sleep、加TTL | 用语义事件与可控延迟／行锁复现，区分产品与测试缺陷 |
| 改URL/context就算换部署目标 | 明确变量、受控脚本、Secret、调度和基础设施配置各层 |
| 复盘只展示最后成功方案 | 保留第一次处理、为何不足、对照实验、未决与适用条件 |

它不是现成的部署平台，不附带生产Key，不固定要求GitLab、Kubernetes或某个云厂商，也不保证自动修复所有发布问题。稳定私网Runner能直连时，不要求增加SSH中继。

## 成果展示

代表性合成案例：deploy在更新api后断连，api已v2，worker/admin仍v1；入口验收没跑，兼容性未确认。

完整输入：[partial-release-input.md](examples/partial-release-input.md)；实际成果：[partial-release-review.md](examples/partial-release-review.md)。2026-10-27 使用 Codex CLI 0.162.1，在临时 HOME 安装并按技能名加载，实际输出节选如下：

> r42 属于“部分目标已更新、尚未完成验收”。`watch_timeout` 表明部署确认过程失败，不能据此判定更新未发生；现有快照已证明 api 更新到了 image-v2。

该产物逐项区分 api 新版、worker/admin 旧版，先要求兼容性和原发布身份对账，再给有条件的继续／回退方案；没有把 readiness 503 或页面 30/30 外推成业务与高可用结论。展示来自合成输入的真实客户端执行，不是生产发布证明，也不是无 Skill 对照基准。

## 安装

需要 Git、Python 3，以及支持本地Agent Skills的客户端。已按[官方 Codex 技能文档](https://developers.openai.com/codex/skills/)核对用户级路径 `~/.agents/skills/`。名称中的 `z-` 是个人筛选前缀，不是官方强制。

在终端执行（只下载并安装技能文件，不连接集群或发布应用）：

```bash
cicd_checkout=$(mktemp -d)
git clone https://github.com/score2021/z-cicd-delivery.git "$cicd_checkout/z-cicd-delivery"
python3 "$cicd_checkout/z-cicd-delivery/scripts/install-local.py"
```

安装器只复制 SKILL、四份运行参考、UI metadata 和许可证；不复制样例、评测、测试或Git历史。同名文件、目录、断链均拒绝覆盖；默认安装发现旧 `~/.codex/skills/` 同名安装也会拒绝，先由你处理重复版本。脚本不修改客户端全局配置。

新一轮在Codex中输入 `$z-cicd-delivery`；列表未刷新时重启客户端。其他兼容客户端的加载路径以各自文档为准，本仓库不宣称已完成所有客户端测试。

## 样例

下面可以直接复制到已安装技能的Codex对话，无需准备文件：

```text
$z-cicd-delivery 只分析，不改代码、不访问网络、不部署。
合成项目 sample-service 正在发布 r42。发布前 api、worker、admin 都是 image-v1，各2副本就绪。
CI检查和镜像发布通过，deploy先更新api后连接断开，job报watch_timeout。
同一窗口只读快照：api为image-v2，updated=2/ready=2/available=2；另两者仍image-v1、各2副本就绪。
UID未变，未发现更新pipeline，但schema与恢复兼容性尚未确认；自动回滚未开启。
入口静态文件和业务验收没跑；readiness出现4次503，用户页面30/30成功，无业务任务样本。
请给问题判定、当前能确认与不能确认的结论、最小恢复方案和验收步骤。
仅输出Markdown，不保存文件；没有记录的首次处理过程不要编造。
```

预期输出是部分更新状态、证据缺口、条件化恢复和分层验收，不会执行收费调用或修改服务。不要求与展示逐字一致。

需要实现新CI时可这样提出任务（目标、授权和资源范围按实际项目填写，不套用本合成案例的版本）：

```text
$z-cicd-delivery 阅读当前仓库，先核对现有CI与部署脚本，再完成不涉及生产外部写入的实现与隔离验证。
保持现有平台和资源，业务代码与配置变更只限本项目；不改共享数据库，不放开公网，不采购资源。
给出需要维护者配置的变量、目标权限、上线验收和失败恢复方式。已有信息足够就继续，只有真实缺口才问我。
```

## 工作方式与边界

1. 先区分只读评估、实现、排障与复盘，不因阅读日志就获得部署权限。
2. 拆分业务路径和发布路径，先做最小能力和网络实验。
3. 诊断产品缺陷、测试竞态和环境差异；有限修复后复验相关检查。
4. 按原身份对账副作用，再决定继续或回退；保留pending／unknown。
5. 发布锁覆盖更新与验收，按不可变产物确认实际目标和入口。
6. 交付证据、配置位置、未决和清理；不把pipeline通过外推全产品HA。

正常读取技能和安装器无云费用；真正运行AI客户端消耗客户端额度。Skill不授予新费用或权限，示例／历史预算也不构成授权。无需单独配置API、Docker或云账号才能阅读／使用分析模式。

## 目录与验证

```text
SKILL.md                 主指令与按需导航
agents/openai.yaml       Codex UI metadata
references/              交付流程、失败模式、验收恢复、运维复盘
scripts/install-local.py 无网络、不覆盖的本地安装器
tests/test_install.py    安装安全与完整性回归
examples/                合成输入与审核后的实际成果
evals/                   合成行为请求与评判方法
LICENSE                  MIT，仅适用于本仓库重新编写的内容
```

安装器回归可在仓库根目录执行：

```bash
python3 -B -m unittest discover -s tests -v
```

2026-10-27 的验证记录：

| 项目 | 实际结果与边界 |
| --- | --- |
| 官方技能格式校验 | 通过；验证name/frontmatter和结构，不代表行为通过 |
| 安装器回归 | 8/8；覆盖资源完整、重复目标、既有文件、断链、缺文件、源软链接、命名及旧安装冲突 |
| 干净CLI按名称调用 | Codex CLI 0.162.1，临时HOME／独立安装；使用默认模型，未单独核验模型标识 |
| 合成行为smoke | 4个请求完成，人工评议4/4：部分发布、Compose只读方案、传输不完整诊断、缺失历史复盘 |
| 工具副作用检查 | 模型执行命令仅本地读取，未调用部署／网络命令，工作目录输入未改变；客户端本身需要联网认证和模型交互 |
| 发布材料检查 | 显式文件允许清单、基础秘密模式、本地敏感词及语义复核；不包含原项目文件 |
| 成熟秘密扫描器 | 本机gitleaks不可用，未执行；不将其写成扫描通过 |
| 未验证 | 自动触发准确率、其他客户端、真实生产故障、各云环境与长周期可靠性 |

完整合成请求及评判方式见[evals](evals/README.md)。没有与无Skill对照的性能实验，不主张节省了固定比例时间；没有为测试本Skill执行真实基础设施故障、云采购或应用发布。少量smoke不能推导通用可靠性保证。

## 来源与许可证

根据用户明确授权的两份运维／复盘文档重新提炼；原件留在原项目，不作为本仓库附件或安装依赖。公开内容仅通用工程判断和合成材料，没有复制原应用实现。格式参考[Agent Skills](https://agentskills.io/specification)与[官方 Codex 文档](https://developers.openai.com/codex/skills/)。MIT见[LICENSE](LICENSE)。
