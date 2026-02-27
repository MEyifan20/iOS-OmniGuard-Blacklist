import urllib.request
import re
import datetime
import os

# === 1. 配置上游源与动态脚本源 ===
UPSTREAM_DNS_URL = "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt"

SCRIPTS = {
    "bili": "https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js",
    "bili_proto": "https://raw.githubusercontent.com/app2smile/rules/master/js/bilibili-proto.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "baidu": "https://raw.githubusercontent.com/NobyDa/Script/master/Surge/JS/BaiduCloud.js"
}

# === 2. 核心清洗函数 ===
def clean_and_merge_rules(raw_dns_text):
    # 保持 YouTube 历史记录同步，避免 DNS 物理拦截冲突
    conflict_patterns = [
        re.compile(r"\|\|s\.youtube\.com\^.*"),
        re.compile(r"\|\|youtube\.com/api/stats/.*"),
        re.compile(r"\|\|youtube\.com/ptracking.*")
    ]
    cleaned_lines = []
    for line in raw_dns_text.splitlines():
        if not line or line.startswith('!') or line.startswith('['):
            continue
        is_conflict = any(p.match(line) for p in conflict_patterns)
        if not is_conflict:
            cleaned_lines.append(line)
    cleaned_lines = list(dict.fromkeys(cleaned_lines))
    return "\n".join(cleaned_lines)

# === 3. 生成小火箭专属模块 (修正画中画逻辑) ===
def generate_sgmodule(version_str):
    # 注意：为了恢复画中画，我们删除了 YouTube 的 reject-200 重写，全权交给 Script 处理
    module_content = f"""#!name=iOS-OmniGuard Predator (小火箭适配版)
#!desc=状态: 运行中 | 更新: {version_str} | 深度融合 YouTube & Bilibili 专项去广告增强。已修复画中画丢失与历史记录同步冲突。
#!category=OmniGuard
#!system=ios

https://ahrefs.com/writing-tools/paragraph-rewriter
# ～OmniGuard_基础去广告
^https?:\/\/.*\.amap\.com\/ws\/(boss\/order_web\/\w{{8}}_information|asa\/ads_attribution) reject
^https?:\/\/pan\.baidu\.com\/act\/.+ad_ reject
^https?:\/\/.+\.pangle\.io\/api\/ad\/union\/sdk\/ reject
^https?:\/\/.+\.pangolin-sdk-toutiao\.com\/api\/ad\/union\/sdk\/(get_ads|stats|settings)\/ reject
^https?:\/\/gurd\.snssdk\.com\/src\/server\/v3\/package reject

# ～YouTube_修正重写 (仅保留必需的 302 重定向以提升加载速度)
(^https?:\/\/[\w-]+\.googlevideo\.com\/(?!dclk_video_ads).+?)&ctier=L(&.+?),ctier,(.+) $1$2$3 302

# ～BiliBili_应用去广告重写
^https?:\/\/app\.bilibili\.com\/x\/resource\/ip reject
^https?:\/\/app\.bilibili\.com\/bilibili\.app\.interface\.v1\.Search\/Default reject
^https?:\/\/app\.bilibili\.com\/x\/resource\/top\/activity reject-dict
^https:\/\/app\.bilibili\.com\/x\/v2\/splash\/show reject-dict
^https:\/\/app\.bilibili\.com\/x\/v2\/search\/defaultwords reject-dict
^https?:\/\/api\.bilibili\.com\/x\/vip\/ads\/material\/report reject-dict
^https:\/\/api\.bilibili\.com\/pgc\/season\/player\/cards reject-dict
^https?:\/\/api\.vc\.bilibili\.com\/search_svr\/v\d\/Search\/recommend_words reject
^https?:\/\/api\.vc\.bilibili\.com\/topic_svr\/v1\/topic_svr reject-dict
^https?:\/\/api\.bilibili\.com\/pgc\/season\/app\/related\/recommend\? reject-dict
^https?:\/\/manga\.bilibili\.com\/twirp\/comic\.v\d\.Comic\/(Flash|ListFlash) reject-dict
(^https?:\/\/app\.biliintl\.com\/intl\/.+)(&sim_code=\d+)(.+) $1$3 302

[Script]
# ～OmniGuard_网盘增强
baidu_cloud = type=http-response,pattern=^https?://pan\.baidu\.com/rest/2\.0/membership/user,requires-body=1,script-path={SCRIPTS['baidu']}

# ～YouTube_增强脚本 (恢复画中画的关键：通过脚本伪装 Premium 身份)
youtube.response = type=http-response,pattern=^https:\/\/youtubei\.googleapis\.com\/youtubei\/v1\/(browse|next|player|search|reel\/reel_watch_sequence|guide|account\/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SCRIPTS['youtube']},argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false,\\"enableBackground\\":true}}"

# ～BiliBili_去广告脚本合集
biliad1 = type=http-response,pattern=^https?:\/\/api\.(bilibili|biliapi)\.(com|net)\/pgc\/page\/cinema\/tab\?,requires-body=1,script-path={SCRIPTS['bili']}
biliad2 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/x\/v2\/splash\/list,requires-body=1,script-path={SCRIPTS['bili']}
biliad3 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/resource\/show\/skin\?,requires-body=1,script-path={SCRIPTS['bili']}
biliad4 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/v2\/account\/myinfo\?,requires-body=1,script-path={SCRIPTS['bili']}
biliad5 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/x\/v2\/search\/square,requires-body=1,script-path={SCRIPTS['bili']}
biliad6 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/v2\/feed\/index,requires-body=1,script-path={SCRIPTS['bili']}
biliad7 = type=http-response,pattern=^https?:\/\/api\.(bilibili|biliapi)\.(com|net)\/pgc\/page\/bangumi,requires-body=1,script-path={SCRIPTS['bili']}
biliad8 = type=http-response,pattern=^https?:\/\/api\.live\.bilibili\.com\/xlive\/app-room\/v1\/index\/getInfoByRoom,requires-body=1,script-path={SCRIPTS['bili']}
biliad9 = type=http-response,pattern=^https?:\/\/api\.vc\.bilibili\.com\/dynamic_svr\/v1\/dynamic_svr\/dynamic_(history|new)\?,requires-body=1,script-path={SCRIPTS['bili']}
biliad10 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/resource\/show\/tab,requires-body=1,script-path={SCRIPTS['bili']}
biliad11 = type=http-response,pattern=^https?:\/\/app\.bilibili\.com\/x\/v2\/account\/mine,requires-body=1,script-path={SCRIPTS['bili']}

# ～BiliBili_Proto去广告
biliad12 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/bilibili\.app\.(view\.v1\.View\/View|dynamic\.v2\.Dynamic\/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SCRIPTS['bili_proto']}

[MITM]
hostname = -redirector*.googlevideo.com, -broadcast.chat.bilibili.com, -*cdn*.biliapi.net, -*tracker*.biliapi.net, *amap.com, pan.baidu.com, *.googlevideo.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, *.pangolin-sdk-toutiao.com, *.pangle.io, *.pstatp.com, gurd.snssdk.com, *.bilibili.com, *.biliapi.net, *.biliapi.com, app.biliintl.com
"""
    with open("OmniGuard-Predator-MitM.sgmodule", "w", encoding="utf-8") as f:
        f.write(module_content)

# === 4. 生成带 Header 的 txt 文件 (逻辑保持不变) ===
def generate_blacklist_txt(cleaned_rules, version_str):
    header = f"""[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist
! Version: {version_str}
! Updated: {version_str[:10]} {version_str[11:]}
! -------------------------------------------------------------------------------------------------------

! === Upstream Synchronized Rules ===
"""
    custom_cosmetic_rules = """
! === Cosmetic Filtering & Advanced Scriptlets ===
google.com,google.com.hk###tads
youtube.com##ytd-display-ad-renderer
youtube.com##.ad-showing
bilibili.com##.ad-report
*#%#//scriptlet("abort-on-property-read", "BlockAdBlock")
youtube.com#%#//scriptlet("set-constant", "ytInitialPlayerResponse.adPlacements", "undefined")
"""
    with open("iOS-OmniGuard-Blacklist.txt", "w", encoding="utf-8") as f:
        f.write(header + cleaned_rules + "\n" + custom_cosmetic_rules)

# === 5. 探活脚本并更新 README (逻辑保持不变) ===
def check_script_health(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        return response.getcode() == 200
    except:
        return False

def update_readme(version_str, health_status):
    if not os.path.exists("README.md"): return
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    readme = re.sub(r"更新于: \d{4}-\d{2}-\d{2} \d{2}:\d{2}", f"更新于: {version_str[:10]} {version_str[11:]}", readme)
    status_text = f"- ✅ 上游 DNS 规则库全量同步完成\\n"
    for name, is_alive in health_status.items():
        icon = "✅" if is_alive else "❌"
        status_text += f"- {icon} {name} 源脚本{'正常存活' if is_alive else '拉取失败'}\\n"
    readme = re.sub(r"> 更新于:.*?(?=\\n---)", f"> 更新于: {version_str[:10]} {version_str[11:]}\\n{status_text}", readme, flags=re.DOTALL)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    utc_now = datetime.datetime.utcnow()
    bj_time = utc_now + datetime.timedelta(hours=8)
    version_str = bj_time.strftime("%Y-%m-%d %H:%M")
    try:
        req = urllib.request.Request(UPSTREAM_DNS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        raw_dns = urllib.request.urlopen(req).read().decode('utf-8')
    except:
        raw_dns = ""
    cleaned_dns = clean_and_merge_rules(raw_dns)
    generate_sgmodule(version_str)
    generate_blacklist_txt(cleaned_dns, version_str)
    health_status = {name: check_script_health(url) for name, url in SCRIPTS.items()}
    update_readme(version_str, health_status)
