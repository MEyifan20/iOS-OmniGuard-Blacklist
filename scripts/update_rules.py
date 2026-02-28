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

# === 2. 逻辑固化生成 (确保画中画生效) ===
def generate_sgmodule(version_str):
    # 关键：手动粘贴之所以失败，是因为原代码里有占位符。这里我们填充为标准值。
    # 严格按照 Maasea 脚本所需的 JSON 格式，不留任何占位符。
    yt_arg = '{"lyricLang":"zh-Hans","captionLang":"zh-Hans","blockUpload":true,"blockImmersive":true,"debug":false}'
    
    # 将 argument 中的双引号进行 Python 转义，确保输出到文件时是 argument="{"key":"value"}"
    yt_script_line = f'youtube.response = type=http-response,pattern=^https:\/\/youtubei\.googleapis\.com\/youtubei\/v1\/(browse|next|player|search|reel\/reel_watch_sequence|guide|account\/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SCRIPTS["youtube"]},argument="{yt_arg.replace("\"", "\\\"")}"'

    module_content = f"""#!name=iOS-OmniGuard Predator (Standard Edition)
#!desc=状态: 运行中 | 更新: {version_str} | 已固化 Maasea 逻辑，修复画中画权限。
#!category=OmniGuard

[Rule]
AND,((DOMAIN-SUFFIX,googlevideo.com), (PROTOCOL,UDP)),REJECT
AND,((DOMAIN,youtubei.googleapis.com), (PROTOCOL,UDP)),REJECT

https://ahrefs.com/writing-tools/paragraph-rewriter
(^https?:\/\/[\w-]+\.googlevideo\.com\/(?!dclk_video_ads).+?)&ctier=L(&.+?),ctier,(.+) $1$2$3 302
^https?:\/\/[\w-]+\.googlevideo\.com\/(?!(dclk_video_ads|videoplayback\?)).+&oad _ reject-200
^https?:\/\/(www|s)\.youtube\.com\/api\/stats\/ads _ reject-200
^https?:\/\/(www|s)\.youtube\.(com|com\.hk)\/(pagead|ptracking) _ reject-200
^https?:\/\/s\.youtube\.com\/api\/stats\/qoe\?adcontext _ reject-200

# --- Bilibili & 其他净化 ---
^https?:\/\/.*\.amap\.com\/ws\/(boss\/order_web\/\w{{8}}_information|asa\/ads_attribution) reject
^https?:\/\/pan\.baidu\.com\/act\/.+ad_ reject
(^https?:\/\/app\.biliintl\.com\/intl\/.+)(&sim_code=\d+)(.+) $1$3 302
^https?:\/\/app\.bilibili\.com\/x\/resource\/ip reject

[Script]
{yt_script_line}

biliad1 = type=http-response,pattern=^https?:\/\/api\.(bilibili|biliapi)\.(com|net)\/pgc\/page\/cinema\/tab\?,requires-body=1,script-path={SCRIPTS['bili']}
biliad12 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/bilibili\.app\.(view\.v1\.View\/View|dynamic\.v2\.Dynamic\/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SCRIPTS['bili_proto']}
baidu_cloud = type=http-response,pattern=^https?://pan\.baidu\.com/rest/2\.0/membership/user,requires-body=1,script-path={SCRIPTS['baidu']}

[MITM]
hostname = %APPEND% -redirector*.googlevideo.com, *.googlevideo.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, pan.baidu.com, *.amap.com, *.bilibili.com, *.biliapi.net, app.biliintl.com
"""
    with open("OmniGuard-Predator-MitM.sgmodule", "w", encoding="utf-8") as f:
        f.write(module_content)

# === 4. 辅助函数保持不变 ===
def generate_blacklist_txt(cleaned_rules, version_str):
    header = f"[Adblock Plus 2.0]\\n! Title: iOS-OmniGuard-Blacklist\\n! Version: {version_str}\\n! Updated: {version_str}\\n"
    with open("iOS-OmniGuard-Blacklist.txt", "w", encoding="utf-8") as f:
        f.write(header + cleaned_rules)

if __name__ == "__main__":
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    try:
        req = urllib.request.Request(UPSTREAM_DNS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        raw_dns = urllib.request.urlopen(req).read().decode('utf-8')
    except: raw_dns = ""
    # 清洗逻辑
    cleaned = "\n".join([l for l in raw_dns.splitlines() if "youtube.com" not in l or "stats" not in l])
    generate_sgmodule(bj_time)
    generate_blacklist_txt(cleaned, bj_time)
