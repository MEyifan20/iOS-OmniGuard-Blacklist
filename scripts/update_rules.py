import os, datetime, requests

# === 基础配置 ===
REPO_FULL_NAME = os.environ.get('GITHUB_REPOSITORY', 'MEyifan20/iOS-OmniGuard-Blacklist')
UPSTREAM_URL = "https://raw.githubusercontent.com/217heidai/adblockdns/main/rule/adblockdns.txt"
BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

SOURCES = {
    "bili": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "baidu": "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "qimao": "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

def main():
    print("🚀 启动核弹级稳定版...")
    tz = datetime.timezone(datetime.timedelta(hours=8))
    t_now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    v_now = datetime.datetime.now(tz).strftime("%Y.%m.%d.%H")

    # 1. 更新黑名单文件 (逐行扫描，不报异常)
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
                for line in lines:
                    if '! Version:' in line: f.write(f"! Version: {v_now}\n")
                    elif '! Updated:' in line: f.write(f"! Updated: {t_now}\n")
                    else: f.write(line)
            print("📅 黑名单日期已更新")
        except: print("⚠️ 黑名单更新跳过")

    # 2. 构造模块内容 (采用手动拼接，避开 f-string 转义陷阱)
    script_part = []
    script_part.append(f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll|interface\\.v1\\.Search/Default|resource\\.show\\.v1\\.Tab/GetTabs|account\\.v1\\.Account/Mine)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}')
    script_part.append(f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player|search|reel/reel_watch_sequence|guide|account/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},argument="{{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true,\\"blockImmersive\\":true,\\"debug\\":false}}"')
    script_part.append(f'amap_ad = type=http-response,pattern=^https?://.*\\.amap\\.com/ws/(faas/amap-navigation/main-page|valueadded/alimama/splash_screen|msgbox/pull|shield/(shield/dsp/profile/index/nodefaas|search/new_hotword)),requires-body=1,script-path={SOURCES["amap"]}')
    script_part.append(f'unblock_wechat = type=http-response,pattern=^https\\:\\/\\/(weixin110\\.qq|security.wechat)\\.com\\/cgi-bin\\/mmspamsupport-bin\\/newredirectconfirmcgi\\?,requires-body=1,max-size=0,script-path={SOURCES["wechat"]},argument="useCache=true&forceRedirect=true"')
    script_part.append(f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}')
    script_part.append(f'qimao_vip = type=http-response,pattern=^https?://(api-\\w+|xiaoshuo)\\.wtzw\\.com/api/v\\d/,requires-body=1,script-path={SOURCES["qimao"]}')

    module_text = """#!name = iOS-OmniGuard Predator-MitM
#!desc = 模块状态: 🟢 正常 | 更新时间: {TIME}
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

https://monica.im/en/tools/rewrite-text
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
{SCRIPTS}

[MITM]
hostname = %APPEND% *amap.com, security.wechat.com, weixin110.qq.com, pan.baidu.com, app.bilibili.com, api.live.bilibili.com, api.vc.bilibili.com, api.bilibili.com, manga.bilibili.com, grpc.biliapi.net, api.biliapi.net, -broadcast.chat.bilibili.com, api.zhihu.com, btrace.video.qq.com, t7z.cupid.iqiyi.com, ad.api.3g.youku.com, *ad-sign.byteimg.com, *ad.bytebe.com, api-ks.qimao.com, wtw.qimao.com, edith.xiaohongshu.com, www.youtube.com, s.youtube.com, youtubei.googleapis.com, -*redirector*.googlevideo.com, *.googlevideo.com, *.wtzw.com, *.pangolin-sdk-toutiao, *.pstatp.com, gurd.snssdk.com
"""
    # 使用 replace 代替 f-string，避开转义错误
    final_module = module_text.replace("{TIME}", t_now).replace("{SCRIPTS}", "\n".join(script_part))
    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f:
        f.write(final_module)

    # 3. 更新 README (最简逻辑)
    if os.path.exists(README_FILE):
        try:
            with open(README_FILE, 'r', encoding='utf-8') as f:
                r_lines = f.readlines()
            with open(README_FILE, 'w', encoding='utf-8') as f:
                for line in r_lines:
                    if '**最后修改时间**：' in line:
                        f.write(f"**最后修改时间**：{t_now} (GMT+8)\n")
                    else: f.write(line)
        except: print("⚠️ README 更新跳过")
    
    print("✅ 执行完成")

if __name__ == '__main__':
    main()
