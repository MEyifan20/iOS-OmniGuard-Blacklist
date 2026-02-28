import os
import re
from datetime import datetime, timezone, timedelta

# 配置区
TXT_FILE = "ios-omniguard-blacklist.txt" # 确保小写规范
SG_MODULE = "omniguard-predator-mitm.sgmodule" # 确保小写规范
README_FILE = "README.md"

def get_beijing_time():
    # 获取北京时间 (UTC+8)
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz)

def update_files():
    now = get_beijing_time()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    version = now.strftime("%Y%m%d.%H%M") # 版本号格式：年月日.时分

    # 1. 读取黑名单并去重、排序
    if not os.path.exists(TXT_FILE):
        print(f"Error: {TXT_FILE} not found")
        return

    with open(TXT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 过滤注释和空行，提取域名并转小写
    rules = sorted(list(set(
        line.strip().lower() for line in lines 
        if line.strip() and not line.startswith("#")
    )))
    rule_count = len(rules)

    # 2. 更新 .sgmodule (Surge 模块)
    sg_content = [
        f"#!name=OmniGuard Predator MitM",
        f"#!desc=拦截广告与追踪器。版本: {version} | 更新时间: {timestamp} | 规则数: {rule_count}",
        f"#!system=ios",
        "\n[Rule]",
        *[f"DOMAIN-SET,https://raw.githubusercontent.com/MEyifan20/iOS-OmniGuard-Blacklist/main/{TXT_FILE},REJECT" for _ in range(1)], # 示例逻辑
        "\n[MITM]",
        "hostname = %APPEND% *google*" # 示例逻辑，可按需修改
    ]
    
    with open(SG_MODULE, "w", encoding="utf-8") as f:
        f.write("\n".join(sg_content))

    # 3. 更新 README.md (自动查找标记并替换)
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            readme_data = f.read()
        
        # 使用正则替换特定标记的内容
        readme_data = re.sub(r"规则数量：.*", f"规则数量：`{rule_count}`", readme_data)
        readme_data = re.sub(r"更新时间：.*", f"更新时间：`{timestamp} (UTC+8)`", readme_data)
        readme_data = re.sub(r"当前版本：.*", f"当前版本：`{version}`", readme_data)

        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(readme_data)

    print(f"✅ 更新成功: 版本 {version}, 规则总数 {rule_count}")

if __name__ == "__main__":
    update_files()
