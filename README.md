# 🛡️ iOS-OmniGuard-Blacklist (Predator-Standard)

[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist (Standard Unified Edition)
! Description: 针对 iOS 环境深度优化的全能黑名单拦截引擎。整合 217heidai 环境前提，融合 BlueSkyXN 双库并加入个人规则丰富，与 Whitelist 完美配合。
! Version: 2026.02.28.15
! Codename: Predator-Standard
! Updated: 2026-02-28 15:30
! -------------------------------------------------------------------------------------------------------

## 📖 项目简介
**iOS-OmniGuard-Blacklist** 是专为 iOS 高级用户打造的“系统级净网”拦截方案。当你在浏览网页或使用 App 时，往往会遭遇各种开屏广告、追踪器以及隐私泄露风险。

本项目以 **[217heidai](https://github.com/217heidai/adblockfilters)** 的过滤逻辑为环境前提，深度融合 **[BlueSkyXN](https://github.com/BlueSkyXN/AdGuardHomeRules)** 的 `all.txt` 与 `skyrules.txt` 核心域名库，并针对个人特殊拦截需求进行全方位增量丰富。建议将其与 **iOS-OmniGuard-Whitelist** 组合使用，构建完美的攻防闭环。

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
1. **DNS 规则安装**：进入应用 -> DNS 防护 -> DNS 过滤器 -> 添加过滤器 -> 粘贴上述 TXT 链接（AdGuard 原生支持识别 `||domain^` 语法）。
2. **执行顺序**：请务必确保该黑名单的排序和优先级**低于**所有白名单，让防护盾在第一层生效。
3. **配合使用**: 强烈建议与本项目的兄弟版本 `iOS-OmniGuard-Whitelist` 组合使用。

---

## 🤖 自动化维护 (Auto-Update)
本项目支持通过 GitHub Actions 实现自动化维护，每日自动同步上游并更新统计数据，确保你的规则永远处于激活状态。

* **规则总数**：`计算中...` 条 (自动去重后)
* **最后同步**：`等待脚本运行...` (北京时间 UTC+8)
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

**最后修改时间**：2026-02-28 15:30 (GMT+8)
**维护者**：MEyifan20
**许可证**：MIT
