import datetime
import os

# 路径配置
RULES_FILE = "iOS-OmniGuard-Blacklist.txt"
CHANGELOG_FILE = "changelog.md"

def update():
    # 获取北京时间
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    formatted_time = now.strftime("%Y-%m-%d %H:%M") + " (GMT+8)"
    version_str = now.strftime("%Y.%m.%d.%H")

    if not os.path.exists(RULES_FILE):
        return

    with open(RULES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 动态计算规则数
    rules_count = sum(1 for line in lines if line.strip() and not line.startswith("!"))

    # 刷新头部元数据
    new_rules = []
    for line in lines:
        if line.startswith("! Version:"):
            new_rules.append(f"! Version: {version_str}\n")
        elif line.startswith("! Updated:"):
            new_rules.append(f"! Updated: {formatted_time}\n")
        elif line.startswith("! Rules Count:"):
            new_rules.append(f"! Rules Count: {rules_count:,}\n")
        else:
            new_rules.append(line)

    with open(RULES_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_rules)

    # 刷新 changelog.md (置顶逻辑)
    header = "## 📅 版本更新日志 | Version Changelog\n\n"
    new_entry = (
        f"### 🔖 Version: {version_str}\n"
        f"- **Codename:** Predator-Standard\n"
        f"- **Updated:** {formatted_time}\n"
        f"- **Rules Count:** {rules_count:,}\n"
        f"- **Status:** 已同步兼容兄弟项目 [iOS-OmniGuard-Whitelist](https://github.com/MEyifan20/iOS-OmniGuard-Whitelist)\n\n"
        f"---\n\n"
        f"最后修改时间：{formatted_time}  \n"
        f"维护者：MEyifan20  \n"
        f"许可证：MIT\n\n"
        f"---\n\n"
    )

    old_content = ""
    if os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
            old_content = f.read().replace(header, "")

    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        f.write(header + new_entry + old_content)

if __name__ == "__main__":
    update()
