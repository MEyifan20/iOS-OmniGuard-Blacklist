import datetime
import os
import subprocess
import re

# 路径配置：严格执行规范
RULES_FILE = "iOS-OmniGuard-Blacklist.txt"
CHANGELOG_FILE = "changelog.md"
README_FILE = "README.md"

def get_beijing_time():
    """获取当前北京时间 (GMT+8)"""
    tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(tz)

def get_stats():
    """获取规则统计数据及变动详情"""
    if not os.path.exists(RULES_FILE):
        return 0, 0, 0, 0, []
    
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    raw_rules = [line.strip() for line in lines if line.strip() and not line.startswith("!")]
    raw_count = len(raw_rules)
    unique_rules = sorted(list(set(raw_rules)))
    deduped_count = raw_count - len(unique_rules)
    final_count = len(unique_rules)
    
    added = 0
    removed = 0
    try:
        old_content = subprocess.check_output(["git", "show", f"HEAD:{RULES_FILE}"], stderr=subprocess.DEVNULL).decode("utf-8")
        old_rules = set(line.strip() for line in old_content.splitlines() if line.strip() and not line.startswith("!"))
        current_set = set(unique_rules)
        added = len(current_set - old_rules)
        removed = len(old_rules - current_set)
    except:
        added = final_count
        removed = 0

    return final_count, added, removed, deduped_count, unique_rules

def update_readme(version, time, count, codename):
    """使用正则锚点动态刷新 README.md 中的元数据"""
    if not os.path.exists(README_FILE):
        print(f"⚠️ 未找到 {README_FILE}，跳过同步。")
        return
    
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 核心修复点：补全丢失的 HTML 锚点匹配 ---
    replacements = {
        r"()(.*?)()": f"\\1{version}\\3",
        r"()(.*?)()": f"\\1{time}\\3",
        r"()(.*?)()": f"\\1{count:,}\\3",
        r"()(.*?)()": f"\\1{codename}\\3"
    }

    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content, flags=re.DOTALL)

    # 2. 同步刷新页脚的“最后修改时间” (支持加粗或非加粗)
    content = re.sub(r"(\*\*最后修改时间\*\*|最后修改时间)：(.*)", f"\\1：{time}", content)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def update():
    now = get_beijing_time()
    formatted_time = now.strftime("%Y-%m-%d %H:%M") + " (GMT+8)"
    version_str = now.strftime("%Y.%m.%d.%H")
    codename = "掠夺者标准" # 已根据你的最新介绍文档同步代号

    final_count, added, removed, deduped, sorted_rules = get_stats()

    # --- 1. 更新主规则文件头部 (保持 Adblock Plus 2.0 风格) ---
    new_head = [
        f"[Adblock Plus 2.0]\n",
        f"! Title: iOS-OmniGuard-Blacklist (Standard Unified Edition)\n",
        f"! Description: 针对 iOS 环境深度优化的全能黑名单拦截引擎。整合 217heidai 环境前提，融合 BlueSkyXN 双库并加入个人规则丰富，与 Whitelist 完美配合。\n",
        f"! Version: {version_str}\n",
        f"! Codename: {codename}\n",
        f"! Updated: {formatted_time}\n",
        f"! Rules Count: {final_count:,}\n",
        f"! -------------------------------------------------------------------------------------------------------\n"
    ]
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_head)
        f.write("\n".join(sorted_rules) + "\n")

    # --- 2. 更新介绍文档 (生态联动) ---
    update_readme(version_str, formatted_time, final_count, codename)

    # --- 3. 更新 changelog.md (置顶追加) ---
    header = "## 📅 版本更新日志 | Version Changelog\n\n"
    new_entry = (
        f"### 🔖 版本：{version_str}\n"
        f"- **代号：** {codename}\n"
        f"- **更新时间：** {formatted_time}\n"
        f"- **规则总数：** {final_count:,}\n"
        f"- **变动详情：** \n"
        f"  - ⬆️ 新增规则：{added:,}\n"
        f"  - ⬇️ 移除规则：{removed:,}\n"
        f"  - 🧹 自动去重：{deduped:,}\n"
        f"- **项目状态：** 已同步兼容兄弟项目 [iOS-OmniGuard-Whitelist](https://github.com/MEyifan20/iOS-OmniGuard-Whitelist)\n\n"
        f"---\n\n"
        f"最后修改时间：{formatted_time}  \n"
        f"维护者：MEyifan20  \n"
        f"许可证：MIT\n\n"
        f"---\n\n"
    )

    old_changelog = ""
    if os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
            old_changelog = f.read().replace(header, "")
    
    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        f.write(header + new_entry + old_changelog)

    print(f"🚀 [生态联动] 成功同步所有文档，当前代号：{codename}")

if __name__ == "__main__":
    update()
