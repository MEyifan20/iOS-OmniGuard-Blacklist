import os
import re
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor

# === 自动获取环境变量 ===
REPO_FULL_NAME = os.environ.get('GITHUB_REPOSITORY', 'MEyifan20/iOS-OmniGuard-Blacklist')
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

CHECK_LIST = [
    "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/bilibili.enhance.js",
    "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "https://github.com/ddgksf2013/Scripts/raw/master/amap.js",
    "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
]

COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
}

# 全局变量用于存储更新日志摘要
update_logs = []

def check_url(url):
    try:
        with requests.Session() as s:
            resp = s.get(url, headers=COMMON_HEADERS, timeout=12)
            if resp.status_code == 200:
                return None
            msg = f"链接失效: {url.split('/')[-1]} [{resp.status_code}]"
            update_logs.append(f"❌ {msg}")
            return f"{url} [{resp.status_code}]"
    except Exception as e:
        update_logs.append(f"⚠️ 网络超时: {url.split('/')[-1]}")
        return f"{url} (Timeout)"

def process_blacklist():
    print("⏳ 正在同步黑名单...")
    try:
        upstream_resp = requests.get(UPSTREAM_URL, headers=COMMON_HEADERS, timeout=30)
        upstream_rules = set([l.strip() for l in upstream_resp.text.splitlines() if l.strip() and not l.startswith(('!', '#'))])
    except:
        update_logs.append("⚠️ 无法连接上游 DNS 仓库，跳过本轮去重。")
        return

    if not os.path.exists(BLACKLIST_FILE): return
    with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
        old_content = f.read()
        lines = old_content.splitlines()

    new_lines = []
    removed_count = 0
    special_rule_re = re.compile(r'\$important|##|#%#|@@')

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(('!', '[')) or special_rule_re.search(stripped):
            new_lines.append(line); continue
        if stripped in upstream_rules:
            removed_count += 1; continue
        new_lines.append(line)

    if removed_count > 0:
        update_logs.append(f"🧹 黑名单优化：自动剔除 {removed_count} 条与上游重复的规则。")

    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    version_str, time_str = now.strftime("%Y.%m.%d.%H"), now.strftime("%Y-%m-%d %H:%M")
    
    content = "\n".join(new_lines)
    content = re.sub(r'! Version: .*', f'! Version: {version_str}', content)
    content = re.sub(r'! Updated: .*', f'! Updated: {time_str}', content)

    with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_mitm_module(failed_urls):
    print("⏳ 正在生成 MitM 模块...")
    status_emoji = "🟢" if not failed_urls else "🟠"
    if not failed_urls:
        update_logs.append("✅ 核心脚本健康检测通过，所有外部资源在线。")
    
    module_template = f"""#!name = iOS-OmniGuard Predator-MitM
#!desc = 状态: {"正常" if not failed_urls else "部分异常"} | 更新: {datetime.datetime.now().strftime('%m-%d %H:%M')} | 自动同步 Maasea 等资源。
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

def update_readme():
    if not os.path.exists(README_FILE): return
    time_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    cdn_mitm = f"https://cdn.jsdelivr.net/gh/{REPO_FULL_NAME}@main/{MITM_MODULE_FILE}"
    cdn_dns = f"https://cdn.jsdelivr.net/gh/{REPO_FULL_NAME}@main/{BLACKLIST_FILE}"

    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 更新最后修改时间
    content = re.sub(r'\*\*最后修改时间\*\*：.*', f'**最后修改时间**：{time_str} (GMT+8)', content)

    # 2. 更新 CDN 地址
    cdn_header = "## 🚀 全自动 CDN 订阅地址"
    cdn_body = f"\n{cdn_header}\n- **Predator-MitM 模块**: `{cdn_mitm}`\n- **DNS 黑名单**: `{cdn_dns}`\n"
    if cdn_header in content:
        content = re.sub(f"{cdn_header}.*?txt`", cdn_body.strip(), content, flags=re.DOTALL)
    else:
        content += cdn_body

    # 3. 更新自动生成的【最近更新动态】
    log_header = "## 📅 最近更新动态"
    log_content = f"\n{log_header}\n> 更新于: {time_str}\n\n" + "\n".join([f"- {item}" for item in update_logs]) + "\n"
    
    if log_header in content:
        # 使用正则表达式替换旧的 Log 区域
        content = re.sub(f"{log_header}.*?(?=\n##|$)", log_content, content, flags=re.DOTALL)
    else:
        content += log_content

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ README.md 更新动态已同步。")

if __name__ == '__main__':
    update_logs.append("🚀 开始自动化执行构建任务...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_failed = executor.submit(lambda: [r for r in list(map(check_url, CHECK_LIST)) if r])
        process_blacklist()
        failed_urls = future_failed.result()
    generate_mitm_module(failed_urls)
    update_logs.append("📦 所有规则文件编译完成。")
    update_readme()
