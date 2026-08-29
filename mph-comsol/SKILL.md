---
name: mph-comsol
description: "MPh（Pythonic scripting interface for COMSOL Multiphysics）仿真自动化技能。用于让代理通过 Python + JPype 驱动本机 COMSOL：加载/创建/修改 .mph 模型、改参数、建网格、求解研究、评估结果（NumPy 数组）、导出图片与数据、批量参数扫描、多进程并行仿真、调用完整 COMSOL Java API；当用户提到 COMSOL、多物理场仿真、.mph 文件、MPh 库、Comsol 脚本/自动化/批处理、参数扫描、仿真结果提取时应优先使用。"
category: engineering
license: MIT
metadata:
    os: ["win32"]
    skill-author: dsh-agent (封装自 MPh 官方文档 v1.3.2)
    requires:
        pythonPackages: ["JPype1", "numpy"]
---

# MPh · COMSOL 自动化技能

> 本技能封装开源库 **MPh**（Pythonic scripting interface for Comsol Multiphysics）的完整使用知识：架构、安装、标准工作流、API 速查、陷阱与排障、本机环境特情。涉及 COMSOL 仿真自动化时**优先按本技能行动**，不要凭记忆拼 MPh 代码。

## 目标

让代理在本机 Windows 环境可靠驱动 COMSOL Multiphysics：加载模型 → 改参数 → 求解 → 评估/导出；批量参数扫描与多进程并行；必要时降级到完整 COMSOL Java API。同时提供本机可用的网络抓取通道（Anaconda Python + 本地代理），保证能随时回查官方文档。

## 何时使用

- 用户提到 COMSOL、多物理场、`.mph` 文件、MPh 库、Comsol 脚本/自动化/批处理
- 需要批量跑仿真、参数扫描、优化迭代（遗传算法、差分进化）
- 需要从 Python 加载/创建/修改 COMSOL 模型并提取结果（NumPy）
- 用户想用 Python 替代 COMSOL GUI / Matlab / Java 脚本

**不要用于**：SolidWorks/AutoCAD 建模（转 solidworks-automation / autocad-automation）、非 COMSOL 的 FEM/CFD（如 fluidsim）。

## 核心事实

- MPh：MIT 开源，作者 John Hennig，当前 v1.3.2（Python ≥ 3.10），PyPI 包名 `MPh`
- 原理：`JPype1` 桥接 COMSOL Java API + `NumPy` 返回数组；依赖仅这两个
- 官方文档：https://mph.readthedocs.io；本地镜像：工作区 `MPh_docs/`（30 个文件，含全部 docs/ 与 mph/ 源码）
- **一个 Python 进程同时只能有一个 COMSOL 客户端**（JPype 单 JVM + COMSOL 单 client）；并行 = `multiprocessing` 多进程

## 标准工作流

```python
import mph
client = mph.start()                    # 启动 COMSOL 服务器（约 10 s；cores=N 限核）
model = client.load('capacitor.mph')    # 或 client.create() 从零创建
model.parameters()                      # 查看参数（字典，值含单位字符串）
model.parameter('d', '1[mm]')           # 修改参数
model.build(); model.mesh()             # 建几何 + 网格（solve 前自动做，显式更稳）
model.solve('static')                   # 求解指定研究；model.solve() = 全部
model.evaluate('2*es.intWe/U^2', 'pF')  # 全局/局部评估 → numpy 数组
model.export('image', 'out.png')        # 触发模型预设导出节点
model.save('solved')                    # 保存（自动补 .mph）
```

## 关键 API 速查（详见 references/api-cheatsheet.md）

- **名称优先于 tag**：全程用 label（如 `'medium 1'`）引用节点，不用 `mat1` 之类 tag
- **pathlib 风格 `/` 运算符**：`model/'geometries/geometry/ice block'`；根节点 `model/''` 或 `model/None`；名称含 `/` 时用 `//` 转义
- **完整 Java API 兜底**：`model.java` / `client.java` 暴露 COMSOL 原生对象，官方 Java 示例几乎可原样粘贴
- `mph.tree(model)` 打印模型树；`mph.inspect(obj)` 检视 Java 对象
- `mph.option('session', ...)`：`'client-server'`（默认）/ `'stand-alone'` / `'platform-dependent'`；`mph.option('classkit', True)` 用于 Class Kit 许可证
- 结果数据集：`model.datasets()` / `model.inner()`（时间步）/ `model.outer()`（参数索引）

## 本机环境注意（Windows，详见 references/local-environment.md）

- Python 用 `D:\Anaconda3\python.exe`（OpenSSL TLS）；**系统 curl 是 schannel 版**，在沙箱/代理环境下 HTTPS 报 `SEC_E_NO_CREDENTIALS (0x8009030e)`，直连 GitHub 会失败
- **抓取 GitHub/PyPI/readthedocs 内容**：Anaconda Python + 本地代理 `http://127.0.0.1:7892`（自由猫 ziyoumaoCore），参考 `scripts/fetch_mph_docs.py`
- 代理端口 7892 来自 Windows 系统代理设置；必要时先用 `netstat -ano | findstr :7892` 确认代理进程存活
- 运行前可先 `python scripts/check_comsol_env.py` 做环境体检

## 已知限制与陷阱（详见 references/troubleshooting.md）

- **Ctrl+C 会崩溃 Python 会话**（JPype JVM 关停 bug）——应用代码别依赖 KeyboardInterrupt
- 单进程单客户端；client-server 模式模型树操作较慢（求解时间不受影响）
- Windows 别用 Microsoft Store 的 Python（issue #57）
- COMSOL 5.5/5.6 需 `pip install "jpype1<1.6"`；6.0+ 官方支持（至 6.3 验证）
- 组合参数扫描索引映射可能受限
- Linux/macOS stand-alone 需 LD_LIBRARY_PATH/DYLD_LIBRARY_PATH

## 参考文件

- `references/api-cheatsheet.md` — 公开 API 逐条速查（start/Client/Model/Node/tree/inspect/option）
- `references/workflows.md` — 典型工作流完整代码（基础/扫描/多进程并行/Java API/模型瘦身）
- `references/troubleshooting.md` — 安装、平台差异、已知限制与解决办法
- `references/local-environment.md` — 本机环境事实与网络通道
- `scripts/check_comsol_env.py` — 环境体检（Python/依赖/COMSOL 发现/代理）
- `scripts/fetch_mph_docs.py` — 走本地代理抓取 GitHub 原始文件（可配置仓库/分支/路径）
