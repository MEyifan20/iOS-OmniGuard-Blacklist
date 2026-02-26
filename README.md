# 🛡️ iOS-OmniGuard-Blacklist (Predator-Standard)

[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist (Standard Unified Edition)
! Description: 针对 iOS 环境深度优化的全能黑名单旗舰版。采用去重增强架构，精准锁定 Google、YouTube 及国内主流视频/阅读 APP，与 Whitelist 实现 100% 逻辑闭环。
! Version: 2026.02.26.22
! Codename: Predator-Standard
! Updated: 2026-02-26
! -------------------------------------------------------------------------------------------------------

## 📖 项目简介
**iOS-OmniGuard-Blacklist** 是专为 iOS 高级用户打造的“去重增强型”拦截方案。本方案不以域名数量取胜，而是通过高强度的 `$important` 标签和 DNS 库无法实现的**路径级规则**，对顽固广告进行精准剥离。

本库已完成对 **[iOS-OmniGuard-Whitelist](https://github.com/MEyifan20/Whitelist)** 的全量冲突校验，并针对全球最大规则集 `217heidai/adblockdns` 完成了物理去重，确保系统资源占用极低。

---

## 🚀 订阅指引
建议在 **AdGuard Pro / Shadowrocket** 中添加以下订阅地址：

订阅链接:
https://raw.githubusercontent.com/MEyifan20/Whitelist/main/iOS-OmniGuard-Blacklist.txt

---

## 💎 核心优势
* 🚀 极速补丁: 已剔除通用库中 20w+ 冗余域名，仅保留高频变动与高难度的特定规则。
* 🎯 路径级过滤: 突破 DNS 拦截局限，精准锁定 YouTube 视频中插及 Google 统计脚本路径。
* 🛠️ 强效修正: 使用 $important 标签，强制覆盖第三方规则中可能的误杀或漏杀。
* 📖 深度专项: 内置“优爱腾芒”及“七猫/番茄”等国内主流视频与小说 APP 的专项补丁。

---

## 🛠️ 技术指标 (Technical Metrics)
为了实现极致的拦截效果，本项目遵循以下逻辑：
$$Block \cap \{Ad, Tracker, Hijack\} \setminus \{Core\_Service\} = \emptyset$$

| 模块名称 | 拦截目标 | 策略强度 |
| :--- | :--- | :--- |
| **Priority Targets** | Google 广告集群、GTM 追踪、路径级脚本 | 核心 (Core) |
| **YouTube Predator** | 视频中插、QOE 统计、短视频广告标识 | 实时 (Real-time) |
| **CN Video Shield** | 优爱腾芒、B站动态广告、日志上报 | 专项 (Special) |
| **Reading Shield** | 七猫/番茄小说穿插、激励视频、SDK 注入 | 深度 (Clean) |
| **Global Networks** | 全球主流广告分发、移动端统计引擎 | 强化 (Force) |

---

## ⚙️ 配置建议
1. 务必同时订阅 iOS-OmniGuard-Whitelist 并将其优先级设为最高，以确保系统服务不被误杀。
2. 配合使用: 本列表已针对 217heidai 规则去重，建议将两者配合使用以获得覆盖率与性能的最优解。

---

## 🤝 致谢与声明
* 致谢: 感谢 EasyList, AdRules 及 217heidai 提供的基础数据支持。
* 声明: 本项目仅供技术研究与交流使用，禁止用于任何非法用途。

---
**Maintained by**: [MEyifan20](https://github.com/MEyifan20)  
**License**: [MIT](https://opensource.org/licenses/mit-license.php)
