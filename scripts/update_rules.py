import os
import re
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor

# === 配置区 ===
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

# 需要检测健康状态的外部链接列表
CHECK_LIST = [
    "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/bilibili.enhance.js",
    "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "https://github.com/ddgksf2013/Scripts/raw/master/amap.js",
    "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
]

# === 核心逻辑：多线程链接健康检测 ===
def check_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}
    try:
        # 使用 Session 复用连接，增加超时容错
        with requests.Session() as s:
            resp = s.head(url, headers=headers, timeout=10, allow_redirects=True)
            if resp.status_code >= 400:
                resp = s.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return None  # 正常
            return f"{url} [{resp.status_code}]"
    except Exception as e:
        return f"{url} (Error: {str(e)})"

def get_failed_urls():
    print(f"🔍 正在并行检测 {len(CHECK_LIST)} 个外部资源健康状态...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_url, CHECK_LIST))
    
    failed = [r for r in results if r is not None]
    if not failed:
        print("✨ 所有外部脚本资源均在线。")
    else:
        for f in failed: print(f"❌ 链接异常: {f}")
    return failed

# === 核心逻辑：黑名单去重处理 ===
def process_blacklist():
    print(f"⏳ 正在同步黑名单并去重...")
    try:
        upstream_resp = requests.get(UPSTREAM_URL, timeout=30)
        upstream_rules = set([l.strip() for l in upstream_resp.text.splitlines() if l.strip() and not l.startswith(('!', '#'))])
    except Exception as e:
        print(f"❌ 拉取上游规则失败: {e}")
        return

    if not os.path.exists(BLACKLIST_FILE): return
    
    with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    removed_count = 0
    # 预编译正则提高效率
    special_rule_re = re.compile(r'\$important|##|#%#|@@')

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(('!', '[')):
            new_lines.append(line); continue
        if special_rule_re.search(stripped):
            new_lines.append(line); continue
        if stripped in upstream_rules:
            removed_count += 1; continue
        new_lines.append(line)

    # 更新元数据
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    version_str, time_str = now.strftime("%Y.%m.%d.%H"), now.strftime("%Y-%m-%d %H:%M")
    
    content = "".join(new_lines)
    content = re.sub(r'! Version: .*', f'! Version: {version_str}', content)
    content = re.sub(r'! Updated: .*', f'! Updated: {time_str}', content)

    with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 黑名单处理完成，剔除 {removed_count} 条重复项。版本: {version_str}")

# === 核心逻辑：MitM 模块集成 ===
def generate_mitm_module(failed_urls):
    print(f"⏳ 正在生成 OmniGuard MitM 模块...")
    
    warning_block = ""
    if failed_urls:
        warning_block = "# 🚨 [WARNING] Detection failed for:\n" + "".join([f"# ! {u}\n" for u in failed_urls]) + "\n"

    # 使用 Raw String 结合 Double Braces 彻底解决正则转义与 f-string 冲突
    module_template = f"""{warning_block}#!name = iOS-OmniGuard Predator-MitM (2026 终极全能版)
#!desc = 集成：高德净化、微信解锁、YouTube(后台/PiP)、Bilibili(4K解锁/去广告)、百度网盘(倍速)、七猫(VIP)、番茄(深度净化)。
#!category = OmniGuard
#!author = MEyifan20 & Maasea & ddgksf2013 & Choler
#!system = ios

[Rule]
AND,((DOMAIN-SUFFIX,googlevideo.com), (PROTOCOL,UDP)),REJECT
AND,((DOMAIN-KEYWORD,youtubei), (PROTOCOL,UDP)),REJECT
AND,((DOMAIN-SUFFIX,biliapi.net), (PROTOCOL,UDP)),REJECT
AND,((DOMAIN-SUFFIX,amap.com), (PROTOCOL,UDP)),REJECT
DOMAIN,p6-ad-sign.byteimg.com,REJECT
DOMAIN,p9-ad-sign.byteimg.com,REJECT
DOMAIN-SUFFIX,byteimg.com,DIRECT
DOMAIN-KEYWORD,zijieapi,REJECT
DOMAIN-SUFFIX,pglstatp-toutiao.com,REJECT
IP-CIDR,49.71.37.101/32,REJECT,no-resolve

https://ahrefs.com/writing-tools/paragraph-rewriter
^https?://.*\\.amap\\.com/ws/(boss/order_web/\\w{{8}}_information|asa/ads_attribution|shield/scene/recommend) _ reject
^https?://pan\\.baidu\\.com/act/.+ad_ - reject
^https?://api\\.zhihu\\.com/commercial_api/real_time_zone - reject-dict
^https?://btrace\\.video\\.qq\\.com/kvcollect - reject
^https?://t7z\\.cupid\\.iqiyi\\.com/.* - reject-dict
^https?://edith\\.xiaohongshu\\.com/api/sns/v\\d/system_service/splash_config - reject-dict
^https?://.+\\.pangolin-sdk-toutiao\\.com/api/ad/union/sdk/(get_ads|stats/settings)/ - reject
^https?://api-ks\\.qimao\\.com/.* - reject-dict
^https?://wtw\\.qimao\\.com/api/ad/.* - reject-dict
(^https?://[\\w-]+\\.googlevideo\\.com/(?!dclk_video_ads).+?)&ctier=L(&.+?),ctier,(.+) $1$2$3 302
^https?://[\\w-]+\\.googlevideo\\.com/(?!(dclk_video_ads|videoplayback\\?)).+&oad _ reject-200
^https?://s\\.youtube\\.com/api/stats/qoe\\?adcontext _ reject-200

[Script]
bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll|interface\\.v1\\.Search/Default|resource\\.show\\.v1\\.Tab/GetTabs|account\\.v1\\.Account/Mine)$,requires-body=1,binary-body-mode=1,script-path=https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/bilibili.enhance.js
youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player|search|reel/reel_watch_sequence|guide|account/get_setting/get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path=https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js,argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}}"
amap_ad = type=http-response,pattern=^https?://.*\\.amap\\.com/ws/(faas/amap-navigation/main-page|valueadded/alimama/splash_screen|msgbox/pull|shield/(shield/dsp/profile/index/nodefaas|search/new_hotword)),requires-body=1,script-path=https://github.com/ddgksf2013/Scripts/raw/master/amap.js
unblock_wechat = type=http-response,pattern=^https\\:\\/\\/(weixin110\\.qq|security.wechat)\\.com\\/cgi-bin\\/mmspamsupport-bin\\/newredirectconfirmcgi\\?,requires-body=1,max-size=0,script-path=https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js,argument="useCache=true&forceRedirect=true"
baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path=https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js
qimao_vip = type=http-response,pattern=^https?://(api-\\w+|xiaoshuo)\\.wtzw\\.com/api/v\\d/,requires-body=1,script-path=https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js

[MITM]
hostname = %APPEND% *amap.com, security.wechat.com, weixin110.qq.com, pan.baidu.com, app.bilibili.com, api.live.bilibili.com, api.vc.bilibili.com, api.bilibili.com, manga.bilibili.com, grpc.biliapi.net, api.biliapi.net, -broadcast.chat.bilibili.com, api.zhihu.com, btrace.video.qq.com, t7z.cupid.iqiyi.com, ad.api.3g.youku.com, *ad-sign.byteimg.com, *ad.bytebe.com, api-ks.qimao.com, wtw.qimao.com, edith.xiaohongshu.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, -*redirector*.googlevideo.com, *.googlevideo.com, *.wtzw.com, *.pangolin-sdk-toutiao, *.pstatp.com, gurd.snssdk.com
"""
    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f:
        f.write(module_template)
    print(f"✅ MitM 模块生成完毕。")

def update_readme():
    if not os.path.exists(README_FILE): return
    time_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'\*\*最后修改时间\*\*：.*', f'**最后修改时间**：{time_str} (GMT+8)', content)
    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ README 已更新最后修改时间。")

if __name__ == '__main__':
    failed = get_failed_urls()
    process_blacklist()
    generate_mitm_module(failed)
    update_readme()
