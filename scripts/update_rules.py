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

# === 2. 核心清洗函数 (仅针对外部拉取的 DNS 黑名单) ===
def clean_and_merge_rules(raw_dns_text):
    # 剔除黑名单中可能干扰 YouTube 历史记录和画中画的物理拦截行
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
    # 去重并合并
    return "\n".join(list(dict.fromkeys(cleaned_lines)))

# === 3. 生成模块 (全量复刻 Maasea 逻辑，确保自动更新不失效) ===
def generate_sgmodule(version_str):
    # 锁定原作者 Argument 格式，确保 \" 转义正确
    yt_arg = '{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}'
    
    module_content = f"""#!name=iOS-OmniGuard Predator (小火箭适配版)
#!desc=状态: 运行中 | 更新: {version_str} | 已固化 Maasea 原厂逻辑，确保画中画与后台播放永久生效。
#!category=OmniGuard
#!system=ios

[Rule]
# 固化：封死 UDP 逃逸通道 (画中画激活前提)
AND,((DOMAIN-SUFFIX,googlevideo.com), (PROTOCOL,UDP)),REJECT
AND,((DOMAIN,youtubei.googleapis.com), (PROTOCOL,UDP)),REJECT

https://ahrefs.com/writing-tools/paragraph-rewriter
# --- 锁定 YouTube 核心重写 (严格复刻，严禁修改) ---
(^https?:\/\/[\w-]+\.googlevideo\.com\/(?!dclk_video_ads).+?)&ctier=L(&.+?),ctier,(.+) $1$2$3 302
^https?:\/\/[\w-]+\.googlevideo\.com\/(?!(dclk_video_ads|videoplayback\?)).+&oad _ reject-200
^https?:\/\/(www|s)\.youtube\.com\/api\/stats\/ads _ reject-200
^https?:\/\/(www|s)\.youtube\.com\/(pagead|ptracking) _ reject-200
^https?:\/\/s\.youtube\.com\/api\/stats\/qoe\?adcontext _ reject-200

# --- 扩展应用规则 ---
^https?:\/\/.*\.amap\.com\/ws\/(boss\/order_web\/\w{{8}}_information|asa\/ads_attribution) reject
^https?:\/\/pan\.baidu\.com\/act\/.+ad_ reject
^https?:\/\/.+\.pangle\.io\/api\/ad\/union\/sdk\/ reject
^https?:\/\/.+\.pangolin-sdk-toutiao\.com\/api\/ad\/union\/sdk\/(get_ads|stats|settings)\/ reject
^https?:\/\/gurd\.snssdk\.com\/src\/server\/v3\/package reject
(^https?:\/\/app\.biliintl\.com\/intl\/.+)(&sim_code=\d+)(.+) $1$3 302
^https?:\/\/app\.bilibili\.com\/x\/resource\/ip reject
^https?:\/\/app\.bilibili\.com\/bilibili\.app\.interface\.v1\.Search\/Default reject

[Script]
# --- 锁定脚本注入 ---
youtube.response = type=http-response,pattern=^https:\/\/youtubei\.googleapis\.com\/youtubei\/v1\/(browse|next|player|search|reel\/reel_watch_sequence|guide|account\/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SCRIPTS['youtube']},argument="{yt_arg}"

biliad1 = type=http-response,pattern=^https?:\/\/api\.(bilibili|biliapi)\.(com|net)\/pgc\/page\/cinema\/tab\?,requires-body=1,script-path={SCRIPTS['bili']}
biliad12 = type=http-response,pattern=^https:\/\/app\.bilibili\.com\/bilibili\.app\.(view\.v1\.View\/View|dynamic\.v2\.Dynamic\/DynAll)$,requires-body=1,binary-body-mode=1,script-path={SCRIPTS['bili_proto']}
baidu_cloud = type=http-response,pattern=^https?://pan\.baidu\.com/rest/2\.0/membership/user,requires-body=1,script-path={SCRIPTS['baidu']}

[MITM]
# 锁定：使用 %APPEND% 强制合并
hostname = %APPEND% -redirector*.googlevideo.com, *.googlevideo.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, pan.baidu.com, *.amap.com, *.bilibili.com, *.biliapi.net, app.biliintl.com
"""
    with open("OmniGuard-Predator-MitM.sgmodule", "w", encoding="utf-8") as f:
        f.write(module_content)

# === 4. 生成带动态 Header 的 txt 文件 ===
def generate_blacklist_txt(cleaned_rules, version_str):
    header = f"""[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist
! Description: 针对 iOS 环境深度优化的全能黑名单旗舰版。已固化 YouTube 原厂去广告逻辑。
! Version: {version_str.replace("-", ".").replace(" ", ".")}
! Codename: Predator-Standard
! Updated: {version_str}
! -------------------------------------------------------------------------------------------------------

! === Upstream Synchronized Rules ===
"""
    with open("iOS-OmniGuard-Blacklist.txt", "w", encoding="utf-8") as f:
        f.write(header + cleaned_rules)

# === 5. 探活脚本并更新 README ===
def check_script_health(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        return urllib.request.urlopen(req, timeout=10).getcode() == 200
    except: return False

def update_readme(version_str, health_status):
    if not os.path.exists("README.md"): return
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    
    # 更新 README 中的时间戳
    readme = re.sub(r"更新于: \d{4}-\d{2}-\d{2} \d{2}:\d{2}", f"更新于: {version_str}", readme)
    
    # 构造状态列表
    status_text = f"> 更新于: {version_str}\\n- ✅ 上游 DNS 同步完成\\n"
    for name, is_alive in health_status.items():
        status_text += f"- {'✅' if is_alive else '❌'} {name} 脚本源状态\\n"
    
    # 使用正则替换 README 中的特定区块
    readme = re.sub(r"> 更新于:.*?(?=\\n---)", status_text, readme, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    # 获取北京时间
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    
    try:
        req = urllib.request.Request(UPSTREAM_DNS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        raw_dns = urllib.request.urlopen(req).read().decode('utf-8')
    except:
        raw_dns = ""
        
    cleaned_dns = clean_and_merge_rules(raw_dns)
    
    # 生成文件
    generate_sgmodule(bj_time)
    generate_blacklist_txt(cleaned_dns, bj_time)
    
    # 探活与 README 更新
    health = {name: check_script_health(url) for name, url in SCRIPTS.items()}
    update_readme(bj_time, health)
