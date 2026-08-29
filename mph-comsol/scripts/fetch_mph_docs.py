# -*- coding: utf-8 -*-
"""走本地代理抓取 GitHub 仓库文件（适用于沙箱内 schannel HTTPS 受限的环境）。

原理:
    沙箱内系统 curl(schannel) 的 HTTPS 会报 SEC_E_NO_CREDENTIALS；
    本机代理 127.0.0.1:7892 的纯 HTTP 通道可用；
    Anaconda Python 的 urllib 使用 OpenSSL, 经代理可正常完成 HTTPS。

用法:
    python fetch_mph_docs.py [--repo owner/name] [--branch main] [--out DIR] [--path 子路径]

默认抓取 MPh-py/MPh main 分支的 docs/ + mph/ 源码 + 顶层元数据文件。
代理地址可用环境变量 FETCH_PROXY 覆盖 (默认 http://127.0.0.1:7892)。
"""
import argparse
import json
import os
import sys
import urllib.request

DEFAULT_PROXY = os.environ.get("FETCH_PROXY", "http://127.0.0.1:7892")


def make_opener(proxy):
    handler = urllib.request.ProxyHandler({"https": proxy, "http": proxy})
    return urllib.request.build_opener(handler)


def get(url, proxy, timeout=60):
    opener = make_opener(proxy)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(req, timeout=timeout) as r:
        return r.read()


def select(path, keep):
    """按 keep 谓词挑选感兴趣的路径。"""
    return [p for p in path if keep(p)]


def main():
    ap = argparse.ArgumentParser(description="Fetch GitHub repo files via local proxy")
    ap.add_argument("--repo", default="MPh-py/MPh")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--out", default=r"C:\Users\Lenovo\Desktop\skill存储与杂\MPh_docs")
    ap.add_argument("--proxy", default=DEFAULT_PROXY)
    ap.add_argument("--path", default=None, help="只抓取该子路径下的文件")
    args = ap.parse_args()

    print(f"proxy={args.proxy}  repo={args.repo}@{args.branch}", flush=True)
    api_url = (f"https://api.github.com/repos/{args.repo}/git/trees/"
               f"{args.branch}?recursive=1")
    tree = json.loads(get(api_url, args.proxy).decode("utf-8"))
    if "tree" not in tree:
        print("API 响应异常:", json.dumps(tree)[:300], flush=True)
        sys.exit(1)
    paths = [e["path"] for e in tree["tree"] if e["type"] == "blob"]
    print(f"仓库共 {len(paths)} 个文件", flush=True)

    if args.path:
        wanted = [p for p in paths if p.startswith(args.path)]
    else:
        def keep(p):
            return (p.startswith("docs/") and p.endswith(".md")) or \
                p in ("ReadMe.md", "README.md", "LICENSE", "license.txt",
                      "pyproject.toml", "PyPI.md") or \
                (p.startswith("mph/") and p.endswith(".py"))
        wanted = select(paths, keep)

    ok, fail = 0, []
    for p in sorted(wanted):
        url = f"https://raw.githubusercontent.com/{args.repo}/{args.branch}/{p}"
        try:
            data = get(url, args.proxy)
            dest = os.path.join(args.out, p.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            ok += 1
            print(f"  [OK] {p} ({len(data)} B)", flush=True)
        except Exception as e:
            fail.append((p, str(e)))
            print(f"  [FAIL] {p}: {e}", flush=True)

    print(f"\n完成: {ok} 成功, {len(fail)} 失败 -> {args.out}", flush=True)
    if fail:
        for p, e in fail:
            print(f"  FAILED: {p} -> {e}", flush=True)


if __name__ == "__main__":
    main()
