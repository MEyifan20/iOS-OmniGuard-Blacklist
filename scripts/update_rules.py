import os
import re
import datetime
import urllib.request

# 上游 217heidai 规则地址
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"

def get_upstream_rules():
    print(f"⏳ 正在拉取上游规则: {UPSTREAM_URL}")
    try:
        # 伪装请求头，防止被 GitHub Raw 拒绝
        req = urllib.request.Request(UPSTREAM_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
            # 提取所有规则，过滤掉注释和空行，放入集合中以供 O(1) 极速查询
            rules = set([line.strip() for line in content.splitlines() if line.strip() and not line.startswith('!') and not line.startswith('#')])
            print(f"✅ 成功拉取上游规则，共计 {len(rules)} 条有效规则。")
            return rules
    except Exception as e:
        print(f"❌ 拉取上游规则失败: {e}")
        return set()

def process_and_deduplicate(blacklist_path, upstream_rules):
    if not os.path.exists(blacklist_path):
        print(f"⚠️ 找不到文件: {blacklist_path}")
        return

    with open(blacklist_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    removed_count = 0

    for line in lines:
        stripped_line = line.strip()
        
        # 1. 保留元数据、空行、注释
        if not stripped_line or stripped_line.startswith('!') or stripped_line.startswith('['):
            new_lines.append(line)
            continue
        
        # 2. 保留所有带有高级修饰符的“战术级规则” (你的心血)
        if '$important' in stripped_line or '##' in stripped_line or '#%#' in stripped_line or '@@' in stripped_line:
            new_lines.append(line)
            continue

        # 3. 核心去重：如果这条普通规则在上游库中已经存在，则剔除
        if stripped_line in upstream_rules:
            removed_count += 1
            print(f"🗑️ 发现冗余并剔除: {stripped_line}")
            continue
        
        # 4. 其他本地独有的规则，保留
        new_lines.append(line)

    # 准备写入新的时间戳与版本号
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    version_str = now.strftime("%Y.%m.%d.%H")
    time_str = now.strftime("%Y-%m-%d %H:%M")

    final_content = "".join(new_lines)
    # 使用正则替换文件头的版本和时间
    final_content = re.sub(r'! Version: .*', f'! Version: {version_str}', final_content)
    final_content = re.sub(r'! Updated: .*', f'! Updated: {time_str}', final_content)

    with open(blacklist_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"✅ 黑名单处理完成！本次剔除了 {removed_count} 条与上游重复的规则。")
    print(f"✅ 黑名单已更新至版本: {version_str}")

def update_readme():
    readme_path = 'README.md'
    if not os.path.exists(readme_path):
        return
        
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    version_str = now.strftime("%Y.%m.%d.%H")
    time_str = now.strftime("%Y-%m-%d %H:%M")

    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # 替换 README 中的版本和时间
    readme_content = re.sub(r'! Version: .*', f'! Version: {version_str}', readme_content)
    readme_content = re.sub(r'! Updated: .*', f'! Updated: {time_str}', readme_content)
    readme_content = re.sub(r'\*\*最后修改时间\*\*：.*', f'**最后修改时间**：{time_str} (GMT+8)', readme_content)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ README.md 同步更新完毕。")

if __name__ == '__main__':
    # 1. 抓取上游
    upstream = get_upstream_rules()
    # 2. 去重并更新黑名单
    process_and_deduplicate('iOS-OmniGuard-Blacklist.txt', upstream)
    # 3. 更新 README
    update_readme()
