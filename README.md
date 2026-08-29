# mph-comsol-skill

MPh（Pythonic scripting interface for COMSOL Multiphysics）仿真自动化技能仓库。

## 这是什么

一个可迁移的 AI 技能包：让 Codex / Claude / DSH 等代理通过 Python + JPype 驱动本机 COMSOL，
覆盖模型加载/创建/修改、参数扫描、求解、结果评估（NumPy）、导出、多进程并行仿真与完整 Java API 兜底。

内容封装自 MPh 官方仓库（v1.3.2）的 README、tutorial、demonstrations、installation、limitations、credits，
并包含本机实测的环境结论（COMSOL 6.4 + stand-alone 模式验证通过）。

## 目录结构

```
mph-comsol/                     # 技能本体（可直接复制到技能目录）
├── SKILL.md                    # 主指令（frontmatter: name/description/category/license/metadata）
├── README.md                   # 技能简介
├── manifest.yaml               # 技能元数据
├── references/
│   ├── api-cheatsheet.md       # 公开 API 速查（按 v1.3.2 源码核对）
│   ├── workflows.md            # 8 个典型工作流完整代码
│   ├── troubleshooting.md      # 安装/平台/已知限制/沙箱排障
│   └── local-environment.md    # 本机环境事实与网络通道（可自行改写）
└── scripts/
    ├── check_comsol_env.py     # 环境体检（Python/依赖/COMSOL 发现/代理）
    └── fetch_mph_docs.py       # 走本地代理抓取 GitHub 文件
```

## 安装方法

**方式 A：Claude Code（复制）**

```bash
# Windows
xcopy /E /I mph-comsol %USERPROFILE%\.claude\skills\mph-comsol
# Linux / macOS
cp -r mph-comsol ~/.claude/skills/mph-comsol
```

**方式 B：DSH 代理（复制）**

```bash
cp -r mph-comsol ~/.dsh/skills/mph-comsol
```

**方式 C：skills CLI（如已安装 skills 工具）**

```bash
npx -y skills add https://github.com/<你的账号>/mph-comsol-skill --skill mph-comsol
```

安装后验证：`python mph-comsol/scripts/check_comsol_env.py`

## 前置要求

- Python >= 3.10（64 位）
- `pip install MPh`（自动装 JPype1 + numpy）
- COMSOL Multiphysics 6.0+（已装许可证）
- 沙箱/受限环境注意：COMSOL 需写 `~/.comsol`；默认 client-server 模式可能因端口受限失败，
  可改用 `mph.option('session', 'stand-alone')`（详见 references/troubleshooting.md）

## 许可证

MIT。技能内容基于 MIT 许可的开源项目 MPh（https://github.com/MPh-py/MPh）文档整理。
