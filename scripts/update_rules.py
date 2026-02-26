import os, re, datetime, requests
from concurrent.futures import ThreadPoolExecutor

# === 自动获取环境变量 ===
REPO_FULL_NAME = os.environ.get('GITHUB_REPOSITORY', 'MEyifan20/iOS-OmniGuard-Blacklist')
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

# 严苛模式：404 不写入模块，确保手机端可用
STRICT_MODE = True

# === 2026 最终校对后的绝对路径 (增加缓存刷新参数) ===
SOURCES = {
    "bili": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://github.com/ddgksf2013/Scripts/raw/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "baidu": "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "qimao": "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

COMMON_HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU OS 17_6 like Mac OS X) AppleWebKit/605.1.15'}
update_logs = []

def check_url(item):
    name, url = item
    # 增加随机数防止 CDN 缓存 404 页面
    test_url = f"{url}?t={datetime.datetime.now().timestamp()}"
    try:
        resp = requests.get(test_url, headers=COMMON_HEADERS, timeout=15)
        if resp.status_code == 200:
            return name, True
        update_logs.append(f"❌ {name} 失效 [HTTP {resp.status_code}]")
        return name, False
    except Exception as e:
        update_logs.append(f"⚠️ {name} 超时: {str(e)[:20]}")
        return name, False

def process_blacklist():
    print("⏳ 正在深度同步并更新时间戳...")
    try:
        upstream_resp = requests.get(UPSTREAM_URL, headers=COMMON_HEADERS, timeout=30)
        upstream_rules = set([l.strip() for l in upstream_resp.text.splitlines() if l.strip() and not l.startswith(('!', '#'))])
    except:
        update_logs.append("⚠️ 上游拉取失败")
        return

    if not os.path.exists(BLACKLIST_FILE): return
    with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 获取北京时间
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    version_str = now.strftime("%Y.%m.%d.%H")
    time_str = now.strftime("%Y-%m-%d %H:%M")

    # --- 终极正则：无视空格、无视位置、无视大小写 ---
    content = re.sub(r'(?i)(!\s*Version\s*:\s*).*', rf'\1{version_str}', content)
    content = re.sub(r'(?i)(!\s*Updated\s*:\s*).*', rf'\1{time_str}', content)

    # 处理去重
    lines = content.splitlines()
    new_lines = []
    removed_count = 0
    # 仅对普通的域名规则进行去重，保留元数据和高级规则
    for line in lines:
        stripped = line.strip()
        if stripped and not any(x in stripped for x in ['!', '[', '$', '#', '@']):
            if stripped in upstream_rules:
                removed_count += 1
                continue
        new_lines.append(line)

    with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines))
    if removed_count > 0: update_logs.append(f"🧹 自动剔除重复规则 {removed_count} 条")

def generate_mitm_module(health):
    print("⏳ 正在重新编译模块...")
    s_entries = []
    # 这里的键名必须与 SOURCES 保持一致
    if health.get("bili"): s_entries.append(f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll|interface\\.v1\\.Search/Default|resource\\.show\\.v1\\.Tab/GetTabs|account\\.v1\\.Account/Mine)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}')
    if health.get("youtube"): s_entries.append(f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player|search|reel/reel_watch_sequence|guide|account/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}}"')
    if health.get("amap"): s_entries.append(f'amap_ad = type=http-response,pattern=^https?://.*\\.amap\\.com/ws/(faas/amap-navigation/main-page|valueadded/alimama/splash_screen|msgbox/pull|shield/(shield/dsp/profile/index/nodefaas|search/new_hotword)),requires-body=1,script-path={SOURCES["amap"]}')
    if health.get("wechat"): s_entries.append(f'unblock_wechat = type=http-response,pattern=^https\\:\\/\\/(weixin110\\.qq|security.wechat)\\.com\\/cgi-bin\\/mmspamsupport-bin\\/newredirectconfirmcgi\\?,requires-body=1,max-size=0,script-path={SOURCES["wechat"]},argument="useCache=true&forceRedirect=true"')
    if health.get("baidu"): s_entries.append(f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}')
    if health.get("qimao"): s_entries.append(f'qimao_vip = type=http-response,pattern=^https?://(api-\\w+|xiaoshuo)\\.wtzw\\.com/api/v\\d/,requires-body=1,script-path={SOURCES["qimao"]}')

    valid_count = len(s_entries)
    module_content = f"""#!name = iOS-OmniGuard Predator-MitM
#!desc = 状态: {"🟢 正常" if valid_count==6 else f"🟠 {valid_count}/6 运行中"} | 更新: {datetime.datetime.now().strftime('%m-%d %H:%M')} | 4K/倍速/解锁已全集成。
#!category = OmniGuard
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
{"\n".join(s_entries)}

[MITM]
hostname = %APPEND% *amap.com, security.wechat.com, weixin110.qq.com, pan.baidu.com, app.bilibili.com, api.live.bilibili.com, api.vc.bilibili.com, api.bilibili.com, manga.bilibili.com, grpc.biliapi.net, api.biliapi.net, -broadcast.chat.bilibili.com, api.zhihu.com, btrace.video.qq.com, t7z.cupid.iqiyi.com, ad.api.3g.youku.com, *ad-sign.byteimg.com, *ad.bytebe.com, api-ks.qimao.com, wtw.qimao.com, edith.xiaohongshu.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, -*redirector*.googlevideo.com, *.googlevideo.com, *.wtzw.com, *.pangolin-sdk-toutiao, *.pstatp.com, gurd.snssdk.com
"""
    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(module_content)

def update_readme():
    if not os.path.exists(README_FILE): return
    time_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    cdn_mitm = f"https://cdn.jsdelivr.net/gh/{REPO_FULL_NAME}@main/{MITM_MODULE_FILE}"
    cdn_dns = f"https://cdn.jsdelivr.net/gh/{REPO_FULL_NAME}@main/{BLACKLIST_FILE}"
    
    with open(README_FILE, 'r', encoding='utf-8') as f: content = f.read()
    content = re.sub(r'(?i)(\*\*最后修改时间\*\*：).*', rf'\1{time_str} (GMT+8)', content)
    
    cdn_h = "## 🚀 全自动 CDN 订阅地址"
    cdn_b = f"\n{cdn_h}\n- **Predator-MitM 模块**: `{cdn_mitm}`\n- **DNS 黑名单**: `{cdn_dns}`\n"
    content = re.sub(f"{cdn_h}.*?txt`", cdn_b.strip(), content, flags=re.DOTALL) if cdn_h in content else content + cdn_b

    log_h = "## 📅 最近更新动态"
    log_b = f"\n{log_h}\n> 更新于: {time_str}\n\n" + "\n".join([f"- {item}" for item in update_logs]) + "\n"
    content = re.sub(f"{log_h}.*?(?=\n##|$)", log_b, content, flags=re.DOTALL) if log_h in content else content + log_b
    with open(README_FILE, 'w', encoding='utf-8') as f: f.write(content)

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=6) as executor:
        health_status = dict(executor.map(check_url, SOURCES.items()))
    process_blacklist()
    generate_mitm_module(health_status)
    update_readme()
