# -*- coding: utf-8 -*-
"""MPh/COMSOL 自动化环境体检脚本（纯标准库，无网络依赖）。

用法:
    python check_comsol_env.py

检查项:
    1. Python 版本与解释器路径 (需要 >= 3.10)
    2. JPype1 / numpy 是否已安装
    3. COMSOL 安装发现 (Windows 注册表 + PATH)
    4. 代理环境变量状态 (本机特情参考)
"""
import os
import platform
import shutil
import sys

# Windows GBK 控制台避免中文乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def check_python():
    print(f"[Python] {sys.version.split()[0]}  {sys.executable}")
    if sys.version_info < (3, 10):
        print("  !! MPh 1.3+ 需要 Python >= 3.10")
    print(f"[Platform] {platform.platform()}")


def check_packages():
    for pkg, modname in (("JPype1", "jpype"), ("numpy", "numpy")):
        try:
            mod = __import__(modname)
            version = getattr(mod, "__version__", "?")
            print(f"[Package] {pkg}: OK ({version})")
        except ImportError:
            print(f"[Package] {pkg}: MISSING  ->  pip install {pkg}")
    try:
        import jpype  # noqa: F401
        print("[JPype] JVM 可加载（COMSOL 5.x 需 jpype1<1.6）")
    except Exception as e:
        print(f"[JPype] 加载异常: {e}")


def check_comsol():
    found = []
    if sys.platform == "win32":
        try:
            import winreg
            for hive, label in ((winreg.HKEY_LOCAL_MACHINE, "HKLM"),
                                (winreg.HKEY_CURRENT_USER, "HKCU")):
                try:
                    key = winreg.OpenKey(hive, r"Software\COMSOL")
                    i = 0
                    while True:
                        try:
                            sub = winreg.EnumKey(key, i)
                            found.append(f"{label}\\Software\\COMSOL\\{sub}")
                            i += 1
                        except OSError:
                            break
                except OSError:
                    pass
        except Exception as e:
            print(f"[COMSOL] 注册表扫描异常: {e}")
    comsol = shutil.which("comsol")
    if comsol:
        found.append(f"PATH: {comsol}")
    if found:
        print("[COMSOL] 发现候选:")
        for f in found:
            print(f"    {f}")
    else:
        print("[COMSOL] 未发现安装 (注册表/PATH 均无) —— 需先安装 COMSOL 6.0+")


def check_proxy():
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        print(f"[Proxy] HTTPS_PROXY = {proxy}")
    else:
        print("[Proxy] 环境变量未设置 (沙箱默认; 本机系统代理为 127.0.0.1:7892)")
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
            enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
            server, _ = winreg.QueryValueEx(key, "ProxyServer")
            print(f"[Proxy] 系统代理: enabled={enabled}, server={server}")
        except Exception:
            pass


def main():
    print("=" * 60)
    print("MPh / COMSOL 环境体检")
    print("=" * 60)
    check_python()
    check_packages()
    check_comsol()
    check_proxy()
    print("=" * 60)
    print("完成。缺依赖: pip install MPh  (自动装 JPype1 + numpy)")


if __name__ == "__main__":
    main()
