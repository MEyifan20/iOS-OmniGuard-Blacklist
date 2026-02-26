import os, datetime, requests, re

# ==========================================================
# 1. 订阅链接与资源配置 (放在开头方便修改)
# ==========================================================
USER = "MEyifan20"
REPO = "iOS-OmniGuard-Blacklist"

# CDN 订阅地址 (用于 README 展示)
CDN_MODULE = f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@main/OmniGuard-Predator-MitM.sgmodule"
CDN_BLACKLIST = f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@main/iOS-OmniGuard-Blacklist.txt"

# 脚本原生资源
SOURCES = {
    "bili": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "baidu": "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "qimao": "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

# ==========================================================
# 2. 核心逻辑
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

    # --- 阶段 B: 静默探测资源 ---
    for name, url in SOURCES.items():
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200: status_logs.append(f"✅ {name} 正常")
            else: status_logs.append(f"🚨 {name} 失效({r.status_code})")
        except: status_logs.append(f"⚠️ {name} 超时")

    # --- 阶段 C: 构造全量模块 ---
    yt_arg = 'argument="{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true}"'
    m = f"#!name = iOS-OmniGuard Predator-MitM\n#!desc = 状态: 运行中 | 更新: {t_str}\n"
    m += "#!category = OmniGuard\n#!system = ios\n\n"
    m += "^https?://.*\\.amap\\.com/ws/(boss/order_web/\\w{8}_information|asa/ads_attribution) _ reject\n"
    m += "^https?://pan\\.baidu\\.com/act/.+ad_ - reject\n\n[Script]\n"
    m += f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}\n'
    m += f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},{yt_arg}\n'
    m += f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}\n'
    m += f'\n[MITM]\nhostname = %APPEND% *amap.com, pan.baidu.com, app.bilibili.com, *.googlevideo.com, youtubei.googleapis.com\n'

    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(m)

    # --- 阶段 D: 更新 README (优化字体与布局) ---
    if os.path.exists(README_FILE):
        with open(README_FILE, 'r', encoding='utf-8') as f: 
            lines = f.readlines()
        
        # 移除旧的订阅地址和动态日志，准备重新生成
        new_content = []
        skip_mode = False
        for line in lines:
            if "### 🚀 CDN 订阅地址" in line or "## 📅 最近更新动态" in line:
                skip_mode = True
            if skip_mode and (line.startswith("## ") or line.startswith("---")) and not ("### 🚀" in line or "## 📅" in line):
                skip_mode = False
            if not skip_mode:
                new_content.append(line)

        # 构造新模块
        sub_section = f"### 🚀 CDN 订阅地址\n- 模块: `{CDN_MODULE}`\n- 屏蔽: `{CDN_BLACKLIST}`\n\n"
        log_section = f"## 📅 最近更新动态\n> 更新于: {t_str}\n" + '\n'.join([f"- {s}" for s in status_logs]) + "\n"

        # 组装：将订阅地址插入到开头（通常在第一行标题后）
        final_lines = []
        if new_content and new_content[0].startswith("# "):
            final_lines.append(new_content[0])
            final_lines.append(sub_section)
            final_lines.extend(new_content[1:])
        else:
            final_lines.append(sub_section)
            final_lines.extend(new_content)

        # 更新时间戳并追加日志
        res_md = "".join(final_lines)
        res_md = re.sub(r'\*\*最后修改时间\*\*：.*', f'**最后修改时间**：{t_str} (GMT+8)', res_md)
        if "## 📅 最近更新动态" not in res_md:
            res_md += f"\n---\n{log_section}"
        else:
            res_md = re.sub(r'## 📅 最近更新动态.*', log_section, res_md, flags=re.DOTALL)

        with open(README_FILE, 'w', encoding='utf-8') as f: 
            f.write(res_md.strip())

if __name__ == '__main__':
    main()
