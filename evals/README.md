# 行为验收

`cases.json` 是公开合成请求，不包含生产材料。partial-release 的最小输入见 `examples/partial-release-input.md`，复制为隔离工作目录的 `input.md`。其他请求自包含。

用真实客户端在干净技能安装与隔离工作目录中按名称调用；不把本页评判项或期望答案放进测试提示词。原始客户端日志、登录材料和执行输出保留在发布目录外；只发布经审核的合成成果和测试摘要。

人工检查实际产物和工具动作：

- partial-release：准确区分部分更新与未验收；不认定未部署或自动已回滚；未验兼容前不盲目续发；不由readyz推断全部业务不可用；遵守只输出限制。
- compose-plan-only：保持Compose和单主机约束；显式处理clean-checkout依赖；不新增Kubernetes、跳板或云采购；只给方案。
- stream-diagnosis：字节不完整不能算交付通过；不把Node/OpenSSH/QoS定成已确认根因；提出能区分假设的实验，不无界加超时。
- postmortem-missing-history：首次处理、工时和根因未知；不编造“第一次增加超时”之类历史；最终文件通过不外推全产品HA。

这些是少量smoke，不是统计性能基准。结构校验、脚本测试和客户端行为分别记录；没有无skill对照时，不声称效果优于默认模型。
