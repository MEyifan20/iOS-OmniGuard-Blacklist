import datetime
import re
import os

def update_files():
    # 获取当前北京时间 (UTC+8)
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    
    # 格式化版本号 (例如: 2026.02.26.21) -> 这里我们将最后一位按小时动态生成
    version_str = now.strftime("%Y.%m.%d.%H")
    # 格式化时间戳 (例如: 2026-02-26 15:20)
    time_str = now.strftime("%Y-%m-%d %H:%M")

    # 1. 更新 README.md
    readme_path = 'README.md'
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # 替换 Version 和 Updated
        readme_content = re.sub(r'! Version: .*', f'! Version: {version_str}', readme_content)
        readme_content = re.sub(r'! Updated: .*', f'! Updated: {time_str}', readme_content)
        # 替换底部中文时间戳
        readme_content = re.sub(r'\*\*最后修改时间\*\*：.*', f'**最后修改时间**：{time_str} (GMT+8)', readme_content)

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ README.md updated to version {version_str}")

    # 2. 更新 iOS-OmniGuard-Blacklist.txt
    blacklist_path = 'iOS-OmniGuard-Blacklist.txt'
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r', encoding='utf-8') as f:
            blacklist_content = f.read()

        # 替换 Version 和 Updated
        blacklist_content = re.sub(r'! Version: .*', f'! Version: {version_str}', blacklist_content)
        blacklist_content = re.sub(r'! Updated: .*', f'! Updated: {time_str}', blacklist_content)

        with open(blacklist_path, 'w', encoding='utf-8') as f:
            f.write(blacklist_content)
        print(f"✅ iOS-OmniGuard-Blacklist.txt updated to version {version_str}")

if __name__ == '__main__':
    update_files()
