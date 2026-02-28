import os
import re
import requests
from datetime import datetime, timedelta

# 路径锁死逻辑 (小写路径规范)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
README_FILE = os.path.join(ROOT_DIR, "README.md")
OUTPUT_FILE = os.path.join(ROOT_DIR, "iOS-OmniGuard-Blacklist.txt")

def fetch_rules():
    """从上游抓取规则并执行物理去重"""
    rules_set = set() # 使用 set 自动去重
    
    # ⚠️ 请确认以下三大上游的直链 URL 是否准确，若有变动可直接修改
    urls = [
        "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt", # 217heidai
        "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/all.txt",        # BlueSkyXN (All)
        "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/skyrules.txt"    # BlueSkyXN (Sky)
    ]
    
    # 1. 抓取网络规则
    for url in urls:
        try:
            print(f"⏳ 正在下载规则: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            for line in response.text.splitlines():
                line = line.strip()
                # 过滤掉空行和注释行
                if line and not line.startswith('!') and not line.startswith('#') and not line.startswith('['):
                    rules_set.add(line)
            print("✅ 下载并解析成功")
        except Exception as e:
            print(f"❌ 下载失败 {url}: {e}")
            
    # 2. 读取本地个人规则包 (my-rules.txt)
    my_rules_path = os.path.join(ROOT_DIR, "my-rules.txt")
    if os.path.exists(my_rules_path):
        print(f"⏳ 正在读取个人包: my-rules.txt")
        with open(my_rules_path, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                line = line.strip()
                if line and not line.startswith('!') and not line.startswith('#') and not line.startswith('['):
                    rules_set.add(line)
        print("✅ 个人包合并完成")
    else:
        print("⚠️ 未找到 my-rules.txt，跳过合并本地规则。")
        
    # 转换回列表并按字母排序，保持文件整洁
    sorted_rules = sorted(list(rules_set))
    return sorted_rules

def update_files(rules_list):
    """更新规则文件和 README.md"""
    # 动态逻辑：北京时间动态更新
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
        f"! -------------------------------------------------------------------------------------------------------\n"
    )
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(rules_list))
    print(f"🛡️ 规则文件已生成，总计拦截条目: {total_count:,} 条")

    # 2. 安全更新 README.md (严格锁死排版)
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        if len(content) > 1024 * 500:
            print("❌ 警告: README 文件大小异常，已停止自动写入。")
            return

        # 策略 A: 首次替换（针对 {{TAG}}）
        content = content.replace("{{VERSION}}", v_time)
        content = content.replace("{{UPDATE_TIME}}", u_time)
        content = content.replace("{{TOTAL_RULES}}", f"{total_count:,}")
        content = content.replace("{{SYNC_TIME}}", u_time)
        content = content.replace("{{FOOTER_TIME}}", u_time)

        # 策略 B: 持续更新（正则替换）
        content = re.sub(r"! Version: \d+\.\d+\.\d+\.\d+", f"! Version: {v_time}", content)
        content = re.sub(r"! Updated: \d{4}-\d{2}-\d{2} \d{2}:\d{2}", f"! Updated: {u_time}", content)
        content = re.sub(r"\*\*规则总数\*\*：`[\d,]+` 条", f"**规则总数**：`{total_count:,}` 条", content)
        content = re.sub(r"\*\*最后同步\*\*：`\d{4}-\d{2}-\d{2} \d{2}:\d{2}`", f"**最后同步**：`{u_time}`", content)
        
        # 强制分行页脚锁死
        content = re.sub(r"\*\*最后修改时间\*\*：.*", f"**最后修改时间**：{u_time} (GMT+8)  ", content)

        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📖 README.md 动态元数据已刷新 ({u_time})")
    else:
        print("❌ 错误: 未找到 README.md 文件")

if __name__ == "__main__":
    print("🚀 开始执行 iOS-OmniGuard-Blacklist 构建任务...")
    
    # 获取真实规则
    final_rules = fetch_rules()
    
    # 只有抓取到规则才进行写入
    if final_rules and len(final_rules) > 100:
        update_files(final_rules)
    else:
        print("❌ 致命错误: 规则条目过少或抓取失败，取消文件写入以保护原有配置。")
