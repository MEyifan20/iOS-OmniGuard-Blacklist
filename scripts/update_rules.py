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

        # 异常膨胀检查
        if len(content) > 1024 * 500:
            print("❌ 警告: README 文件大小异常，已停止。")
            return

        # --- 策略 A: 首次替换（针对 {{TAG}} 占位符） ---
        content = content.replace("{{VERSION}}", v_time)
        content = content.replace("{{UPDATE_TIME}}", u_time)
        content = content.replace("{{TOTAL_RULES}}", f"{total_count:,}")
        content = content.replace("{{SYNC_TIME}}", u_time)
        content = content.replace("{{FOOTER_TIME}}", u_time)

        # --- 策略 B: 持续更新（正则替换，修复了之前的断行错误） ---
        # 顶部 Version
        content = re.sub(r"! Version: \d+\.\d+\.\d+\.\d+", f"! Version: {v_time}", content)
        # 顶部 Updated
        content = re.sub(r"! Updated: \d{4}-\d{2}-\d{2} \d{2}:\d{2}", f"! Updated: {u_time}", content)
        # 规则总数
        content = re.sub(r"\*\*规则总数\*\*：`[\d,]+` 条", f"**规则总数**：`{total_count:,}` 条", content)
        # 同步时间
        content = re.sub(r"\*\*最后同步\*\*：`\d{4}-\d{2}-\d{2} \d{2}:\d{2}`", f"**最后同步**：`{u_time}`", content)
        # 页脚时间
        content = re.sub(r"\*\*最后修改时间\*\*：.*", f"**最后修改时间**：{u_time} (GMT+8)  ", content)

        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ README.md 动态元数据已刷新 ({u_time})")
    else:
        print("❌ 错误: 未找到 README.md 文件")

if __name__ == "__main__":
    # 模拟规则数据，实际运行时建议从您的源获取
    rules_list = ["||example.com^", "||ads.net^"]
    update_files(rules_list)
