# 仓库元信息配置

开源发布前的一次性配置清单。配置完可以删掉这个文件。

---

## 1. 仓库名

**定：`gesture-fingerprint`**（2026-07-26 已查重确认可用）

### 查重结果

| 候选 | PyPI | npm | GH 组织名 | 商业占用 | 结论 |
|---|---|---|---|---|---|
| **gesture-fingerprint** | ✅ 空 | ✅ 空 | ✅ 空 | 搜索零商业结果 | ✅ **采用** |
| touchsig | ✅ 空 | ✅ 空 | ✅ 空 | 干净 | 备选 |
| touch-dna | ✅ 空 | ✅ 空 | ✅ 空 | 法医学标准术语（NIJ / Wikipedia / PubMed） | 搜索会被刑侦 DNA 内容淹没 |
| ~~touchprint~~ | ✅ 空 | ✅ 空 | ❌ 被空号占 | 🔴 **IDEMIA 在售指纹采集产品线** | ❌ **否决** |

### 为什么否决 touchprint

包名虽然都空着，但 **IDEMIA 有一条名为 TouchPrint 的在售指纹采集产品线**（TouchPrint 5300 / 5600 / 5900、TouchPrint Enterprise TPE5，有独立产品页），IDEMIA 是全球最大的生物识别厂商之一。

这不是跨行业巧合，是**同一个语义域——生物特征识别**：

1. 商标风险实打实：安全公司开源一个做"指纹识别"的项目、用同行大厂的产品名，是会收函的那种撞法
2. SEO 归零：搜 "touchprint" 出来的是 IDEMIA 产品页和几家印刷公司（touchprint.nz / touchprint.us），仓库永远排不上

`gesture-fingerprint` 是描述性词组，商标上属弱标记——别人告不了你，你也不用担心撞别人；而且目标读者搜的就是 "gesture" + "fingerprint" 这两个词，SEO 反而最好。

### 复查命令（改名或新增候选时用）

```bash
n=gesture-fingerprint
curl -s -o /dev/null -w "PyPI:%{http_code}\n" "https://pypi.org/pypi/$n/json"
curl -s -o /dev/null -w "npm:%{http_code}\n"  "https://registry.npmjs.org/$n"
curl -s -o /dev/null -w "GH组织:%{http_code}\n" "https://api.github.com/users/$n"
# 404 = 可用；200 = 已被占
# 商业名/商标必须另外用搜索引擎查一遍——包名空着不代表名字能用
```

> Python 包名和 CLI 名**不跟着改**，保持 `gesture-behavior-classifier` / `gesture-classify`。
> 仓库名负责传播，包名负责准确，两者不一致在开源项目里很常见，改动收益远小于成本。

---

## 2. About · Description

GitHub 的 About 字段限 350 字符。搜索权重主要在这里，不在仓库名。

**推荐（英文，国际可发现性 + 关键词覆盖）：**

```
Identify whether a mobile touch comes from a human, a software script, or a specific cheating hardware device — gesture fingerprinting across 9 behavioral dimensions, built from 75k+ labeled gestures and 8 real cheating devices bought off the shelf.
```

**中文备选（如果只面向国内）：**

```
从手机触摸埋点判定操作来自真人、软件脚本，还是某一种作弊硬件。基于 8 台实购作弊设备、7.5 万条标注手势、9 个行为维度的可解释规则引擎。
```

推荐用英文：README 已经是中文，国内读者从视频/文章带链接进来，不靠 description 理解；而英文 description 能多吃一层 GitHub 全站搜索和国际同行的流量，成本为零。

**Website 字段**：填揭秘视频的落地页或公司官网。留空是浪费一个免费外链位。

---

## 3. Topics

直接粘贴（GitHub 上限 20 个，这里 16 个）：

```
bot-detection
anti-bot
anti-fraud
fraud-detection
risk-control
behavioral-biometrics
device-fingerprint
gesture-recognition
touch-analysis
automation-detection
mobile-security
security-research
click-farm
android
rule-engine
python
```

> `behavioral-biometrics` 是这个领域的**学术标准术语**，别漏。国际同行搜索时用的是这个词，不是 "bot detection"。

---

## 4. Social preview

`social-preview.png`（1280×640）已生成，直接上传：

**Settings → General → Social preview → Upload an image**

设计说明：左侧是核心主张，右侧是两块轨迹叠加对比——真人 250 条发散成一片，机器 250 条挤成一束。这张图在微信、Twitter、Slack 里被转发时，**不用点开就能看懂项目在做什么**。

需要改文案时编辑 `gen_social.py` 后重新生成：

```bash
python3 gen_social.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --hide-scrollbars --window-size=1280,640 --screenshot=social-preview.png \
  --default-background-color=0A0D14FF "file://$PWD/wrap.html"
```

---

## 5. 仓库设置

| 项 | 建议 | 理由 |
|---|---|---|
| 默认分支 | `main` | — |
| Issues | 开 | 主要的外部反馈入口 |
| Discussions | 开 | 阈值标定、机型适配这类问题不适合当 issue |
| Wiki | 关 | 内容都在 `docs/`，两处会分叉 |
| Projects | 关 | 用不上 |
| Releases | 用 | **APK 作为 Release 附件，不要进 git** |

### Issue 标签

除默认标签外加这三个：

| 标签 | 颜色 | 用途 |
|---|---|---|
| `calibration` | `#0E8A16` | 阈值标定、机型适配 |
| `new-device` | `#D93F0B` | 新的作弊设备样本贡献 |
| `false-positive` | `#FBCA04` | 误判反馈 |

`new-device` 是最重要的一个——**仓库真正的资产是设备指纹库，不是那 859 行代码**。要让外部贡献设备样本这件事有明确入口。

---

## 6. README badges

放在标题下方一行：

```markdown
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Python](https://img.shields.io/badge/python-%E2%89%A53.9-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Devices](https://img.shields.io/badge/tested%20devices-10%20classes-orange)
```

`dependencies-none` 这个 badge 值得放——纯标准库、零依赖对安全团队是实打实的加分项（不用过供应链审查）。

---

## 7. 发布前必须处理

### 🔴 阻断级 —— 已全部修复

- [x] **修 config 路径**。原 `cli.py:14` 用 `parents[2]/config`，只在源码目录成立；非 editable 安装后会去 `site-packages/../../config/` 找，必然崩。
  已把 config 移入包内（`src/gesture_behavior_classifier/config/`）、改成 `parent/"config"`、并在 `pyproject.toml` 声明 package-data。
  **已用干净 venv + `pip install .` + 从无关目录运行验证通过。**
- [x] **清理仓库文件**。删掉 56 个 `.trashed-*`、2 个 `.DS_Store`、误建的 `path/to/...` 输出目录，新增 `.gitignore`。
- [x] **APK 移出 git**。`测试appV2.apk` 已移到 `release-assets/`，`.gitignore` 里加了 `*.apk`。发版时作为 Release 附件上传。
- [x] **example_outputs 瘦身**。原来是 86,884 条手势的全量输出（99 MB，单文件 53 MB），
  已改为用 `人工测试数据/touch_20260724_194817`（机械臂，66 条）重新生成，**99 MB → 72 KB**，
  且输出内容正好对应 `docs/04` 里那组 72.7% / 27.3% 的真实结果。
- [x] **修复被 config 移动打断的测试**。`tests/test_rules.py` 原本硬编码 `parents[1]/config`，
  已改为从 `cli.DEFAULT_CONFIG` 读取，今后不会再和打包位置分叉。**6/6 通过（源码模式与安装模式各验一次）。**

> 仓库体积：**169 MB → 1.0 MB**。

### 🟡 仍建议做

- [ ] 补 `CONTRIBUTING.md`，重点写"如何贡献一台新设备的样本"
- [ ] 加一个最小 GitHub Actions：`pytest` + 用 `人工测试数据` 跑一次端到端，防止改阈值改坏
- [ ] 修合并多文件时的静默丢数据：`features.deduplicate_summary_rows` 按 `gesture_index` 去重，
      但每个采集文件的序号都从 1 重新开始——把两个 50 条的文件拼起来喂进去，会只处理 50 条且无任何告警。
      建议改成 `文件名 + gesture_index` 复合键。

---

## 8. 首个 Release

标签 `v0.1.0`，标题「首次公开：9 维度手势指纹识别」。

Release notes 建议结构：

```markdown
首次公开发布。

**能做什么**
从手机触摸埋点判定操作来自真人、软件脚本，还是 10 类作弊工具中的哪一种。

**实验规模**
8 台实购作弊硬件（1863.6 元）+ 2 类软件脚本对照组，
3 部手机 × 5 种手机状态，累计 7.5 万+ 条标注手势，9 个行为维度。

**实测准确率**
真人 98–100% · 屏幕录制脚本 100% · 鼠标点击器 78% · 机械臂 72.7%
（弱项归因见 docs/04-验证与局限.md）

**已知边界**
不是实时拦截器 · 需要端侧埋点 · 阈值需按机型标定

**附件**
测试appV2.apk —— 我们实验用的 Android 采集 App，可直接复现全部实验
```

> 把 78% 和 72.7% 写进 Release notes 里。安全同行对"准确率 99.9%"的第一反应是不信，
> 把弱项摆出来反而是最强的可信度信号。
