# 🛡️ iOS-OmniGuard-Blacklist (Predator-Standard)

[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist (Standard Unified Edition)
! Description: 针对 iOS 环境深度优化的全能黑名单拦截引擎。整合 217heidai 环境前提，融合 BlueSkyXN 双库并加入个人规则丰富，与 Whitelist 完美配合。
! Version: {{VERSION}}
! Codename: Predator-Standard
! Updated: {{UPDATE_TIME}}
! -------------------------------------------------------------------------------------------------------

## 📖 项目简介
**iOS-OmniGuard-Blacklist** 是专为 iOS 高级用户打造的“系统级净网”拦截方案。当你在浏览网页或使用 App 时，往往会遭遇各种开屏广告、追踪器以及隐私泄露风险。

**强烈建议将其与本作者兄弟项目 [iOS-OmniGuard-Whitelist](https://github.com/MEyifan20/Whitelist) 组合使用**。黑名单负责全域拦截，白名单负责精准放行苹果核心服务及国内支付/社交关键节点。通过这种“攻防对冲”的逻辑，可以完美防止因暴力拦截导致的 App 无法登录、图片断流或系统自动更新延迟等误杀问题，确保系统 100% 稳定运行。

---

## 🚀 订阅地址

### 1️⃣ DNS 过滤器 (全量聚合黑名单)
* **jsDelivr CDN (推荐国内直连)**
https://cdn.jsdelivr.net/gh/MEyifan20/iOS-OmniGuard-Blacklist@main/iOS-OmniGuard-Blacklist.txt

* **GitHub 原生地址**
https://raw.githubusercontent.com/MEyifan20/iOS-OmniGuard-Blacklist/main/iOS-OmniGuard-Blacklist.txt

---

## 💎 核心优势
* 🚫 **全域广告截断**: 强制拦截主流 App 开屏广告、内置横幅及信息流推广。
* 🕵️ **隐私追踪防护**: 封杀移动端常见的分析插件、采集日志器及用户画像监测点。
* 📊 **多源动态融合**: 自动同步三大上游仓库，确保规则的时效性、广度与深度。
* ⚖️ **底层逻辑闭环**: 遵循 AdGuard 官方语法规范，自动执行物理去重，优化加载速度。

---

## 🛠️ 技术指标 (Technical Metrics)
为了实现最大限度的拦截效率，本项目遵循以下过滤逻辑：
$$Block \cap \{AD\_Server, Tracker, Analytics\} \setminus \{Whitelist\_Allow\} = 0\%$$

| 模块名称 | 保护目标 | 策略强度 |
| :--- | :--- | :--- |
| **Ad Server** | 开屏广告、弹窗广告、视频前贴片 | 深度拦截 (Block) |
| **Trackers** | 友盟、TalkingData、Adjust 等追踪器 | 全面封杀 (Reject) |
| **Analytics** | 各大厂 App 内部的行为日志上传接口 | 行为抑制 (Mute) |
| **Security** | 恶意软件分发、钓鱼链接及垃圾域名 | 安全防护 (Secure) |

---

## ⚙️ 配置建议
1. **安装逻辑**：进入应用 -> DNS 防护 -> DNS 过滤器 -> 添加过滤器 -> 粘贴上述 TXT 链接。
2. **优先级对齐**：**强烈建议** 确保 `iOS-OmniGuard-Whitelist`（白名单）的排序和优先级始终高于本项目，以遵循“先守护放行、后精准拦截”的原则。
3. **协同运作**: 单独使用本项目可能会因第三方库的激进规则导致误杀，请务必配合兄弟项目 `Whitelist` 以构建完美的攻防闭环。

---

## 🤖 自动化维护 (Auto-Update)
本项目支持通过 GitHub Actions 实现自动化维护，每日自动同步上游并更新统计数据，确保你的规则永远处于激活状态。

* **规则总数**：`{{TOTAL_RULES}}` 条 (自动去重后)
* **最后同步**：`{{SYNC_TIME}` (北京时间 UTC+8)
* **核心来源**：217heidai + BlueSkyXN (All + Sky)
* **个人来源**：my-rules.txt (个性化丰富包)
---

## 🤝 致谢与声明
* **致谢**: 感谢 **217heidai** 与 **BlueSkyXN** 提供的优秀规则基础。
* **声明**: 本项目仅供技术研究与交流使用，禁止用于任何非法用途。

---

## ❤️ 助力项目
- **点亮 Star**：点击右上角 ⭐ Star，这是对我持续维护最大的动力。
- **反馈问题**：请提交 [Issues](https://github.com/MEyifan20/iOS-OmniGuard-Blacklist/issues)。

---
**iOS-OmniGuard-Blacklist** · 愿你的网络环境干净且自由。

**最后修改时间**：{{FOOTER_TIME}} (GMT+8)  
**维护者**：[MEyifan20](https://github.com/MEyifan20)  
**许可证**：[MIT](https://opensource.org/licenses/MIT)
