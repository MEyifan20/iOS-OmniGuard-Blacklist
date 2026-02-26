import os, re, datetime, requests
from concurrent.futures import ThreadPoolExecutor

# === 自动获取环境变量 (无人值守核心) ===
REPO_FULL_NAME = os.environ.get('GITHUB_REPOSITORY', 'MEyifan20/iOS-OmniGuard-Blacklist')
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

# === 2026 最终实测有效路径 (修正 404) ===
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
    try:
        # 增加随机戳强行刷新 CDN 缓存，确保探测真实状态
        ts_url = f"{url}?t={datetime.datetime.now().timestamp()}"
        resp = requests.get(ts_url, headers=COMMON_HEADERS, timeout=12)
        if resp.status_code == 200:
            return name, True
        update_logs.append(f"❌ {name} 失效 [HTTP {resp.status_code}]")
        return name, False
    except:
        update_logs.append(f"⚠️ {name} 超时")
        return name, False

def process_blacklist():
    print("⏳ [复查] 正在深度处理黑名单时间戳与去重...")
    try:
        # 加长超时，确保网络波动不挂断
        up_resp = requests.get(UPSTREAM_URL, headers=COMMON_HEADERS, timeout=30)
        up_rules = set([l.strip() for l in up_resp.text.splitlines() if l.strip() and not l.startswith(('!', '#'))])
    except:
        update_logs.append("⚠️ 上游拉取失败，跳过去重")
        up_rules = set()

    if not os.path.exists(BLACKLIST_FILE): return

    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    v_str, t_str = now.strftime("%Y.%m.%d.%H"), now.strftime("%Y-%m-%d %H:%M")

    with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
        old_lines = f.readlines()

    new_lines = []
    removed_count = 0
    
    # 采用逐行精确扫描替换，规避全局正则失效
    for line in old_lines:
        s_line = line.strip()
        # 覆盖所有可能的元数据写法
        if s_line.startswith('!') and 'Version' in s_line:
            new_lines.append(f"! Version: {v_str}\n")
        elif s_line.startswith('!') and 'Updated' in s_line:
            new_lines.append(f"! Updated: {t_str}\n")
        # 去重逻辑：仅处理纯规则行
        elif s_line and not any(x in s_line for x in ['!', '[', '$', '#', '@']):
            if s_line in up_rules:
                removed_count += 1
                continue
            new_lines.append(line)
        else:
            new_lines.append(line)

    with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    if removed_count > 0: update_logs.append(f"🧹 剔除重复规则 {removed_count} 条")
    update_logs.append(f"📅 黑名单时间戳已刷新至 {t_str}")

def generate_mitm_module(health):
    print("⏳ [复查] 正在编译集成模块...")
    s_block = []
    # 像素级校对每个脚本条目的转义字符
    if health.get("bili"): s_block.append(f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll|interface\\.v1\\.Search/Default|resource\\.show\\.v1\\.Tab/GetTabs|account\\.v1\\.Account/Mine)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}')
    if health.get("youtube"): s_block.append(f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player|search|reel/reel_watch_sequence|guide|account/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}}"')
    if health.get("amap"): s_block.append(f'amap_ad = type=http-response,pattern=^https?://.*\\.amap\\.com/ws/(faas/amap-navigation/main-page|valueadded/alimama/splash_screen|msgbox/pull|shield/(shield/dsp/profile/index/nodefaas|search/new_hotword)),requires-body=1,script-path={SOURCES["amap"]}')
    if health.get("wechat"): s_block.append(f'unblock_wechat = type=http-response,pattern=^https\\:\\/\\/(weixin110\\.qq|security.wechat)\\.com\\/cgi-bin\\/mmspamsupport-bin\\/newredirectconfirmcgi\\?,requires-body=1,max-size=0,script-path={SOURCES["wechat"]},argument="useCache=true&forceRedirect=true"')
    if health.get("baidu"): s_block.append(f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}')
    if health.get("qimao"): s_block.append(f'qimao_vip = type=http-response,pattern=^https?://(api-\\w+|xiaoshuo)\\.wtzw\\.com/api/v\\d/,requires-body=1,script-path={SOURCES["qimao"]}')

    scripts_str = "\n".join(s_block)
    module_body = f"""#!name = iOS-OmniGuard Predator-MitM
#!desc = 状态: {"🟢 正常" if len(s_block)==6 else "🟠 部分异常"} | 更新: {datetime.datetime.now().strftime('%m-%d %H:%M')}
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
{scripts_str}

[MITM]
hostname = %APPEND% *amap.com, security.wechat.com, weixin110.qq.com, pan.baidu.com, app.bilibili.com, api.live.bilibili.com, api.vc.bilibili.com, api.bilibili.com, manga.bilibili.com, grpc.biliapi.net, api.biliapi.net, -broadcast.chat.bilibili.com, api.zhihu.com, btrace.video.qq.com, t7z.cupid.iqiyi.com, ad.api.3g.youku.com, *ad-sign.byteimg.com, *ad.bytebe.com, api-ks.qimao.com, wtw.qimao.com, edith.xiaohongshu.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, -*redirector*.googlevideo.com, *.googlevideo.com, *.wtzw.com, *.pangolin-sdk-toutiao, *.pstatp.com, gurd.snssdk.com
"""
    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(module_body)

def update_readme():
    if not os.path.exists(README_FILE): return
    time_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    cdn_m = f"https://cdn.jsdelivr.net/gh/{REPO_FULL_NAME}@main/{MITM_MODULE_FILE}"
    cdn_d = f"https://cdn.jsdelivr.net/gh/{REPO_FULL_NAME}@main/{BLACKLIST_FILE}"
    
    with open(README_FILE, 'r', encoding='utf-8') as f: readme_raw = f.read()
    
    # 使用行匹配更新 README 时间，更稳定
    readme_lines = readme_raw.splitlines()
    new_readme = []
    for rl in readme_lines:
        if '**最后修改时间**：' in rl:
            new_readme.append(f"**最后修改时间**：{time_str} (GMT+8)")
        else:
            new_readme.append(rl)
    
    final_readme = "\n".join(new_readme)
    
    # 动态注入 CDN 与日志块 (使用稳健匹配)
    cdn_h = "## 🚀 全自动 CDN 订阅地址"
    cdn_b = f"\n{cdn_h}\n- **Predator-MitM 模块**: `{cdn_m}`\n- **DNS 黑名单**: `{cdn_d}`\n"
    if cdn_h in final_readme:
        final_readme = re.sub(f"{cdn_h}.*?txt`", cdn_b.strip(), final_readme, flags=re.DOTALL)
    else:
        final_readme += cdn_body

    log_h = "## 📅 最近更新动态"
    log_b = f"\n{log_h}\n> 更新于: {time_str}\n\n" + "\n".join([f"- {item}" for item in update_logs]) + "\n"
    if log_h in final_readme:
        final_readme = re.sub(f"{log_h}.*?(?=\n##|$)", log_b, final_readme, flags=re.DOTALL)
    else:
        final_readme += log_b
        
    with open(README_FILE, 'w', encoding='utf-8') as f: f.write(final_readme)

if __name__ == '__main__':
    try:
        with ThreadPoolExecutor(max_workers=6) as executor:
            health_map = dict(executor.map(check_url, SOURCES.items()))
        process_blacklist()
        generate_mitm_module(health_map)
        update_readme()
        print("✅ 全自动化流程执行成功！")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        exit(1)
