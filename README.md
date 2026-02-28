# 🛡️ iOS-OmniGuard-Blacklist（Predator-Standard）

[广告拦截加 2.0]！
标题：iOS-OmniGuard-黑名单（标准统一版）！
描述：针对 iOS 环境深度优化的全能黑名单拦截引擎。整合 217黑带环境前提，融合 BlueSkyXN 双库并加入个人规则丰富，与白名单完美配合。
版本：2026.03.01.01！
代号：掠夺者标准！
更新：2026-03-01 01:01 (GMT+8)！
! -----------------------------------------------------------------------------------------------------------

## 📖 项目简介
iOS-OmniGuard-Blacklist 是专为 iOS 高级用户打造的“系统级净网”拦截方案。当你在浏览网页或使用 App 时，往往会遇到各种开屏广告、追踪器以及隐私泄露风险。

**💡 作者强烈建议：** 请务必将本项目与本作者的兄弟项目 **[iOS-OmniGuard-Whitelist](https://github.com/MEyifan20/iOS-OmniGuard-Whitelist)** 组合使用。

黑名单负责全域深度拦截，而白名单负责精准放行苹果服务、国内主流支付/社交渠道及关键 CDN 节点。这种“攻防对冲”的闭环逻辑能有效防止因暴力拦截导致的 App 无法登录、图片加载失败或系统自动更新延迟等误杀与系统错误。

---

## 🚀 订阅地址
1️⃣ **DNS 过滤器 (全量聚合黑名单)**
- **jsDelivr CDN (推荐国内直连)**: `https://cdn.jsdelivr.net/gh/MEyifan20/iOS-OmniGuard-Blacklist@main/iOS-OmniGuard-Blacklist.txt`
- **GitHub 原始地址**: `https://raw.githubusercontent.com/MEyifan20/iOS-OmniGuard-Blacklist/main/iOS-OmniGuard-Blacklist.txt`

---

## 💎 核心优势
- 🚫 **全域广告截断**: 强制拦截主流 App 开屏广告、内置横幅及信息流推广。
- 🕵️ **隐私追踪防护**: 封杀移动端常见的分析插件、采集日志器及用户画像监测点。
- 📊 **多源动态融合**: 自动同步三大上游仓库，保证规则的时效性、广度与深度。
- ⚖️ **底层逻辑闭环**: 遵循 AdGuard 官方语法规范，自动执行物理去重。

---

## 🛠️ 技术指标 (Technical Metrics)
为了实现最大的拦截效率，本项目遵循以下过滤逻辑：
$$Block \cap \{AD\_Server, Tracker, Analytics\} \setminus \{Whitelist\_Allow\} = 0\%$$

| 模块名称 | 保护目标 | 策略强度 |
| :--- | :--- | :--- |
| **广告服务器** | 开屏广告、弹窗广告 | 拦截 (Block) |
| **追踪器** | 追踪器、数据采集器 | 全面封杀 (Reject) |
| **分析** | App 内部行为日志上传 | 行为抑制 (Mute) |
| **安全** | 恶意软件、钓鱼链接 | 安全防护 (Secure) |

---

## 🤖 自动化维护 (Auto-Update)
本项目支持通过 GitHub Actions 实现自动化维护。
- **规则总数**：1,012,211条 (自动去重后)
- **最后同步**：2026-03-01 01:01(北京时间 UTC+8)
- **核心来源**：217heidai + BlueSkyXN (All + Sky)
- **个人来源**：my-rules.txt (个性化丰富包)

---

## 📝 变更日志 | Changelog
详细的版本演进记录、新增/移除规则统计以及自动化去重报告，请参阅：
👉 **[查看完整更新日志](./changelog.md)**

---

## ❤️ 助力项目
- **点亮星星**：点击右上角 ⭐ 星星，这是对我持续维护最大的动力。
- **反馈问题**：请提交 [Issues](https://github.com/MEyifan20/iOS-OmniGuard-Blacklist/issues)。

---
**iOS-OmniGuard-Blacklist** · 愿您的网络环境干净且自由。

**最后修改时间**：2026-03-01 01:01 (GMT+8)**维护者**：[MEyifan20](https://github.com/MEyifan20)  
**许可证**：MIT
