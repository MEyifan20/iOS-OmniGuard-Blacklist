import os, datetime, requests

# === 1. 资源配置 (如果这些 404，脚本会自动冻结旧版本) ===
SOURCES = {
    "bili": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Bilibili/Bilibili.js",
    "youtube": "https://raw.githubusercontent.com/Maasea/sgmodule/master/Script/Youtube/youtube.response.js",
    "amap": "https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js",
    "wechat": "https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js",
    "baidu": "https://raw.githubusercontent.com/Choler/Surge/master/Script/BaiduCloud.js",
    "qimao": "https://raw.githubusercontent.com/I-am-R-E/QuantumultX/main/JavaScript/QiMaoXiaoShuo.js"
}

BLACKLIST_FILE = 'iOS-OmniGuard-Blacklist.txt'
MITM_MODULE_FILE = 'OmniGuard-Predator-MitM.sgmodule'
README_FILE = 'README.md'

def main():
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    t_str = now.strftime("%Y-%m-%d %H:%M")
    v_str = now.strftime("%Y.%m.%d.%H")
    
    # --- 阶段 A: 更新黑名单元数据 ---
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
            for l in lines:
                if '! Version:' in l: f.write('! Version: ' + v_str + '\n')
                elif '! Updated:' in l: f.write('! Updated: ' + t_str + '\n')
                else: f.write(l)

    # --- 阶段 B: 探测资源 (404 仅记录，不报错) ---
    status_logs = []
    for name, url in SOURCES.items():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                status_logs.append(f"✅ {name} 同步成功")
            else:
                status_logs.append(f"🚨 {name} 失效({r.status_code})，已冻结旧版")
        except:
            status_logs.append(f"⚠️ {name} 超时，维持原状")

    # --- 阶段 C: 构造全量模块 (补全所有丢失的功能) ---
    # YouTube 参数转义处理
    yt_arg = 'argument="{\\"lyricLang\\":\\"zh-Hans\\",\\"captionLang\\":\\"zh-Hans\\",\\"blockUpload\\":true}"'
    
    m = '#!name = iOS-OmniGuard Predator-MitM\n'
    m += '#!desc = 状态: 运行中 | 更新: ' + t_str + ' | 包含冻结保护机制\n'
    m += '#!category = OmniGuard\n#!system = ios\n\n'
    
    m += 'https://monica.im/en/tools/rewrite-text\n'
    m += '^https?://.*\\.amap\\.com/ws/(boss/order_web/\\w{8}_information|asa/ads_attribution|shield/scene/recommend) _ reject\n'
    m += '^https?://pan\\.baidu\\.com/act/.+ad_ - reject\n'
    m += '^https?://api-ks\\.qimao\\.com/.* - reject-dict\n\n'
    
    m += '[Script]\n'
    m += f'bili.enhance = type=http-response,pattern=^https://app\\.bilibili\\.com/bilibili\\.app\\.(view\\.v1\\.View/View|dynamic\\.v2\\.Dynamic/DynAll|interface\\.v1\\.Search/Default|resource\\.show\\.v1\\.Tab/GetTabs|account\\.v1\\.Account/Mine)$,requires-body=1,binary-body-mode=1,script-path={SOURCES["bili"]}\n'
    m += f'youtube.response = type=http-response,pattern=^https://youtubei\\.googleapis\\.com/youtubei/v1/(browse|next|player|search|reel/reel_watch_sequence|guide|account/get_setting|get_watch),requires-body=1,max-size=-1,binary-body-mode=1,script-path={SOURCES["youtube"]},{yt_arg}\n'
    m += f'amap_ad = type=http-response,pattern=^https?://.*\\.amap\\.com/ws/(faas/amap-navigation/main-page|valueadded/alimama/splash_screen|msgbox/pull|shield/(shield/dsp/profile/index/nodefaas|search/new_hotword)),requires-body=1,script-path={SOURCES["amap"]}\n'
    m += f'wechat_unblock = type=http-response,pattern=^https\\:\\/\\/(weixin110\\.qq|security.wechat)\\.com,requires-body=1,script-path={SOURCES["wechat"]}\n'
    m += f'baidu_cloud = type=http-response,pattern=^https?://pan\\.baidu\\.com/rest/2\\.0/membership/user,requires-body=1,script-path={SOURCES["baidu"]}\n'
    m += f'qimao_vip = type=http-response,pattern=^https?://(api-\\w+|xiaoshuo)\\.wtzw\\.com/api/v\\d/,requires-body=1,script-path={SOURCES["qimao"]}\n\n'
    
    m += '[MITM]\n'
    m += 'hostname = %APPEND% *amap.com, security.wechat.com, pan.baidu.com, app.bilibili.com, *.googlevideo.com, youtubei.googleapis.com, *.wtzw.com\n'

    with open(MITM_MODULE_FILE, 'w', encoding='utf-8') as f:
        f.write(m)

    # --- 阶段 D: 更新 README 日志 ---
    if os.path.exists(README_FILE):
        with open(README_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        new_md = []
        for line in content.splitlines():
            if '**最后修改时间**：' in line:
                new_md.append('**最后修改时间**：' + t_str + ' (GMT+8)')
            else:
                new_md.append(line)
        
        # 简单注入更新动态
        final_readme = '\n'.join(new_md)
        if '## 📅 最近更新动态' in final_readme:
            log_block = '## 📅 最近更新动态\n> 更新于: ' + t_str + '\n' + '\n'.join([f"- {s}" for s in status_logs])
            import re
            final_readme = re.sub(r'## 📅 最近更新动态.*?(?=\n##|$)', log_block, final_readme, flags=re.DOTALL)
            
        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.write(final_readme)

if __name__ == '__main__':
    main()
