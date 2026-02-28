import requests
import os
from datetime import datetime, timedelta

# --- 路径锁死逻辑 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
README_FILE = os.path.join(ROOT_DIR, "README.md")
OUTPUT_FILE = os.path.join(ROOT_DIR, "iOS-OmniGuard-Blacklist.txt")
MY_RULES_FILE = os.path.join(ROOT_DIR, "my-rules.txt")

SOURCE_URLS = [
    "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt",
    "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/all.txt",
    "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/skyrules.txt"
]

def get_beijing_time():
    return datetime.utcnow() + timedelta(hours=8)

def update():
    bj_now = get_beijing_time()
    v_time = bj_now.strftime("%Y.%m.%d.%H")
    u_time = bj_now.strftime("%Y-%m-%d %H:%M")
    
    # 1. 抓取与去重
    all_rules = set()
    for url in SOURCE_URLS:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                lines = {l.strip() for l in r.text.splitlines() if l.strip() and not l.startswith(('!', '['))}
                all_rules.update(lines)
        except: continue
    
    if os.path.exists(MY_RULES_FILE):
        with open(MY_RULES_FILE, "r", encoding="utf-8") as f:
            all_rules.update({l.strip() for l in f if l.strip() and not l.startswith(('!', '['))})

    sorted_rules = sorted(list(all_rules))
    total_count = len(sorted_rules)

    # 2. 写入规则文件
    header = f"[Adblock Plus 2.0]\n! Title: iOS-OmniGuard-Blacklist\n! Version: {v_time}\n! Updated: {u_time}\n! Total Rules: {total_count}\n! ----------------------------------------------------------\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(sorted_rules))

    # 3. 写入 README.md (使用简单直接的 replace)
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查防膨胀：如果文件超过 1MB，说明之前坏了，直接跳过不写，防止 push 失败
        if len(content) > 1024 * 1024:
            print("README 文件体积异常，请手动清理后再运行脚本！")
            return

        # 替换占位符
        content = content.replace("{{VERSION}}", v_time)
        content = content.replace("{{UPDATE_TIME}}", u_time)
        content = content.replace("{{TOTAL_RULES}}", f"{total_count:,}")
        content = content.replace("{{SYNC_TIME}}", u_time)
        content = content.replace("{{FOOTER_TIME}}", u_time)

        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"成功更新 README！总规则数: {total_count}")

if __name__ == "__main__":
    update()
