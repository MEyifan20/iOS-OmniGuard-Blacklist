import os, re, datetime, requests

# === 核心配置 ===
REPO_FULL_NAME = os.environ.get('GITHUB_REPOSITORY', 'MEyifan20/iOS-OmniGuard-Blacklist')
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

# === 回归最稳路径 ===
SOURCES = {
    "bili": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "baidu": "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "qimao": "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

NAME_MAP = {"bili": "哔哩哔哩", "baidu": "百度网盘", "youtube": "YouTube", "amap": "高德", "wechat": "微信", "qimao": "七猫"}

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU OS 18_0 like Mac OS X)'}
update_logs = []
failed_modules = [] 

def check_url_simple(name, url):
    try:
        # 即使 404 也不要让程序死掉
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return True
        failed_modules.append(NAME_MAP[name])
        update_logs.append(f"❌ {NAME_MAP[name]} 探测异常 [{resp.status_code}]")
        return False
    except:
        failed_modules.append(NAME_MAP[name])
        update_logs.append(f"⚠️ {NAME_MAP[name]} 超时")
        return False

def main():
    print("🚀 启动最终稳定版程序...")
    
    # 1. 检测链接
    health = {}
    for name, url in SOURCES.items():
        health[name] = check_url_simple(name, url)

    # 2. 处理黑名单时间戳
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    v_str, t_str = now.strftime("%Y.%m.%d.%H"), now.strftime("%Y-%m-%d %H:%M")

    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
            for line in lines:
                if '! Version:' in line: f.write(f"! Version: {v_str}\n")
                elif '! Updated:' in line: f.write(f"! Updated: {t_str}\n")
                else: f.write(line)
        update_logs.append(f"📅 黑名单时间戳已刷新")

    # 3. 生成模块
    entries = []
    entries.append(f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll|interface\\.v1\\.Search/Default|resource\\.show\\.v1\\.Tab/GetTabs|account\\.v1\\.Account/Mine)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}')
    entries.append(f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player|search|reel/reel_watch_sequence|guide|account/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}}"')
    entries.append(f'amap_ad = type=http-response,pattern=^https?://.*\\.amap\\.com/ws/(faas/amap-navigation/main-page|valueadded/alimama/splash_screen|msgbox/pull|shield/(shield/dsp/profile/index/nodefaas|search/new_hotword)),requires-body=1,script-path={SOURCES["amap"]}')
    entries.append(f'unblock_wechat = type=http-response,pattern=^https\\:\\/\\/(weixin110\\.qq|security.wechat)\\.com\\/cgi-bin\\/mmspamsupport-bin\\/newredirectconfirmcgi\\?,requires-body=1,max-size=0,script-path={SOURCES["wechat"]},argument="useCache=true&forceRedirect=true"')
    entries.append(f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}')
    entries.append(f'qimao_vip = type=http-response,pattern=^https?://(api-\\w+|xiaoshuo)\\.wtzw\\.com/api/v\\d/,requires-body=1,script-path={SOURCES["qimao"]}')

    status_desc = "🟢 全量正常" if not failed_modules else f"⚠️ 源异常: {', '.join(failed_modules)}"
    module_content = f"""#!name = iOS-OmniGuard Predator-MitM
#!desc = {status_desc} | 更新: {t_str}
#!category = OmniGuard
#!system = ios

[Script]
{"\n".join(entries)}

[MITM]
hostname = %APPEND% *amap.com, security.wechat.com, weixin110.qq.com, pan.baidu.com, app.bilibili.com, api.live.bilibili.com, api.vc.bilibili.com, api.bilibili.com, manga.bilibili.com, grpc.biliapi.net, api.biliapi.net, -broadcast.chat.bilibili.com, api.zhihu.com, btrace.video.qq.com, t7z.cupid.iqiyi.com, ad.api.3g.youku.com, *ad-sign.byteimg.com, *ad.bytebe.com, api-ks.qimao.com, wtw.qimao.com, edith.xiaohongshu.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, -*redirector*.googlevideo.com, *.googlevideo.com, *.wtzw.com, *.pangolin-sdk-toutiao, *.pstatp.com, gurd.snssdk.com
"""
    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f: f.write(module_content)

    # 4. 更新 README
    if os.path.exists(README_FILE):
        with open(README_FILE, 'r', encoding='utf-8') as f: content = f.read()
        
        # 极简替换时间
        new_content = []
        for line in content.splitlines():
            if '**最后修改时间**：' in line:
                new_content.append(f"**最后修改时间**：{t_str} (GMT+8)")
            else:
                new_content.append(line)
        
        content = "\n".join(new_content)
        
        # 极简替换日志
        log_h = "## 📅 最近更新动态"
        if log_h in content:
            log_b = f"{log_h}\n> 更新于: {t_str}\n" + "\n".join([f"- {i}" for i in update_logs])
            content = re.sub(f"{log_h}.*?(?=\n##|$)", log_b, content, flags=re.DOTALL)
            
        with open(README_FILE, 'w', encoding='utf-8') as f: f.write(content)
    
    print("✅ 流程结束，未发生中断异常。")

if __name__ == '__main__':
    main()
