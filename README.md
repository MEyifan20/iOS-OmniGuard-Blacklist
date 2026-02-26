# 🛡️ iOS-OmniGuard-Blacklist (Predator-Standard)

[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist (Standard Unified Edition)
! Description: 针对 iOS 环境深度优化的全能黑名单旗舰版。采用去重增强架构，精准锁定 Google、YouTube 及国内主流视频/阅读 APP，与 Whitelist 实现 100% 逻辑闭环。
! Version: 2026.02.26.24
! Codename: Predator-Standard
! Updated: 2026-02-26 17:00
! -------------------------------------------------------------------------------------------------------

## 📖 项目简介
**iOS-OmniGuard-Blacklist** 是专为 iOS 高级用户打造的“去重增强型”拦截方案。本方案不仅通过高强度的 `$important` 标签和路径级规则剥离广告，更集成了 Cosmetic Filtering（视觉美化）与 Advanced Scriptlets（脚本注入），实现从网络层到渲染层的全维度净网。

本库已完成对 **iOS-OmniGuard-Whitelist** 的全量冲突校验，并针对全球最大规则集 `217heidai/adblockdns` 完成了物理去重，确保系统资源占用极低。依托 GitHub Actions，本项目已实现全自动无人值守维护。

---

## 🚀 订阅地址

[ jsDelivr CDN 加速 (推荐国内直连) ]
https://cdn.jsdelivr.net/gh/MEyifan20/iOS-OmniGuard-Blacklist@main/iOS-OmniGuard-Blacklist.txt

[ GitHub 原生地址 ]
https://raw.githubusercontent.com/MEyifan20/iOS-OmniGuard-Blacklist/refs/heads/main/iOS-OmniGuard-Blacklist.txt

---

## 💎 核心优势
* 🚀 **极速补丁**: 剔除 20w+ 冗余域名，仅保留高频变动与高难度的特定规则。
* 🎯 **路径级过滤**: 突破 DNS 拦截局限，精准锁定 YouTube 视频中插及 Google 统计脚本路径。
* 👻 **视觉与注入**: 支持元素隐藏（剔除空白占位）与 JS 脚本注入（绕过反去广告检测）。
* 📖 **深度专项**: 内置“优爱腾芒”及“七猫/番茄”等国内主流视频与小说 APP 的专项补丁。
* 🪄 **App 级重写**: 提供 Shadowrocket 专属 MitM 模块，实现对加密 HTTPS 广告的直接剥离。
* 🤖 **自动进化**: 部署 GitHub Actions 每日自动抓取上游、智能去重并同步最新版本与时间。

---

## 🛠️ 技术指标 (Technical Metrics)
为了实现极致的拦截效果，本项目遵循以下逻辑：
$$Block \cap \{Ad, Tracker, Hijack\} \setminus \{Core\_Service\} = \emptyset$$

| 模块名称 | 拦截目标 | 策略强度 |
| :--- | :--- | :--- |
| **Priority Targets** | Google 广告集群、GTM 追踪 | 核心 (Core) |
| **YouTube Predator** | 视频中插、QOE 统计、短视频广告 | 实时 (Real-time) |
| **CN Video Shield** | 优爱腾芒、B站动态广告 | 专项 (Special) |
| **Reading Shield** | 七猫/番茄小说穿插、激励视频 | 深度 (Clean) |
| **Advanced Shield** | 元素折叠 (CSS)、反检测劫持 (JS) | 注入 (Inject) |
| **Shadowrocket MitM** | App 内 HTTPS 广告流、开屏数据 | 解密重写 (Rewrite) |

---

## ⚙️ 配置建议
1. **添加路径**：防护 (盾牌图标) -> DNS 防护 -> DNS 过滤 -> DNS 过滤器 -> 添加过滤器。
2. **务必同时订阅** iOS-OmniGuard-Whitelist 并将其优先级设为最高，以确保系统服务不被误杀。
3. **配合使用**: 本列表已针对 217heidai 规则去重，建议将两者配合使用。

---

## 🚀 小火箭 (Shadowrocket) 专属高级模块
为了突破单纯 DNS 过滤无法处理的 **HTTPS 加密广告**（如 B站、知乎、优爱腾芒及小说的 App 内开屏和贴片），本项目提供配套的 `.sgmodule` 重写模块。

**功能特点：**
* **精准 MitM 劫持**：仅解密特定的广告 API 域名，绝对不触碰个人隐私与支付数据。
* **Reject-Dict 重写**：强制向广告请求返回空数据字典，实现 App 秒进无广告，避免黑屏卡顿。

**模块订阅与使用方式：**
1. **导入模块**：在 Shadowrocket 的 **“配置” -> “模块”** 中，点击右上角 `+`，添加并下载模块链接：
   `https://raw.githubusercontent.com/MEyifan20/iOS-OmniGuard-Blacklist/refs/heads/main/OmniGuard-Predator-MitM.sgmodule`
2. **开启 HTTPS 解密**：在“配置”页面点击“HTTPS 解密”并开启开关。
3. **信任证书 (首次必做)**：点击“生成新的 CA 证书” -> 安装描述文件 -> 去 iOS 系统“设置”中安装该描述文件 -> 在“通用” -> “关于本机” -> “证书信任设置”中开启绿灯信任。

---

## 🤖 自动化维护 (Auto-Update)
本项目已全面接入 GitHub Actions，实现真正的“无人值守”：
* **每日凌晨自动执行**：定时拉取最新的 217heidai 上游规则库。
* **智能去重算法**：保护 `$important` 等高级战术规则的同时，精准剔除普通冗余项。
* **时间与版本自适应**：每天自动更新项目文档底部的“最后修改时间”与规则文件内部的 `Version` 字段。

---

## 🤝 致谢与声明
* 致谢: 感谢 EasyList, AdRules 及 217heidai 提供的基础数据支持。
* 声明: 本项目仅供技术研究与交流使用，禁止用于任何非法用途。

---

## ❤️ 助力项目

- **点亮 Star**：点击右上角 ⭐ Star，这是对我持续维护最大的动力。
- **反馈问题**：请提交 [Issues](https://github.com/MEyifan20/iOS-OmniGuard-Blacklist/issues)。

---
**iOS-OmniGuard-Blacklist** · 愿你的网络环境干净且自由。

**最后修改时间**：2026-02-26 19:14 (GMT+8)

---
**Maintained by**: [MEyifan20](https://github.com/MEyifan20)  
**License**: [MIT](https://opensource.org/licenses/mit-license.php)

## 🚀 全自动 CDN 订阅地址
- **Predator-MitM 模块**: `https://cdn.jsdelivr.net/gh/MEyifan20/iOS-OmniGuard-Blacklist@main/OmniGuard-Predator-MitM.sgmodule`
- **DNS 黑名单**: `https://cdn.jsdelivr.net/gh/MEyifan20/iOS-OmniGuard-Blacklist@main/iOS-OmniGuard-Blacklist.txt`





## 📅 最近更新动态
> 更新于: 2026-02-26 19:14

- ❌ baidu 失效 [HTTP 404]
- ❌ bili 失效 [HTTP 404]
- 📅 黑名单时间戳已刷新至 2026-02-26 19:14

