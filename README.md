# 🛡️ iOS-OmniGuard-Blacklist (Predator-Standard)

[Adblock Plus 2.0]
! Title: iOS-OmniGuard-Blacklist (Standard Unified Edition)
! Description: 针对 iOS 环境深度优化的全能黑名单旗舰版。采用去重增强架构，精准锁定 Google、YouTube 及国内主流视频/阅读 APP，与 Whitelist 实现 100% 逻辑闭环。
! Version: 2026.02.26.26
! Codename: Predator-Standard
! Updated: 2026-02-26 21:32
! -------------------------------------------------------------------------------------------------------

## 📖 项目简介
**iOS-OmniGuard-Blacklist** 是专为 iOS 高级用户打造的“去重增强型”拦截方案。本方案不仅通过高强度的 `$important` 标签和路径级规则剥离广告，更集成了 **Cosmetic Filtering**（视觉美化）与 **Advanced Scriptlets**（脚本注入），实现从网络层到渲染层的全维度净网。

本库已完成对 **iOS-OmniGuard-Whitelist** 的全量冲突校验，并针对全球最大规则集 `217heidai/adblockdns` 完成了物理去重，确保系统资源占用极低。

---

## 🚀 订阅地址 (一键复制)

### 1️⃣ DNS 过滤器 (标准黑名单)
> 适用于 AdGuard, Quantumult X, Shadowrocket (DNS 过滤) 等。

* **jsDelivr CDN (推荐国内直连)**
https://cdn.jsdelivr.net/gh/MEyifan20/iOS-OmniGuard-Blacklist@main/iOS-OmniGuard-Blacklist.txt

* **GitHub 原生地址**
https://raw.githubusercontent.com/MEyifan20/iOS-OmniGuard-Blacklist/refs/heads/main/iOS-OmniGuard-Blacklist.txt

### 2️⃣ Shadowrocket 增强模块 (MitM + Script)
> 包含 HTTPS 解密后的深度去广告脚本，需开启 MitM 配合使用。

* **jsDelivr CDN (推荐国内直连)**
https://cdn.jsdelivr.net/gh/MEyifan20/iOS-OmniGuard-Blacklist@main/OmniGuard-Predator-MitM.sgmodule

* **GitHub 原生地址**
https://raw.githubusercontent.com/MEyifan20/iOS-OmniGuard-Blacklist/refs/heads/main/OmniGuard-Predator-MitM.sgmodule

---

## 💎 核心优势
* 🚀 **极速补丁**: 剔除 20w+ 冗余域名，仅保留高频变动与高难度的特定规则。
* 🎯 **路径级过滤**: 突破 DNS 拦截局限，精准锁定 YouTube 视频中插及 Google 统计脚本路径。
* 👻 **视觉与注入**: 支持元素隐藏（剔除空白占位）与 JS 脚本注入（绕过反去广告检测）。
* 📖 **深度专项**: 内置“优爱腾芒”及“七猫/番茄”等国内主流视频与小说 APP 的专项补丁。

---

## 🛠️ 技术指标 (Technical Metrics)
| 模块名称 | 拦截目标 | 策略强度 | 特性 |
| :--- | :--- | :--- | :--- |
| **Priority Targets** | Google 广告集群、GTM 追踪 | 核心 (Core) | 极速响应 |
| **YouTube Predator** | 视频中插、QOE 统计、短视频广告 | 实时 (Real-time) | 路径级锁定 |
| **CN Video Shield** | 优爱腾芒、B站动态广告 | 专项 (Special) | 动态更新 |
| **Reading Shield** | 七猫/番茄小说穿插、激励视频 | 深度 (Clean) | 沉浸体验 |
| **Advanced Shield** | 元素折叠 (CSS)、反检测劫持 (JS) | 注入 (Inject) | 视觉美化 |

---

## ⚙️ 配置建议
1. **DNS 规则安装**：进入应用 -> DNS 防护 -> DNS 过滤器 -> 添加过滤器 -> 粘贴上述 TXT 链接。
2. **小火箭模块安装**：配置 -> 模块 -> 点击右上角 `+` -> 粘贴上述 `.sgmodule` 链接。
3. **务必同时订阅** [iOS-OmniGuard-Whitelist](https://github.com/MEyifan20/iOS-OmniGuard-Whitelist) 并将其优先级设为最高，以确保系统服务不被误杀。
4. **配合使用**: 本列表已针对 `217heidai` 规则去重，建议将两者叠加使用。

---

## 🤝 致谢与声明
* **致谢**: 感谢 EasyList, AdRules 及 217heidai 提供的基础数据支持。
* **声明**: 本项目仅供技术研究与交流使用，禁止用于任何非法用途。

---

## ❤️ 助力项目
- **点亮 Star**：点击右上角 ⭐ Star，这是对我持续维护最大的动力。
- **反馈问题**：请提交 [Issues](https://github.com/MEyifan20/iOS-OmniGuard-Blacklist/issues)。

---
**iOS-OmniGuard-Blacklist** · 愿你的网络环境干净且自由。

**最后修改时间**：2026-02-26 21:32 (GMT+8)
**Maintained by**: [MEyifan20](https://github.com/MEyifan20)  
**License**: [MIT](https://opensource.org/licenses/mit-license.php)
