import os, datetime, requests, re

# ==========================================================
# 自动定位路径：获取脚本所在目录的上一级（即仓库根目录）
# ==========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 拼接根目录文件的绝对路径
BLACKLIST_FILE = os.path.join(BASE_DIR, 'iOS-OmniGuard-Blacklist.txt')
MITM_MODULE_FILE = os.path.join(BASE_DIR, 'OmniGuard-Predator-MitM.sgmodule')
README_FILE = os.path.join(BASE_DIR, 'README.md')

# ==========================================================
# 1. 订阅链接与资源配置
# ==========================================================
USER = "MEyifan20"
REPO = "iOS-OmniGuard-Blacklist"

CDN_MODULE = f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@main/OmniGuard-Predator-MitM.sgmodule"
CDN_BLACKLIST = f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@main/iOS-OmniGuard-Blacklist.txt"

SOURCES = {
    "bili": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "baidu": "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "qimao": "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

def main():
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    t_str = now.strftime("%Y-%m-%d %H:%M")
    v_str = now.strftime("%Y.%m.%d.%H")
    status_logs = []

    # --- 阶段 A: 更新黑名单元数据 ---
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f: lines = f.readlines()
        with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
            for l in lines:
                if '! Version:' in l: f.write(f"! Version: {v_str}\n")
                elif '! Updated:' in l: f.write(f"! Updated: {t_str}\n")
                else: f.write(l)

    # --- 阶段 B: 资源探测 ---
    for name, url in SOURCES.items():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200: status_logs.append(f"✅ {name} 正常")
            else: status_logs.append(f"🚨 {name} 失效({r.status_code})")
        except: status_logs.append(f"⚠️ {name} 超时")
    
    status_logs.append("✅ fanqie 规则已集成")

    # --- 阶段 C: 构造全量模块 (集成番茄系规则) ---
    yt_arg = r'argument="{\"lyricLang\":\"zh-Hans\",\"captionLang\":\"zh-Hans\",\"blockUpload\":true}"'
    
    m = f"#!name = iOS-OmniGuard Predator-MitM\n#!desc = 状态: 运行中 | 更新: {t_str}\n"
    m += "#!category = OmniGuard\n#!system = ios\n\n"
    m += "https://www.merriam-webster.com/dictionary/rewrite\n"
    m += r"^https?://.*\.amap\.com/ws/(boss/order_web/\w{8}_information|asa/ads_attribution) reject" + "\n"
    m += r"^https?://pan\.baidu\.com/act/.+ad_ reject" + "\n"
    m += r"^https?://.+\.pangolin-sdk-toutiao\.com/api/ad/union/sdk/(get_ads|stats|settings)/ reject" + "\n"
    m += r"^https?://gurd\.snssdk\.com/src/server/v3/package reject" + "\n\n"
    
    m += "[Script]\n"
    m += f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}\n'
    m += f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},{yt_arg}\n'
    m += f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}\n'
    
    m += f'\n[MITM]\nhostname = %APPEND% *amap.com, pan.baidu.com, app.bilibili.com, *.googlevideo.com, youtubei.googleapis.com, *.pangolin-sdk-toutiao.com, *.pstatp.com, gurd.snssdk.com\n'

    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(m)

    # --- 阶段 D: 更新 README ---
    if os.path.exists(README_FILE):
        with open(README_FILE, 'r', encoding='utf-8') as f: content = f.read()
        
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if '**最后修改时间**：' in line:
                new_lines.append(f"**最后修改时间**：{t_str} (GMT+8)")
            elif '! Version:' in line:
                new_lines.append(f"! Version: {v_str}")
            elif '! Updated:' in line:
                new_lines.append(f"! Updated: {t_str}")
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)

        log_header = "## 📅 最近更新动态"
        log_body = f"\n> 更新于: {t_str}\n" + '\n'.join([f"- {s}" for s in status_logs]) + "\n"
        
        if log_header in content:
            parts = content.split(log_header)
            suffix = parts[1].split("\n---")
            if len(suffix) > 1:
                content = parts[0] + log_header + log_body + "\n---" + "---".join(suffix[1:])
            else:
                content = parts[0] + log_header + log_body
        else:
            content = content.replace("\n---", f"\n\n{log_header}{log_body}\n---", 1)

        with open(README_FILE, 'w', encoding='utf-8') as f: f.write(content)

    for file_path in [BLACKLIST_FILE, MITM_MODULE_FILE, README_FILE]:
        if os.path.exists(file_path):
            os.utime(file_path, None)

if __name__ == '__main__':
    main()
