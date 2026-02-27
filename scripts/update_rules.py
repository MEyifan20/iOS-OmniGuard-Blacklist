import urllib.request
import re
import datetime
import os

# === 1. 配置源 ===
UPSTREAM_DNS_URL = "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt"

SCRIPTS = {
    "bili": "https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js",
    "bili_proto": "https://raw.githubusercontent.com/app2smile/rules/master/js/bilibili-proto.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "baidu": "https://raw.githubusercontent.com/NobyDa/Script/master/Surge/JS/BaiduCloud.js"
}

# === 2. 规则清洗 (保持兼容历史记录) ===
def clean_and_merge_rules(raw_dns_text):
    conflict_patterns = [
        re.compile(r"\|\|s\.youtube\.com\^.*"),
        re.compile(r"\|\|youtube\.com/api/stats/.*"),
        re.compile(r"\|\|youtube\.com/ptracking.*")
    ]
    cleaned_lines = []
    for line in raw_dns_text.splitlines():
        if not line or line.startswith('!') or line.startswith('['):
            continue
        if not any(p.match(line) for p in conflict_patterns):
            cleaned_lines.append(line)
    return "\n".join(list(dict.fromkeys(cleaned_lines)))

# === 3. 生成模块 (严格匹配原厂去广告逻辑) ===
def generate_sgmodule(version_str):
    # 严格按照原作者 JSON 格式，不添加多余参数，确保 100% 兼容
    yt_arg = '{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}'
    
    module_content = f"""#!name=iOS-OmniGuard Predator (小火箭适配版)
#!desc=状态: 运行中 | 更新: {version_str} | 基于 Maasea 原厂逻辑重构，修复画中画、后台播放及历史记录同步。
#!category=OmniGuard
#!system=ios

[Rule]
# 核心：阻断 YouTube UDP 协议，防止广告通过 QUIC 协议逃逸 (画中画关键)
AND,((DOMAIN-SUFFIX,googlevideo.com), (PROTOCOL,UDP)),REJECT
AND,((DOMAIN,youtubei.googleapis.com), (PROTOCOL,UDP)),REJECT

https://ahrefs.com/writing-tools/paragraph-rewriter
# ～YouTube_原作者标准规则 (保留下划线占位符以确保小火箭解析稳定)
(^https?:\/\/[\w-]+\.googlevideo\.com\/(?!dclk_video_ads).+?)&ctier=L(&.+?),ctier,(.+) $1$2$3 302
^https?:\/\/[\w-]+\.googlevideo\.com\/(?!(dclk_video_ads|videoplayback\?)).+&oad _ reject-200
^https?:\/\/(www|s)\.youtube\.com\/api\/stats\/ads _ reject-200
^https?:\/\/(www|s)\.youtube\.com\/(pagead|ptracking) _ reject-200
^https?:\/\/s\.youtube\.com\/api\/stats\/qoe\?adcontext _ reject-200

# ～OmniGuard_基础去广告
^https?:\/\/.*\.amap\.com\/ws\/(boss\/order_web\/\w{{8}}_information|asa\/ads_attribution) reject
^https?:\/\/pan\.baidu\.com\/act\/.+ad_ reject
^https?:\/\/.+\.pangle\.io\/api\/ad\/union\/sdk\/ reject
^https?:\/\/.+\.pangolin-sdk-toutiao\.com\/api\/ad\/union\/sdk\/(get_ads|stats|settings)\/ reject
^https?:\/\/gurd\.snssdk\.com\/src\/server\/v3\/package reject

# ～BiliBili_应用去广告
(^https?:\/\/app\.biliintl\.com\/intl\/.+)(&sim_code=\d+)(.+) $1$3 302
^https?:\/\/app\.bilibili\.com\/x\/resource\/ip reject
^https?:\/\/app\.bilibili\.com\/bilibili\.app\.interface\.v1\.Search\/Default reject
^https?:\/\/api\.bilibili\.com\/x\/vip\/ads\/material\/report reject-dict
^https?:\/\/manga\.bilibili\.com\/twirp\/comic\.v\d\.Comic\/(Flash|ListFlash) reject-dict

[Script]
# ～YouTube_增强脚本 (Maasea 核心注入)
youtube.response = type=http-response,pattern=^https:\/\/youtubei\.googleapis\.com\/youtubei\/v1\/(browse|next|player|search|reel\/reel_watch_sequence|guide|account\/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SCRIPTS['youtube']},argument="{yt_arg}"

# ～BiliBili_脚本合集
biliad1 = type=http-response,pattern=^https?:\/\/api\.(bilibili|biliapi)\.(com|net)\/pgc\/page\/cinema\/tab\?,requires-body=1,script-path={SCRIPTS['bili']}
biliad12 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/bilibili\.app\.(view\.v1\.View\/View|dynamic\.v2\.Dynamic\/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SCRIPTS['bili_proto']}
baidu_cloud = type=http-response,pattern=^https?://pan\.baidu\.com/rest/2\.0/membership/user,requires-body=1,script-path={SCRIPTS['baidu']}

[MITM]
hostname = -redirector*.googlevideo.com, *.googlevideo.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, pan.baidu.com, *.amap.com, *.bilibili.com, *.biliapi.net, app.biliintl.com
"""
    with open("OmniGuard-Predator-MitM.sgmodule", "w", encoding="utf-8") as f:
        f.write(module_content)

# === 4. 辅助函数 (保持稳定运行) ===
def generate_blacklist_txt(cleaned_rules, version_str):
    header = f"[Adblock Plus 2.0]\\n! Title: iOS-OmniGuard-Blacklist\\n! Version: {version_str}\\n! -------------------------------------------------------------------------------------------------------\\n"
    with open("iOS-OmniGuard-Blacklist.txt", "w", encoding="utf-8") as f:
        f.write(header + cleaned_rules)

if __name__ == "__main__":
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    try:
        req = urllib.request.Request(UPSTREAM_DNS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        raw_dns = urllib.request.urlopen(req).read().decode('utf-8')
    except: raw_dns = ""
    cleaned = clean_and_merge_rules(raw_dns)
    generate_sgmodule(bj_time)
    generate_blacklist_txt(cleaned, bj_time)
