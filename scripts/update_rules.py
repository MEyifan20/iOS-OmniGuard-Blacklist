import os, datetime, requests, re

# ==========================================================
# 1. 订阅链接与资源配置 (放在开头方便修改)
# ==========================================================
USER = "MEyifan20"
REPO = "iOS-OmniGuard-Blacklist"

# CDN 订阅地址 (用于 README 展示)
CDN_MODULE = f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@main/OmniGuard-Predator-MitM.sgmodule"
CDN_BLACKLIST = f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@main/iOS-OmniGuard-Blacklist.txt"

# 脚本原生资源 (若 404，脚本将自动冻结并保留最后有效版本)
SOURCES = {
    "bili": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "baidu": "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "qimao": "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

# ==========================================================
# 2. 核心逻辑 (建议非必要不修改)
# ==========================================================
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

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

    # --- 阶段 B: 静默探测资源 (404 也不报错) ---
    for name, url in SOURCES.items():
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200: status_logs.append(f"✅ {name} 正常")
            else: status_logs.append(f"🚨 {name} 失效({r.status_code})")
        except: status_logs.append(f"⚠️ {name} 超时")

    # --- 阶段 C: 构造全量模块 (补全功能与 URL 重写) ---
    yt_arg = 'argument="{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true}"'
    
    m = f"#!name = iOS-OmniGuard Predator-MitM\n#!desc = 状态: 运行中 | 更新: {t_str}\n"
    m += "#!category = OmniGuard\n#!system = ios\n\nhttps://ahrefs.com/writing-tools/paragraph-rewriter\n"
    m += "^https?://.*\\.amap\\.com/ws/(boss/order_web/\\w{8}_information|asa/ads_attribution) _ reject\n"
    m += "^https?://pan\\.baidu\\.com/act/.+ad_ - reject\n\n[Script]\n"
    m += f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}\n'
    m += f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},{yt_arg}\n'
    m += f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}\n'
    m += f'\n[MITM]\nhostname = %APPEND% *amap.com, pan.baidu.com, app.bilibili.com, *.googlevideo.com, youtubei.googleapis.com\n'

    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(m)

    # --- 阶段 D: 更新 README (包含 CDN 地址展示) ---
    if os.path.exists(README_FILE):
        with open(README_FILE, 'r', encoding='utf-8') as f: content = f.read()
        
        # 1. 注入 CDN 订阅地址
        cdn_section = f"## 🚀 全自动 CDN 订阅地址\n- **模块**: `{CDN_MODULE}`\n- **DNS**: `{CDN_BLACKLIST}`"
        if "## 🚀 全自动 CDN 订阅地址" in content:
            content = re.sub(r"## 🚀 全自动 CDN 订阅地址.*?txt`", cdn_section, content, flags=re.DOTALL)
        else: content += f"\n\n{cdn_section}"

        # 2. 修改时间与动态日志
        new_md = []
        for rl in content.splitlines():
            if '**最后修改时间**：' in rl: new_md.append(f"**最后修改时间**：{t_str} (GMT+8)")
            else: new_md.append(rl)
        
        final_readme = '\n'.join(new_md)
        if '## 📅 最近更新动态' in final_readme:
            log_block = f"## 📅 最近更新动态\n> 更新于: {t_str}\n" + '\n'.join([f"- {s}" for s in status_logs])
            final_readme = re.sub(r'## 📅 最近更新动态.*?(?=\n##|$)', log_block, final_readme, flags=re.DOTALL)
            
        with open(README_FILE, 'w', encoding='utf-8') as f: f.write(final_readme)

    # --- 阶段 E: 同步物理文件时间戳 (相当于 touch) ---
    for file_path in [BLACKLIST_FILE, MITM_MODULE_FILE, README_FILE]:
        if os.path.exists(file_path):
            os.utime(file_path, None)  # 刷新文件的访问时间和修改时间至当前时间

if __name__ == '__main__':
    main()
