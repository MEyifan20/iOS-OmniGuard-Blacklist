import datetime
import os
import subprocess

# 路径配置：严格执行用户指定的大小写规范
RULES_FILE = "iOS-OmniGuard-Blacklist.txt"
CHANGELOG_FILE = "changelog.md"

def get_beijing_time():
    # 获取当前北京时间 (GMT+8)
    tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(tz)

def get_stats():
    # 1. 获取当前内存中的规则 (自动去重并排序)
    if not os.path.exists(RULES_FILE):
        return 0, 0, 0, 0, []
    
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 提取纯规则行 (非空且不以 ! 开头)
    raw_rules = [line.strip() for line in lines if line.strip() and not line.startswith("!")]
    
    raw_count = len(raw_rules)
    unique_rules = sorted(list(set(raw_rules))) # 执行去重并按字母排序
    deduped_count = raw_count - len(unique_rules)
    final_count = len(unique_rules)
    
    # 2. 与上一次 Git 提交的版本进行对比计算新增/移除
    added = 0
    removed = 0
    try:
        # 获取 HEAD 版本的内容进行差值分析
        old_content = subprocess.check_output(
            ["git", "show", f"HEAD:{RULES_FILE}"], 
            stderr=subprocess.DEVNULL
        ).decode("utf-8")
        
        old_rules = set(line.strip() for line in old_content.splitlines() if line.strip() and not line.startswith("!"))
        current_set = set(unique_rules)
        
        added = len(current_set - old_rules)
        removed = len(old_rules - current_set)
    except Exception:
        # 第一次运行或无旧版本记录时，新增数即为当前总数
        added = final_count
        removed = 0

    return final_count, added, removed, deduped_count, unique_rules

def update():
    now = get_beijing_time()
    formatted_time = now.strftime("%Y-%m-%d %H:%M") + " (GMT+8)"
    version_str = now.strftime("%Y.%m.%d.%H")

    # 获取经过计算的统计数据
    final_count, added, removed, deduped, sorted_rules = get_stats()

    # --- 1. 更新规则文件头部元数据并重新写入去重规则 ---
    new_head = [
        f"! Version: {version_str}\n",
        f"! 代号: 捕食者-标准型\n",
        f"! Updated: {formatted_time}\n",
        f"! Rules Count: {final_count:,}\n",
        "! --------------------------------------------------\n"
    ]
    
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_head)
        f.write("\n".join(sorted_rules) + "\n")

    # --- 2. 更新 changelog.md (全中文多行置顶追加) ---
    header = "## 📅 版本更新日志 | Version Changelog\n\n"
    
    new_entry = (
        f"### 🔖 版本：{version_str}\n"
        f"- **代号：** 捕食者-标准型\n"
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
            content = f.read()
            # 移除旧标题，防止文件内出现重复标题
            old_changelog = content.replace(header, "")

    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        # 新记录置顶，标题始终在最上方
        f.write(header + new_entry + old_changelog)

    print(f"✅ 成功刷新元数据并追加变更日志：Version {version_str}")

if __name__ == "__main__":
    update()
