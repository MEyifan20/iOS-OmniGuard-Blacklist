import datetime
import os
import subprocess
import re

# 路径配置：严格执行规范
RULES_FILE = "iOS-OmniGuard-Blacklist.txt"
CHANGELOG_FILE = "changelog.md"
README_FILE = "README.md"

def get_beijing_time():
    tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(tz)

def get_stats():
    if not os.path.exists(RULES_FILE):
        return 0, 0, 0, 0, []
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    raw_rules = [line.strip() for line in lines if line.strip() and not line.startswith("!")]
    unique_rules = sorted(list(set(raw_rules)))
    final_count = len(unique_rules)
    deduped_count = len(raw_rules) - final_count
    added, removed = 0, 0
    try:
        old_content = subprocess.check_output(["git", "show", f"HEAD:{RULES_FILE}"], stderr=subprocess.DEVNULL).decode("utf-8")
        old_rules = set(line.strip() for line in old_content.splitlines() if line.strip() and not line.startswith("!"))
        added = len(set(unique_rules) - old_rules)
        removed = len(old_rules - set(unique_rules))
    except:
        added = final_count
    return final_count, added, removed, deduped_count, unique_rules

def update_readme(version, time, count, codename):
    """【防乱码+防重复】精准刷新 README.md"""
    if not os.path.exists(README_FILE): return
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 定义替换字典：只替换被 包裹的内容
    replacements = {
        r"()(.*?)()": f"\\1{version}\\3",
        r"()(.*?)()": f"\\1{time}\\3",
        r"()(.*?)()": f"\\1{count:,}\\3",
        r"()(.*?)()": f"\\1{codename}\\3"
    }
    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content, flags=re.DOTALL)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def update():
    now = get_beijing_time()
    formatted_time = now.strftime("%Y-%m-%d %H:%M") + " (GMT+8)"
    version_str = now.strftime("%Y.%m.%d.%H")
    codename = "掠夺者标准"

    final_count, added, removed, deduped, sorted_rules = get_stats()

    # 1. 刷新规则文件头部 (严格对齐你的硬核头部格式)
    new_head = [
        f"[广告拦截加 2.0]！\n",
        f"标题：iOS-OmniGuard-黑名单（标准统一版）！\n",
        f"描述：针对 iOS 环境深度优化的全能黑名单拦截引擎。整合 217黑带环境前提，融合 BlueSkyXN 双库并加入个人规则丰富，与白名单完美配合。\n",
        f"版本：{version_str}！\n",
        f"代号：{codename}！\n",
        f"更新：{formatted_time} ！\n",
        f"规则总数：{final_count:,} 条 ！\n",
        f"! -----------------------------------------------------------------------------------------------------------\n"
    ]
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_head)
        f.write("\n".join(sorted_rules) + "\n")

    # 2. 刷新 README.md
    update_readme(version_str, formatted_time, final_count, codename)

    # 3. 刷新 changelog.md (置顶追加)
    header = "## 📅 版本更新日志 | Version Changelog\n\n"
    new_entry = (
        f"### 🔖 版本：{version_str}\n"
        f"- **代号：** {codename}\n"
        f"- **更新时间：** {formatted_time}\n"
        f"- **规则总数：** {final_count:,} (新增: {added} | 移除: {removed})\n"
        f"- **状态：** 已同步兼容兄弟项目 [iOS-OmniGuard-Whitelist](https://github.com/MEyifan20/iOS-OmniGuard-Whitelist)\n\n"
        f"---\n\n最后修改时间：{formatted_time}\n维护者：MEyifan20\n许可证：MIT\n\n---\n\n"
    )
    old_log = ""
    if os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
            old_log = f.read().replace(header, "")
    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        f.write(header + new_entry + old_log)

if __name__ == "__main__":
    update()
