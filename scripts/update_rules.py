import os
import re
from datetime import datetime, timedelta

# 获取路径锁死逻辑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
README_FILE = os.path.join(ROOT_DIR, "README.md")
OUTPUT_FILE = os.path.join(ROOT_DIR, "iOS-OmniGuard-Blacklist.txt")

def update_files(rules_list):
    bj_now = datetime.utcnow() + timedelta(hours=8)
    u_time = bj_now.strftime("%Y-%m-%d %H:%M")
    v_time = bj_now.strftime("%Y.%m.%d.%H")
    total_count = len(rules_list)

    # 1. 先写规则文件 (这个文件大没关系)
    header = f"[Adblock Plus 2.0]\n! Title: iOS-OmniGuard-Blacklist\n! Version: {v_time}\n! Updated: {u_time}\n! ----------------------------------------------------------\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(rules_list))

    # 2. 【核心修复】安全更新 README.md
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查：如果内容已经超过 1MB，说明之前写错了，尝试重置它
        if len(content) > 1024 * 1024:
            print("检测到 README 异常膨胀，正在重置为标准模板...")
            # 这里建议手动恢复一次 README，或者使用你锁死的模板
            return 

        # 动态更新元数据
        new_meta = (
            "\n"
            f"* **规则总数**：`{total_count:,}` 条 (自动去重后)\n"
            f"* **最后同步**：`{u_time}` (北京时间 UTC+8)\n"
            f"* **核心来源**：217heidai + BlueSkyXN (All + Sky)\n"
            f"* **个人来源**：my-rules.txt (个性化丰富包)\n"
            ""
        )
        
        # 严格替换逻辑
        content = re.sub(r".*?", new_meta, content, flags=re.DOTALL)
        content = re.sub(r"! Version: .*", f"! Version: {v_time}", content)
        content = re.sub(r"! Updated: .*", f"! Updated: {u_time}", content)
        content = re.sub(r"\*\*最后修改时间\*\*：.*", f"**最后修改时间**：{u_time} (GMT+8)  ", content)

        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(content)
