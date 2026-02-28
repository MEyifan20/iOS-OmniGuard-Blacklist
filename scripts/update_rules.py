import os
import re
from datetime import datetime, timedelta

# 路径锁死逻辑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
README_FILE = os.path.join(ROOT_DIR, "README.md")
OUTPUT_FILE = os.path.join(ROOT_DIR, "iOS-OmniGuard-Blacklist.txt")

def update_files(rules_list):
    # 时间计算：北京时间 UTC+8
    bj_now = datetime.utcnow() + timedelta(hours=8)
    u_time = bj_now.strftime("%Y-%m-%d %H:%M")
    v_time = bj_now.strftime("%Y.%m.%d.%H")
    total_count = len(rules_list)

    # 1. 生成规则主文件
    header = (
        f"[Adblock Plus 2.0]\n"
        f"! Title: iOS-OmniGuard-Blacklist\n"
        f"! Version: {v_time}\n"
        f"! Updated: {u_time}\n"
        f"! ----------------------------------------------------------\n"
    )
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(rules_list))
    print(f"✅ 规则文件已更新: {total_count} 条规则")

    # 2. 安全更新 README.md
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # 异常膨胀检查（防止正则失控）
        if len(content) > 1024 * 500:
            print("❌ 警告: README 文件大小异常，已停止自动写入以防损坏。")
            return

        # --- 策略 A: 首次替换（针对 {{TAG}} 占位符） ---
        content = content.replace("{{VERSION}}", v_time)
        content = content.replace("{{UPDATE_TIME}}", u_time)
        content = content.replace("{{TOTAL_RULES}}", f"{total_count:,}")
        content = content.replace("{{SYNC_TIME}}", u_time)
        content = content.replace("{{FOOTER_TIME}}", u_time)

        # --- 策略 B: 持续更新（针对已经生成过的时间戳进行正则替换） ---
        # 匹配顶部的 Version 和 Updated
        content = re.sub(r"! Version: \d+\.\d+\.\
