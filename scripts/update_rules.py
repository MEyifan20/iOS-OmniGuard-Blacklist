import os, re, datetime, requests
from concurrent.futures import ThreadPoolExecutor

# === 核心配置 ===
REPO_FULL_NAME = os.environ.get('GITHUB_REPOSITORY', 'MEyifan20/iOS-OmniGuard-Blacklist')
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

# === 2026 极限稳健路径 (使用 Statically CDN 避开 Raw 404) ===
SOURCES = {
    "bili": "https://cdn.statically.io/gh/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "baidu": "https://cdn.statically.io/gh/Choler/Surge/master/Script/BaiduCloud.js",
    "youtube": "https://cdn.statically.io/gh/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://cdn.statically.io/gh/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://cdn.statically.io/gh/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "qimao": "https://cdn.statically.io/gh/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15'}
update_logs = []

def check_url(item):
    name, url = item
    try:
        # 加上时间戳防止 CDN 强缓存
        resp = requests.get(f"{url}?v={datetime.datetime.now().microsecond}", headers=HEADERS, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 500:
            return name, True
        update_logs.append(f"❌ {name} 资源不可用 [{resp.status_code}]")
        return name, False
    except:
        update_logs.append(f"⚠️ {name} 连接超时")
        return name, False

def process_blacklist():
    if not os.path.exists(BLACKLIST_FILE): return
    
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    v_str = now.strftime("%Y.%m.%d.%H")
    t_str = now.strftime("%Y-%m-%d %H:%M")

    with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    final_lines = []
    found_upd = False
    for line in lines:
        raw_line = line.strip()
        # 暴力替换时间戳：只要是以 ! 开头且包含关键字符
        if raw_line.startswith('!') and 'Version' in raw_line:
            final_lines.append(f"! Version: {v_str}\n")
        elif raw_line.startswith('!') and 'Updated' in raw_line:
            final_lines.append(f"! Updated: {t_str}\n")
            found_upd = True
        else:
            final_lines.append(line)
            
    # 如果文件里压根没找到 Updated 标记，在头部强行插入
    if not found_upd:
        final_lines.insert(2, f"! Updated: {t_str}\n")

    with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    update_logs.append(f"📅 规则文件时间戳已强制同步: {t_str}")

def generate_mitm_module(health):
    print("⏳ 正在编译 MitM 模块...")
    entries = []
    # 采用更安全的字典取值
    if health.get("bili"):
        entries.append(f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll|interface\\.v1\\.Search/Default|resource\\.show\\.v1\\.Tab/GetTabs|account\\.v1\\.Account/Mine)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}')
    if health.get("youtube"):
        entries.append(f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player|search|reel/reel_watch_sequence|guide|account/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}}"')
    if health.get("amap"):
        entries.append(f'amap_ad = type=http-response,pattern=^https?://.*\\.amap\\.com/ws/(faas/amap-navigation/main-page|valueadded/alimama/splash_screen|msgbox/pull|shield/(shield/dsp/profile/index/nodefaas|search/new_hotword)),requires-body=1,script-path={SOURCES["amap"]}')
    if health.get("wechat"):
        entries.append(f'unblock_wechat = type=http-response,pattern=^https\\:\\/\\/(weixin110\\.qq|security.wechat)\\.com\\/cgi-bin\\/mmspamsupport-bin\\/newredirectconfirmcgi\\?,requires-body=1,max-size=0,script-path={SOURCES["wechat"]},argument="useCache=true&forceRedirect=true"')
    if health.get("baidu"):
        entries.append(f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}')
    if health.get("qimao"):
        entries.append(f'qimao_vip = type=http-response,pattern=^https?://(api-\\w+|xiaoshuo)\\.wtzw\\.com/api/v\\d/,requires-body=1,script-path={SOURCES["qimao"]}')

    module_head = f"""#!name = iOS-OmniGuard Predator-MitM
#!desc = 模块状态: {"🟢 正常" if len(entries)==6 else "🟠 部分组件下线"} | 更新: {datetime.datetime.now().strftime('%m-%d %H:%M')}
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
{"\n".join(entries)}

[MITM]
hostname = %APPEND% *amap.com, security.wechat.com, weixin110.qq.com, pan.baidu.com, app.bilibili.com, api.live.bilibili.com, api.vc.bilibili.com, api.bilibili.com, manga.bilibili.com, grpc.biliapi.net, api.biliapi.net, -broadcast.chat.bilibili.com, api.zhihu.com, btrace.video.qq.com, t7z.cupid.iqiyi.com, ad.api.3g.youku.com, *ad-sign.byteimg.com, *ad.bytebe.com, api-ks.qimao.com, wtw.qimao.com, edith.xiaohongshu.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, -*redirector*.googlevideo.com, *.googlevideo.com, *.wtzw.com, *.pangolin-sdk-toutiao, *.pstatp.com, gurd.snssdk.com
"""
    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(module_head)

def update_readme():
    if not os.path.exists(README_FILE): return
    tz = datetime.timezone(datetime.timedelta(hours=8))
    t_now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    with open(README_FILE, 'r', encoding='utf-8') as f: content = f.read()
    
    # 强制行搜索更新 README 时间
    new_content = []
    for line in content.splitlines():
        if '**最后修改时间**：' in line:
            new_content.append(f"**最后修改时间**：{t_now} (GMT+8)")
        else:
            new_content.append(line)
    
    final_md = "\n".join(new_content)
    log_h = "## 📅 最近更新动态"
    log_b = f"\n{log_h}\n> 更新于: {t_now}\n\n" + "\n".join([f"- {item}" for item in update_logs]) + "\n"
    if log_h in final_md:
        final_md = re.sub(f"{log_h}.*?(?=\n##|$)", log_b, final_md, flags=re.DOTALL)
    
    with open(README_FILE, 'w', encoding='utf-8') as f: f.write(final_md)

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=6) as executor:
        h_map = dict(executor.map(check_url, SOURCES.items()))
    process_blacklist()
    generate_mitm_module(h_map)
    update_readme()
