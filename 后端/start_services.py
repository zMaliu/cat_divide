# -*- coding: utf-8 -*-
"""
一键启动：只拉起 Docker 里的 Milvus，不启动 Flask。
运行本脚本后，请在 PyCharm 里单独运行 main.py 启动应用。
这样 Apifox 请求正常，关掉 main.py 也不会卡死。
"""
import os
import sys
import time
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd=None, shell=True):
    cwd = cwd or ROOT_DIR
    print(f"[执行] {cmd}")
    r = subprocess.run(
        cmd, cwd=cwd, shell=shell,
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if r.stdout:
        print(r.stdout)
    if r.returncode != 0 and r.stderr:
        print("[Docker 错误输出]", r.stderr)
    return r.returncode == 0


def wait_for_port(host="127.0.0.1", port=19530, timeout=120):
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            time.sleep(2)
    return False


def main():
    os.chdir(ROOT_DIR)

    if not run("docker compose -p catdivide-milvus up -d"):
        print("---")
        print("Docker 命令执行失败。请确认 Docker Desktop 已启动。")
        sys.exit(1)
    print("等待 Milvus 就绪（约 30–90 秒）...")
    if not wait_for_port(port=19530):
        print("Milvus 未在超时内就绪，请稍后重试或检查 docker compose logs。")
        sys.exit(1)
    print("Milvus 已就绪。")
    print("")
    print("请在本项目里单独运行 main.py 启动 Flask，再用 Apifox 请求。")
    print("（不再由本脚本启动 main.py，避免请求卡住、关掉运行卡死。）")


if __name__ == "__main__":
    main()
