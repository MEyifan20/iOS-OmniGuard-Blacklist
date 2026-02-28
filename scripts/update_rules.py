import requests
import re
import os
from datetime import datetime, timedelta

# --- 配置区域 ---
# 上游规则源
SOURCE_URLS = [
    "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt",
    "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/all.txt",
    "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/skyrules.txt"
]

# 本地个人规则文件 (如不存在则忽略)
MY_RULES_FILE = "my-rules.txt"
# 输出规则文件
OUTPUT_FILE = "iOS-OmniGuard-Blacklist.txt"
# 需要同步更新的介绍文件
README_FILE = "README.md"

def get_beijing_time():
    """获取北京时间 (UTC+8)"""
    return datetime.utcnow() + timedelta(hours=8)

def fetch_and_merge():
    all_rules = set()
    
    # 1. 抓取远程规则
    for url in SOURCE_URLS:
        try:
            print(f"正在同步上游源: {url}")
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                lines = response.text.splitlines()
                # 过滤注释和空白行，仅保留有效规则进行去重
                valid_rules = {line.strip() for line in lines if line.strip() and not line.startswith(('!', '['))}
                all_rules.update(valid_rules)
        except Exception as e:
            print(f"抓取失败 {url}: {e}")

    # 2. 读取本地规则
    if os.path.exists(MY_RULES_FILE):
        with open(MY_RULES_FILE, "r", encoding="utf-8") as f:
            local_rules = {line.strip() for line in f if line.strip() and not line.startswith(('!', '['))}
            all_rules.update(local_rules)

    return sorted(list(all_rules))

def update_files(rules):
    bj_now = get_beijing_time()
    v_time = bj_now.strftime("%Y.%m.%d.%H")
    u_time = bj_now.strftime("%Y-%m-%d %H:%M")
    total_count = len(rules)

    # --- 1. 更新生成的规则文件 (.txt) ---
    header = [
        "[Adblock Plus 2.0]",
        f"! Title: iOS-OmniGuard-Blacklist",
        f"! Version: {v_time}",
        f"! Updated: {u_time}",
        f"! Total Rules: {total_count}",
        "! ----------------------------------------------------------"
    ]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(header) + "\n")
        f.write("\n".join(rules))

    # --- 2. 动态更新 README.md (精准匹配占位符) ---
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # 更新顶部 Version, Codename, Updated (针对之前排好的格式)
        content = re.sub(r"! Version: .*", f"! Version: {v_time}", content)
        content = re.sub(r"! Updated: .*", f"! Updated: {u_time}", content)

        # 更新元数据锚点 (START_METADATA 区域)
        new_meta = (
            "\n"
            f"* **规则总数**：`{total_count:,}` 条 (自动去重后)\n"
            f"* **最后同步**：`{u_time}` (北京时间 UTC+8)\n"
            f"* **核心来源**：217heidai + BlueSkyXN (All + Sky)\n"
            f"* **个人来源**：my-rules.txt (个性化丰富包)\n"
            ""
        )
        content = re.sub(r".*?", new_meta, content, flags=re.DOTALL)

        # 更新页脚时间 (严格执行换行排版)
        content = re.sub(r"\*\*最后修改时间\*\*：.*", f"**最后修改时间**：{u_time} (GMT+8)  ", content)

        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print("README.md 动态同步成功！")

if __name__ == "__main__":
    final_rules = fetch_and_merge()
    update_files(final_rules)
    print(f"构建完成，共计 {len(final_rules)} 条规则。")
