# MPh 排障与已知限制

> 依据官方 docs/installation.md 与 docs/limitations.md（v1.3.2）整理。

## 安装问题

| 症状 | 原因 | 解决 |
|---|---|---|
| `pip install MPh` 后导入失败 | 依赖未装 | 自动装 JPype1、NumPy；`pip uninstall MPh` 不会卸依赖 |
| Windows 上启动报错 | Microsoft Store 的 Python | 换 [python.org](https://python.org) 的 64 位 Python（issue #57） |
| COMSOL 5.5/5.6 连不上 | 新版 JPype 不支持 Java 8 | `pip install "jpype1<1.6"` |
| `mph.start(version=...)` 找不到自定义安装 | 安装位置不可发现 | 把 `comsol` 命令加进 PATH；或在 `~/.local`（Linux）/`~/Application`（macOS）建指向 Comsol 目录、以 `comsol` 开头的符号链接 |
| Class Kit 许可证启动失败 | 需 `-ckl` 参数 | `mph.option('classkit', True)` 后再 `mph.start()` |
| 找不到 COMSOL | 未安装 / 无许可证 | 需自行安装并持有 COMSOL 6.0+ 许可证 |

## 平台差异（limitations.md）

- **运行模式**：`mph.option('session', ...)` = `'client-server'`（默认）| `'stand-alone'` | `'platform-dependent'`
  - stand-alone：单进程直连，启动快、模型树操作快
  - client-server：独立服务器 + socket，启动慢、**模型树/递归访问可慢一个数量级**，但**求解时间不受影响**；支持跨网络远程
  - Linux/macOS 上 stand-alone 开箱即用失败（`java.lang.UnsatisfiedLinkError`）：需在 `.bashrc` 设 `LD_LIBRARY_PATH`（macOS 为 `DYLD_LIBRARY_PATH`），加入 Comsol 的 `lib/glnxa64`、`lib/glnxa64/gcc`、`ext/graphicsmagick/glnxa64`、`ext/cadimport/glnxa64` 等目录（按 COMSOL 版本官方文档）
- Windows 上 1.3.0 起默认也改为 client-server（解决部分用户不可复现的问题）

## 结构性限制（务必记住）

1. **一个 Python 进程 = 一个 COMSOL 客户端**（JPype 单 JVM + COMSOL 单 client）→ 并行必须 multiprocessing 多进程
2. **Ctrl+C 会崩溃 Python 会话**（JPype JVM 关停 bug）→ 应用代码不要依赖捕获 KeyboardInterrupt；长任务建议在独立进程跑
3. 备选桥 pyJNIus 支持多 JVM，但 COMSOL 部分 Java 方法在封装中缺失，官方不推荐
4. 组合参数扫描（多参数组合）映射到索引的规则复杂，官方明示支持可能受限
5. 旧版 `clearSolution()` 已在 1.3.0 替换为 `clearSolutionData()`，极端情况行为略有差异

## 运行时异常速查

| 异常 | 含义 | 处理 |
|---|---|---|
| `mph.start()` 很慢/失败 | 服务器启动（client-server 模式） | 等待约 10 s；检查 7892 无关——这是 COMSOL 服务器端口，与代理无关 |
| 求解报错 | 模型本身问题 | `model.problems()` 列出一致性检查问题 |
| `evaluate` 索引报错 | 数据集/时间/参数索引不对 | 先 `model.datasets()`、`model.inner()`、`model.outer()` 确认 |
| 导出路径不对 | 文件落在模型所在文件夹 | `export(node, file)` 第二参数指定路径 |

## 代理/网络特情（本机沙箱环境，见 local-environment.md）

- 沙箱内系统 curl（schannel）HTTPS 报 `SEC_E_NO_CREDENTIALS` —— 这是凭据存储访问受限，**与梯子无关**
- 抓取 GitHub/PyPI 用 Anaconda Python（OpenSSL）+ 代理 `http://127.0.0.1:7892`

## 沙箱内跑 COMSOL 的已知问题（本机实测）

| 症状 | 原因 | 解决 |
|---|---|---|
| `mph.start()` 报 `Invalid port: 65536` | 默认 client-server 模式需监听端口，沙箱限制 socket | `mph.option('session', 'stand-alone')` 后用 stand-alone 模式 |
| `client.load()` 报 `FlException: comsol.recoveries (拒绝访问)` | COMSOL 要写 `C:\Users\Lenovo\.comsol\v64\`，工作区沙箱拦截 | pwsh 用 `sandbox_permissions: danger-full-access` 运行 |
| 求解慢/无输出 | 首次启动 COMSOL 较慢 | 耐心等；COMSOL 首次启动约 10-30 秒 |
