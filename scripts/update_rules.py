import os, datetime, requests, re

# ==========================================================
# 自动定位路径
# ==========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLACKLIST_FILE = os.path.join(BASE_DIR, 'iOS-OmniGuard-Blacklist.txt')
MITM_MODULE_FILE = os.path.join(BASE_DIR, 'OmniGuard-Predator-MitM.sgmodule')
README_FILE = os.path.join(BASE_DIR, 'README.md')

# ==========================================================
# 资源配置
# ==========================================================
SOURCES = {
    "bili": "https://raw.githubusercontent.com/app2smile/rules/master/js/bilibili-proto.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "baidu": "https://raw.githubusercontent.com/NobyDa/Script/master/Surge/JS/BaiduCloud.js"
}

def main():
    # 强制获取北京时间
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    t_str = now.strftime("%Y-%m-%d %H:%M")
    v_str = now.strftime("%Y.%m.%d.%H")
    status_logs = []

    # --- 阶段 A: 资源探测 ---
    for name, url in SOURCES.items():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200: status_logs.append(f"✅ {name} 源脚本正常存活")
            else: status_logs.append(f"🚨 {name} 源脚本失效 (HTTP {r.status_code})")
        except Exception as e: 
            status_logs.append(f"⚠️ {name} 请求超时或异常")

    # --- 阶段 B: 更新黑名单文本 ---
    if not os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
            f.write(f"#!name=iOS-OmniGuard-Blacklist\n! Version: {v_str}\n! Updated: {t_str}\n\n# 在此添加你的自定义域名拦截规则...\n")
    else:
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f: lines = f.readlines()
        with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
            for l in lines:
                if l.startswith('! Version:'): f.write(f"! Version: {v_str}\n")
                elif l.startswith('! Updated:'): f.write(f"! Updated: {t_str}\n")
                else: f.write(l)

    # --- 阶段 C: 构造并覆盖 SGModule ---
    yt_arg = r'{\"lyricLang\":\"zh-Hans\",\"captionLang\":\"zh-Hans\",\"blockUpload\":true,\"blockImmersive\":true,\"debug\":false}'
    
    m_template = r"""#!name = iOS-OmniGuard Predator-MitM (Pro融合版)
#!desc = 状态: 运行中 | 更新: {{UPDATE_TIME}} | 深度融合 YouTube & Bilibili 专项去广告增强
#!category = OmniGuard
#!system = ios

[Rule]
# ～YouTube_强制走TCP以利于MITM解密
AND,((DOMAIN-SUFFIX,googlevideo.com), (PROTOCOL,UDP)),REJECT
AND,((DOMAIN,youtubei.googleapis.com), (PROTOCOL,UDP)),REJECT

https://www.merriam-webster.com/dictionary/rewrite
# ～OmniGuard_基础去广告
^https?://.*\.amap\.com/ws/(boss/order_web/\w{8}_information|asa/ads_attribution) - reject
^https?://pan\.baidu\.com/act/.+ad_ - reject
^https?://.+\.pangle\.io/api/ad/union/sdk/ - reject
^https?://.+\.pangolin-sdk-toutiao\.com/api/ad/union/sdk/(get_ads|stats|settings)/ - reject
^https?://gurd\.snssdk\.com/src/server/v3/package - reject

# ～YouTube_去广告重写
(^https?:\/\/[\w-]+\.googlevideo\.com\/(?!dclk_video_ads).+?)&ctier=L(&.+?),ctier,(.+) $1$2$3 302
^https?:\/\/[\w-]+\.googlevideo\.com\/(?!(dclk_video_ads|videoplayback\?)).+&oad - reject-200
^https?:\/\/(www|s)\.youtube\.com\/api\/stats\/ads - reject-200
^https?:\/\/(www|s)\.youtube\.com\/(pagead|ptracking) - reject-200
^https?:\/\/s\.youtube\.com\/api\/stats\/qoe\?adcontext - reject-200

# ～BiliBili_哔哩哔哩_应用去广告重写
^https?:\/\/app\.bilibili\.com\/x\/resource\/ip - reject
^https?:\/\/app\.bilibili\.com\/bilibili\.app\.interface\.v1\.Search\/Default - reject
^https?:\/\/app\.bilibili\.com\/x\/resource\/top\/activity - reject-dict
^https:\/\/app\.bilibili\.com\/x\/v2\/splash\/show - reject-dict
^https:\/\/app\.bilibili\.com\/x\/v2\/search\/defaultwords - reject-dict
^https?:\/\/api\.bilibili\.com\/x\/vip\/ads\/material\/report - reject-dict
^https:\/\/api\.bilibili\.com\/pgc\/season\/player\/cards - reject-dict
^https?:\/\/api\.vc\.bilibili\.com\/search_svr\/v\d\/Search\/recommend_words - reject
^https?:\/\/api\.vc\.bilibili\.com\/topic_svr\/v1\/topic_svr - reject-dict
^https?:\/\/api\.bilibili\.com\/pgc\/season\/app\/related\/recommend\? - reject-dict
^https?:\/\/manga\.bilibili\.com\/twirp\/comic\.v\d\.Comic\/(Flash|ListFlash) - reject-dict
# ～BiliBili_哔哩哔哩_解除SIM卡地区限制
(^https?:\/\/app\.biliintl\.com\/intl\/.+)(&sim_code=\d+)(.+) $1$3 302

[Script]
# ～OmniGuard_网盘增强 (动态源)
baidu_cloud = type=http-response,pattern=^https?://pan\.baidu\.com/rest/2\.0/membership/user,requires-body=1,script-path={{BAIDU_URL}}

# ～YouTube_增强脚本 (动态源)
youtube.response = type=http-response,pattern=^https:\/\/youtubei\.googleapis\.com\/youtubei\/v1\/(browse|next|player|search|reel\/reel_watch_sequence|guide|account\/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={{YOUTUBE_URL}},argument="{{YT_ARG}}"

# ～BiliBili_哔哩哔哩_基础去广告脚本合集
biliad1 = type=http-response,pattern=^https?:\/\/api\.(bilibili|biliapi)\.(com|net)\/pgc\/page\/cinema\/tab\?,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad2 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/x\/v2\/splash\/list,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad3 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/resource\/show\/skin\?,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad4 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/v2\/account\/myinfo\?,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad5 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/x\/v2\/search\/square,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad6 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/v2\/feed\/index,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad7 = type=http-response,pattern=^https?:\/\/api\.(bilibili|biliapi)\.(com|net)\/pgc\/page\/bangumi,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad8 = type=http-response,pattern=^https?:\/\/api\.live\.bilibili\.com\/xlive\/app-room\/v1\/index\/getInfoByRoom,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad9 = type=http-response,pattern=^https?:\/\/api\.vc\.bilibili\.com\/dynamic_svr\/v1\/dynamic_svr\/dynamic_(history|new)\?,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad10 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/resource\/show\/tab,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js
biliad11 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/v2\/account\/mine,requires-body=1,script-path=https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js

# ～BiliBili_哔哩哔哩_Proto去广告 (动态源)
biliad12 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/bilibili\.app\.(view\.v1\.View\/View|dynamic\.v2\.Dynamic\/DynAll)$,requires-body=1,binary-body-mode=1,script-path={{BILI_URL}}

[MITM]
hostname = %APPEND% -redirector*.googlevideo.com, -broadcast.chat.bilibili.com, -*cdn*.biliapi.net, -*tracker*.biliapi.net, *amap.com, pan.baidu.com, *.googlevideo.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, *.pangolin-sdk-toutiao.com, *.pangle.io, *.pstatp.com, gurd.snssdk.com, app.bilibili.com, api.live.bilibili.com, api.vc.bilibili.com, api.bilibili.com, manga.bilibili.com, grpc.biliapi.net, api.biliapi.net
"""

    # 动态注入
    m = m_template.replace('{{UPDATE_TIME}}', t_str)
    m = m.replace('{{BAIDU_URL}}', SOURCES["baidu"])
    m = m.replace('{{YOUTUBE_URL}}', SOURCES["youtube"])
    m = m.replace('{{BILI_URL}}', SOURCES["bili"])
    m = m.replace('{{YT_ARG}}', yt_arg)

    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(m)

    # --- 阶段 D: 更新 README.md ---
    if not os.path.exists(README_FILE):
        base_readme = f"""# iOS-OmniGuard-Blacklist

**最后修改时间**：{t_str} (GMT+8)
! Version: {v_str}
! Updated: {t_str}

## 📅 最近更新动态
> 更新于: {t_str}
"""
        with open(README_FILE, 'w', encoding='utf-8') as f: f.write(base_readme)
        
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
            content += f"\n\n{log_header}{log_body}\n---"

        with open(README_FILE, 'w', encoding='utf-8') as f: f.write(content)

    for file_path in [BLACKLIST_FILE, MITM_MODULE_FILE, README_FILE]:
        if os.path.exists(file_path): os.utime(file_path, None)

if __name__ == '__main__':
    main()
