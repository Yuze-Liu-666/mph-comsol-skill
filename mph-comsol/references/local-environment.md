# 本机环境事实（Windows / Lenovo 机器）

> 本文件记录这台机器上与 MPh/COMSOL 自动化相关、且与沙箱默认环境不同的关键事实。
> 2026 年实测记录；若环境变化（重装、换代理），以最新实测为准。

## Python

- Anaconda Python：`D:\Anaconda3\python.exe`（OpenSSL TLS 后端）
- 这是本机**唯一可用的 HTTPS 抓取通道**（见下）
- 沙箱中 `curl.exe`（Windows schannel 版）与 Git 自带 curl 均为 schannel 编译，HTTPS 会失败

## 网络（重要）

- **代理**：`http://127.0.0.1:7892`（自由猫 ziyoumaoCore.exe，PID 动态；系统代理设置里 ProxyServer=127.0.0.1:7892）
- 用户浏览器/Office 等正常应用走系统代理，工作正常
- **沙箱内现象**：
  - 直连（不带代理）：`curl` 全部返回 `000`
  - 走代理 + schannel curl：CONNECT 隧道 200 建立，但 TLS 握手失败 → `curl: (35) schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030e)`
  - 走代理 + 纯 HTTP：正常（200）
  - **走代理 + Anaconda Python（urllib/OpenSSL）：HTTPS 正常** ✅
- **结论**：HTTPS 抓取统一用 `D:\Anaconda3\python.exe` + `ProxyHandler({'http': 'http://127.0.0.1:7892', 'https': 'http://127.0.0.1:7892'})`
- 诊断命令：
  - `netstat -ano | findstr :7892` — 确认代理存活（或 `Get-NetTCPConnection -LocalPort 7892`）
  - 若代理端口变化，查注册表：`HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings` 的 `ProxyServer`

## 已抓取的本地资料（工作区）

- `MPh_docs/` — MPh 仓库 main 分支 30 个文件：全部 `docs/*.md`（tutorial/demonstrations/installation/limitations/releases/credits/api）+ `mph/` 源码（client/model/node/server/session/config/discovery/meta）+ pyproject.toml
- `MPh_ReadMe.md` — README 原文
- `MPh_中文指南.md` — 中文完整指南
- 重新抓取：`python scripts/fetch_mph_docs.py`（见 scripts 说明）

## COMSOL 状态（2026 实测）

- **COMSOL 6.4（64 位）已安装**，注册表发现于 `HKLM\Software\COMSOL\COMSOL64`，stand-alone 模式可正常启动（12 核机器）
- **端到端已验证通过**：`mph.start()` → `client.load('capacitor.mph')` → `model.solve('static')` → `evaluate('2*es.intWe/U^2','pF')` = 0.736785 pF（d=2mm 默认参数，与官方教程 sweep 索引 2 的值 0.73678535 一致）→ `save()`
- MPh 1.3.2 + jpype1 1.7.1 已装入 Anaconda（`pip install MPh` 经代理成功）
- 官方演示模型已本地化：`MPh_docs/demos/capacitor.mph`（99.9 KB）

## 沙箱内运行 COMSOL 的关键结论

1. **必须用 stand-alone 模式**：`mph.option('session', 'stand-alone')` 后再 `mph.start()`
   - 默认 client-server 模式在沙箱内失败：`java.lang.IllegalArgumentException: Internal error. Invalid port: 65536`（找不到可用监听端口，沙箱限制 socket）
2. **必须用完整文件权限运行**（pwsh `sandbox_permissions: danger-full-access`）：
   - COMSOL 要写 `C:\Users\Lenovo\.comsol\v64\`（日志、`comsol.recoveries` 恢复目录）；沙箱工作区模式下报 `FlException: comsol.recoveries (拒绝访问)`
   - 完整权限 + stand-alone 后全流程通过
3. 验证命令模板（含权限）：
   ```
   pwsh(sandbox=danger-full-access): python mph_e2e_test.py <模型路径> stand-alone
   ```
4. 无许可证时 `mph.start()` 会失败 —— 这是预期行为，不是 bug

## 注意事项

- 沙箱 pwsh 无代理环境变量（HTTP_PROXY/HTTPS_PROXY 为空）；需要时手动设置 `$env:HTTPS_PROXY`
- 控制台 GBK 编码：Python print 中文/特殊字符可能报 UnicodeEncodeError —— 写文件代替打印，或设 `PYTHONIOENCODING=utf-8`
