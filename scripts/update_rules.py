import datetime
import os

# 配置路径：严格执行小写路径规范
rules_path = "rules.txt"
changelog_path = "changelog.md"  # 已改为全小写

def update_project_files():
    # 1. 获取当前北京时间 (GMT+8)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    formatted_time = now.strftime("%Y-%m-%d %H:%M") + " (GMT+8)"
    version_str = now.strftime("%Y.%m.%d.%H")
    
    # 2. 读取并计算规则总数 (过滤掉以 ! 开头的注释行)
    if not os.path.exists(rules_path):
        print(f"❌ Error: {rules_path} not found.")
        return

    with open(rules_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    rules_count = sum(1 for line in lines if line.strip() and not line.startswith("!"))
    
    # 3. 动态刷新 rules.txt 头部元数据
    new_lines = []
    for line in lines:
        if line.startswith("! Version:"):
            new_lines.append(f"! Version: {version_str}\n")
        elif line.startswith("! Updated:"):
            new_lines.append(f"! Updated: {formatted_time}\n")
        elif line.startswith("! Rules Count:"):
            new_lines.append(f"! Rules Count: {rules_count:,}\n")
        else:
            new_lines.append(line)
            
    with open(rules_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # 4. 自动化追加 changelog.md (置顶新记录)
    header = "## 📅 版本更新日志 | Version Changelog\n\n"
    
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            old_content = f.read()
    else:
        old_content = header

    new_log_entry = (
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

    # 保持标题置顶，新日志插入标题下方
    body = old_content.replace(header, "")
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(header + new_log_entry + body)

    print(f"✅ Success: Updated {rules_path} and {changelog_path}")

if __name__ == "__main__":
    update_project_files()
