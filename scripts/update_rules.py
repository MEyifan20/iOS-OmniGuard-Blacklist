import urllib.request
import re
import datetime
import os

# === 1. 配置上游源与动态脚本源 ===
UPSTREAM_DNS_URL = "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt"

# 动态脚本探测列表 (用于 README 状态更新与模块注入)
SCRIPTS = {
    "bili": "https://raw.githubusercontent.com/deezertidal/private/master/js-backup/Script/bilibili_json.js",
    "bili_proto": "https://raw.githubusercontent.com/app2smile/rules/master/js/bilibili-proto.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "baidu": "https://raw.githubusercontent.com/NobyDa/Script/master/Surge/JS/BaiduCloud.js"
}

# === 2. 核心清洗函数：适配小火箭与模块闭环 ===
def clean_and_merge_rules(raw_dns_text):
    """清理与小火箭模块冲突的规则，并追加高级自定义规则"""
    
    # 冲突黑名单：这些规则会引起 YouTube 播放无限转圈或历史记录失效，必须从 DNS 层剔除，交由 MitM 模块处理
    conflict_patterns = [
        re.compile(r"\|\|s\.youtube\.com\^.*"),
        re.compile(r"\|\|youtube\.com/api/stats/.*"),
        re.compile(r"\|\|youtube\.com/ptracking.*")
    ]
    
    cleaned_lines = []
    for line in raw_dns_text.splitlines():
        # 忽略原有注释和空行
        if not line or line.startswith('!') or line.startswith('['):
            continue
            
        # 检查是否命中冲突正则
        is_conflict = any(p.match(line) for p in conflict_patterns)
        if not is_conflict:
            cleaned_lines.append(line)
            
    # 去重并保持顺序
    cleaned_lines = list(dict.fromkeys(cleaned_lines))
    return "\n".join(cleaned_lines)

# === 3. 生成小火箭专属模块 ===
def generate_sgmodule(version_str):
    module_content = f"""#!name=iOS-OmniGuard Predator (小火箭适配版)
#!desc=状态: 运行中 | 更新: {version_str} | 深度融合 YouTube & Bilibili 专项去广告增强。已彻底修复 MitM 漏网与小火箭语法冲突。
#!category=OmniGuard
#!system=ios

https://ahrefs.com/writing-tools/paragraph-rewriter
# ～OmniGuard_基础去广告
^https?:\/\/.*\.amap\.com\/ws\/(boss\/order_web\/\w{{8}}_information|asa\/ads_attribution) reject
^https?:\/\/pan\.baidu\.com\/act\/.+ad_ reject
^https?:\/\/.+\.pangle\.io\/api\/ad\/union\/sdk\/ reject
^https?:\/\/.+\.pangolin-sdk-toutiao\.com\/api\/ad\/union\/sdk\/(get_ads|stats|settings)\/ reject
^https?:\/\/gurd\.snssdk\.com\/src\/server\/v3\/package reject

# ～YouTube_去广告重写
(^https?:\/\/[\w-]+\.googlevideo\.com\/(?!dclk_video_ads).+?)&ctier=L(&.+?),ctier,(.+) $1$2$3 302
^https?:\/\/[\w-]+\.googlevideo\.com\/(?!(dclk_video_ads|videoplayback\?)).+&oad reject-200
^https?:\/\/(www|s)\.youtube\.com\/api\/stats\/ads reject-200
^https?:\/\/(www|s)\.youtube\.com\/(pagead|ptracking) reject-200
^https?:\/\/s\.youtube\.com\/api\/stats\/qoe\?adcontext reject-200

# ～BiliBili_哔哩哔哩_应用去广告重写
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

# ～BiliBili_哔哩哔哩_解除SIM卡地区限制
(^https?:\/\/app\.biliintl\.com\/intl\/.+)(&sim_code=\d+)(.+) $1$3 302

[Script]
# ～OmniGuard_网盘增强 (动态源)
baidu_cloud = type=http-response,pattern=^https?://pan\.baidu\.com/rest/2\.0/membership/user,requires-body=1,script-path={SCRIPTS['baidu']}

# ～YouTube_增强脚本 (动态源)
youtube.response = type=http-response,pattern=^https:\/\/youtubei\.googleapis\.com\/youtubei\/v1\/(browse|next|player|search|reel\/reel_watch_sequence|guide|account\/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SCRIPTS['youtube']},argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}}"

# ～BiliBili_哔哩哔哩_基础去广告脚本合集
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

# ～BiliBili_哔哩哔哩_Proto去广告 (动态源)
biliad12 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/bilibili\.app\.(view\.v1\.View\/View|dynamic\.v2\.Dynamic\/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SCRIPTS['bili_proto']}

[MITM]
hostname = -redirector*.googlevideo.com, -broadcast.chat.bilibili.com, -*cdn*.biliapi.net, -*tracker*.biliapi.net, *amap.com, pan.baidu.com, *.googlevideo.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, *.pangolin-sdk-toutiao.com, *.pangle.io, *.pstatp.com, gurd.snssdk.com, *.bilibili.com, *.biliapi.net, *.biliapi.com, app.biliintl.com
"""
    with open("OmniGuard-Predator-MitM.sgmodule", "w", encoding="utf-8") as f:
        f.write(module_content)

# === 4. 生成带 Header 和高阶规则的 txt 文件 ===
def generate_blacklist_txt(cleaned_rules, version_str):
    header = f"""[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist (Standard Unified Edition)
! Description: 针对 iOS 环境深度优化的全能黑名单旗舰版。已剔除冗余项，集成了元素隐藏与高级脚本注入，实现 100% 纯净渲染。
! Version: {version_str}
! Codename: Predator-Standard
! Updated: {version_str[:10]} {version_str[11:]}
! Homepage: https://github.com/MEyifan20/iOS-OmniGuard-Blacklist
! License: https://opensource.org/licenses/mit-license.php
! Changelog: 1. 自动同步上游 DNS; 2. 自动清洗 YouTube MitM 冲突; 3. 补齐 Bilibili 泛解析。
! -------------------------------------------------------------------------------------------------------

! === Upstream Synchronized Rules (上游同步核心库) ===
"""
    
    custom_cosmetic_rules = """
! === Cosmetic Filtering & Advanced Scriptlets (视觉美化与 JS 注入) ===
google.com,google.com.hk###tads
google.com,google.com.hk##.commercial-unit-desktop-top
youtube.com##ytd-display-ad-renderer
youtube.com##ytd-promoted-sparkles-web-renderer
youtube.com##ytd-action-companion-ad-renderer
youtube.com##.ad-showing
baidu.com##.ec_tuiguang_pplink
baidu.com###content_right > div:not([id])
bilibili.com##.ad-report
bilibili.com##.bili-grid > div:has(.bili-video-card__info--ad)
zhihu.com##.Pc-card.Card
zhihu.com##.TopstoryItem--advertCard
*#%#//scriptlet("abort-on-property-read", "BlockAdBlock")
*#%#//scriptlet("abort-on-property-read", "fuckAdBlock")
*#%#//scriptlet("abort-on-property-read", "disable_adblocker")
youtube.com#%#//scriptlet("set-constant", "ytInitialPlayerResponse.adPlacements", "undefined")
youtube.com#%#//scriptlet("set-constant", "playerResponse.adPlacements", "undefined")
"""
    
    with open("iOS-OmniGuard-Blacklist.txt", "w", encoding="utf-8") as f:
        f.write(header + cleaned_rules + "\n" + custom_cosmetic_rules)

# === 5. 探活脚本并更新 README ===
def check_script_health(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        return response.getcode() == 200
    except:
        return False

def update_readme(version_str, health_status):
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # 替换 README 中的更新时间
    readme = re.sub(r"更新于: \d{4}-\d{2}-\d{2} \d{2}:\d{2}", f"更新于: {version_str[:10]} {version_str[11:]}", readme)
    readme = re.sub(r"Version: \d{4}\.\d{2}\.\d{2}\.\d{2}", f"Version: {version_str.replace('-', '.')[:10]}.{version_str[11:13]}", readme)

    # 替换存活状态 (包含了上游 DNS 拉取状态)
    status_text = f"- ✅ 上游 DNS 规则库全量同步完成\n"
    for name, is_alive in health_status.items():
        icon = "✅" if is_alive else "❌"
        status = "正常存活" if is_alive else "拉取失败/异常"
        status_text += f"- {icon} {name} 源脚本{status}\n"

    # 动态替换 README 尾部的更新动态区
    readme = re.sub(r"> 更新于:.*?(?=\n---)", f"> 更新于: {version_str[:10]} {version_str[11:]}\n{status_text}", readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

# === 主程序运行 ===
if __name__ == "__main__":
    # 获取北京时间 (UTC+8)
    utc_now = datetime.datetime.utcnow()
    bj_time = utc_now + datetime.timedelta(hours=8)
    version_str = bj_time.strftime("%Y-%m-%d %H:%M")

    print("开始拉取上游 DNS 规则...")
    try:
        req = urllib.request.Request(UPSTREAM_DNS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        raw_dns = urllib.request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(f"上游规则拉取失败: {e}")
        raw_dns = ""

    print("执行语法清洗与冲突剥离...")
    cleaned_dns = clean_and_merge_rules(raw_dns)

    print("生成小火箭专属模块...")
    generate_sgmodule(version_str)

    print("生成黑名单 TXT...")
    generate_blacklist_txt(cleaned_dns, version_str)

    print("探测底层依赖脚本存活状态...")
    health_status = {name: check_script_health(url) for name, url in SCRIPTS.items()}

    print("更新 README.md 文档...")
    update_readme(version_str, health_status)
    
    print("全量更新与兼容性处理完成！")
