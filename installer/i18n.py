# -*- coding: utf-8 -*-
"""Language support for the Brick Bite installer.

Priority: environment variable BRICKBITE_LANG (zh / tw / en) >
system locale > English. Anything that is neither Simplified nor Traditional
Chinese falls back to English.
"""
import os


def detect_language() -> str:
    forced = (os.environ.get("BRICKBITE_LANG") or "").strip().lower()
    if forced in ("zh", "zh-cn", "zh_cn", "cn", "chs"):
        return "zh"
    if forced in ("tw", "zh-tw", "zh_tw", "hk", "hant", "cht"):
        return "tw"
    if forced in ("en", "en-us", "en_us"):
        return "en"

    name = ""
    try:
        from PySide6.QtCore import QLocale
        name = QLocale.system().name()  # e.g. zh_TW, en_US
    except Exception:
        try:
            import locale
            name = locale.getdefaultlocale()[0] or ""
        except Exception:
            name = ""
    n = (name or "").lower()
    if n.startswith("zh"):
        if any(tag in n for tag in ("tw", "hk", "mo", "hant")):
            return "tw"
        return "zh"
    return "en"


LANG = detect_language()


STRINGS = {
    # app shell
    "app_name": {
        "zh": "Brick Bite 安装程序",
        "tw": "Brick Bite 安裝程式",
        "en": "Brick Bite Installer",
    },
    "credit": {
        "zh": "演示/正式安装 · 只会替换有差异的文件\n由 CAT0998 与大肥鱼友情提供",
        "tw": "示範/正式安裝 · 只會替換有差異的檔案\n由 CAT0998 與大肥魚友情提供",
        "en": "Demo/real install · only differing files are replaced\nby CAT0998 and DaFeiYu",
    },
    "step_welcome": {"zh": "欢迎", "tw": "歡迎", "en": "Welcome"},
    "step_agree": {"zh": "协议", "tw": "協議", "en": "License"},
    "step_mode": {"zh": "方式", "tw": "方式", "en": "Mode"},
    "step_path": {"zh": "路径", "tw": "路徑", "en": "Path"},
    "step_install": {"zh": "安装", "tw": "安裝", "en": "Install"},
    "step_finish": {"zh": "完成", "tw": "完成", "en": "Done"},
    "btn_back": {"zh": "上一步", "tw": "上一步", "en": "Back"},
    "btn_next": {"zh": "下一步", "tw": "下一步", "en": "Next"},
    "btn_finish": {"zh": "完成", "tw": "完成", "en": "Finish"},
    "btn_browse": {"zh": "浏览…", "tw": "瀏覽…", "en": "Browse…"},

    # welcome
    "welcome_title": {
        "zh": "欢迎安装 Brick Bite  砖砌咬合",
        "tw": "歡迎安裝 Brick Bite  磚砌咬合",
        "en": "Welcome to Brick Bite",
    },
    "welcome_sub": {
        "zh": "这是 OrcaSlicer / Bambu Studio 的砖砌咬合功能安装程序。",
        "tw": "這是 OrcaSlicer / Bambu Studio 的磚砌咬合功能安裝程式。",
        "en": "This installer adds the Brick Bite wall interlocking feature to OrcaSlicer / Bambu Studio.",
    },
    "welcome_body": {
        "zh": "隔层把首圈外墙线宽减半，整组内墙平移半个线宽，外表面保持齐平。\n提供两种模式：半宽交替（0.5w ↔ w）、宽窄交替（0.5w ↔ 1.5w）。",
        "tw": "隔層把首圈外牆線寬減半，整組內牆平移半個線寬，外表面保持齊平。\n提供兩種模式：半寬交替（0.5w ↔ w）、寬窄交替（0.5w ↔ 1.5w）。",
        "en": "On alternating layers the outer wall is printed at half width and the whole inner wall block shifts by half a line width, keeping the outer surface flush.\nTwo modes: Half (0.5w ↔ w) and Wide (0.5w ↔ 1.5w).",
    },

    # agreement
    "agree_title": {"zh": "许可与免责声明", "tw": "授權與免責聲明", "en": "License & Disclaimer"},
    "agree_check": {
        "zh": "我已阅读并同意以上许可与免责声明",
        "tw": "我已閱讀並同意以上授權與免責聲明",
        "en": "I have read and agree to the license and disclaimer above",
    },

    # mode
    "mode_title": {"zh": "选择安装方式", "tw": "選擇安裝方式", "en": "Choose install mode"},
    "mode_auto": {
        "zh": "自动检测：在常见位置与注册表中查找 OrcaSlicer / Bambu Studio",
        "tw": "自動偵測：在常見位置與登錄檔中尋找 OrcaSlicer / Bambu Studio",
        "en": "Auto-detect: look for OrcaSlicer / Bambu Studio in common paths and the registry",
    },
    "mode_manual": {
        "zh": "手动选择：我自己指定程序所在文件夹",
        "tw": "手動選擇：我自己指定程式所在資料夾",
        "en": "Manual: choose the installation folder myself",
    },

    # path
    "path_title": {"zh": "确认安装位置", "tw": "確認安裝位置", "en": "Confirm installation folder"},
    "path_note": {
        "zh": "将替换：主程序 DLL 及有差异的依赖文件\n将跳过：resources 资源、哈希相同的文件\n安全：替换前自动备份为 .brickbite.bak，可一键恢复",
        "tw": "將替換：主程式 DLL 及有差異的相依檔案\n將跳過：resources 資源、雜湊相同的檔案\n安全：替換前自動備份為 .brickbite.bak，可一鍵還原",
        "en": "Will replace: the main DLL and any dependency files that differ\nWill skip: resources and files whose hash is identical\nSafe: originals are backed up as .brickbite.bak and can be restored",
    },
    "browse_title": {
        "zh": "选择程序所在文件夹",
        "tw": "選擇程式所在資料夾",
        "en": "Choose the application folder",
    },

    # install
    "install_title": {"zh": "正在安装…", "tw": "正在安裝…", "en": "Installing…"},
    "install_preparing": {"zh": "准备中…", "tw": "準備中…", "en": "Preparing…"},
    "install_done_label": {"zh": "完成", "tw": "完成", "en": "Done"},

    # finish
    "finish_title": {"zh": "安装完成 ✓", "tw": "安裝完成 ✓", "en": "Installation complete ✓"},

    # say lines
    "say_welcome": {
        "zh": "你好呀，我是小鲸鱼～\n今天就由我带你安装 Brick Bite。",
        "tw": "你好呀，我是小鯨魚～\n今天就由我帶你安裝 Brick Bite。",
        "en": "Hi, I'm the little whale!\nI'll walk you through the Brick Bite install.",
    },
    "say_agree": {
        "zh": "安装前请先看看协议哦～\n小鲸鱼可不想你以后遇到麻烦。",
        "tw": "安裝前請先看看協議哦～\n小鯨魚可不想你以後遇到麻煩。",
        "en": "Please read the license first.\nBetter safe than sorry later.",
    },
    "say_mode": {
        "zh": "想让我自动找程序，\n还是你自己指定位置？",
        "tw": "想讓我自動找程式，\n還是你自己指定位置？",
        "en": "Should I find the app automatically,\nor would you rather pick the folder?",
    },
    "say_path": {
        "zh": "确认一下安装位置，\n小鲸鱼只会替换必要文件。",
        "tw": "確認一下安裝位置，\n小鯨魚只會替換必要檔案。",
        "en": "Confirm the install folder.\nOnly necessary files will be replaced.",
    },
    "say_path_found": {"zh": "已自动检测到：", "tw": "已自動偵測到：", "en": "Auto-detected:"},
    "say_path_notfound": {
        "zh": "没有自动找到，请手动选择目录：",
        "tw": "沒有自動找到，請手動選擇資料夾：",
        "en": "Not found automatically, please choose the folder:",
    },
    "say_path_manual": {
        "zh": "请输入程序所在目录：",
        "tw": "請輸入程式所在資料夾：",
        "en": "Enter the application folder:",
    },
    "say_installing": {
        "zh": "正在安装中……\n进度和日志都会显示在这里。",
        "tw": "正在安裝中……\n進度與日誌都會顯示在這裡。",
        "en": "Installing…\nProgress and logs appear here.",
    },
    "say_done": {
        "zh": "这么轻松就搞定了，\n不要再说我是只知道吃大白饭的大肥鱼呢，本模型可是高性能！(￣▽￣)ノ",
        "tw": "這麼輕鬆就搞定了，\n不要再說我是只知道吃大白飯的大肥魚呢，本模型可是高效能！(￣▽￣)ノ",
        "en": "All done!\nAnd no, I'm not just a rice-eating whale — high performance! (￣▽￣)ノ",
    },
    "say_failed": {
        "zh": "呜哇——失败了 (╥﹏╥)\n小鲸鱼已经哭成一条咸鱼了…",
        "tw": "嗚哇——失敗了 (╥﹏╥)\n小鯨魚已經哭成一條鹹魚了…",
        "en": "Oh no — it failed (╥﹏╥)\nThe little whale is crying…",
    },

    # finish body
    "finish_body": {
        "zh": "{msg}\n\n已安装到：{path}\n\n下一步：打开程序 → 工艺/强度 → 墙 → 「Brick wall mode / 砖砌咬合」",
        "tw": "{msg}\n\n已安裝到：{path}\n\n下一步：開啟程式 → 工藝/強度 → 牆 → 「Brick wall mode / 磚砌咬合」",
        "en": "{msg}\n\nInstalled to: {path}\n\nNext: open the app → Process/Strength → Walls → \"Brick wall mode\"",
    },

    # dialogs
    "dlg_new_install_title": {"zh": "新建安装？", "tw": "新建安裝？", "en": "Install as new?"},
    "dlg_new_install_msg": {
        "zh": "在 {path} 下没有找到主程序。\n\n是否把它作为新的安装目录，写入完整程序？",
        "tw": "在 {path} 下沒有找到主程式。\n\n是否把它作為新的安裝資料夾，寫入完整程式？",
        "en": "No application executable found in {path}.\n\nUse it as a new install folder and write the full program there?",
    },
    "dlg_failed_title": {"zh": "安装失败 (╥﹏╥)", "tw": "安裝失敗 (╥﹏╥)", "en": "Installation failed (╥﹏╥)"},

    # worker logs
    "log_restore": {"zh": "恢复 {rel}", "tw": "還原 {rel}", "en": "restore {rel}"},
    "log_skip": {"zh": "跳过 {rel}（相同）", "tw": "跳過 {rel}（相同）", "en": "skip {rel} (identical)"},
    "log_replace": {"zh": "替换 {rel}", "tw": "替換 {rel}", "en": "replace {rel}"},
    "log_summary": {
        "zh": "完成：替换 {copied} 个文件，跳过 {skipped} 个",
        "tw": "完成：替換 {copied} 個檔案，跳過 {skipped} 個",
        "en": "Done: {copied} file(s) replaced, {skipped} skipped",
    },
    "net_plugin_ok": {
        "zh": "网络插件已就绪（下载/复制到 BambuStudioInternal\\plugins）。",
        "tw": "網路外掛已就緒（下載/複製到 BambuStudioInternal\\plugins）。",
        "en": "Network plug-in is ready (installed into BambuStudioInternal\\plugins).",
    },
    "net_plugin_warn": {
        "zh": "网络插件未能自动安装：可联网后重跑本安装程序，或把官方 Bambu Studio 的 plugins 目录复制到 %APPDATA%\\BambuStudioInternal\\plugins。",
        "tw": "網路外掛未能自動安裝：可連網後重跑本安裝程式，或把官方 Bambu Studio 的 plugins 目錄複製到 %APPDATA%\\BambuStudioInternal\\plugins。",
        "en": "Network plug-in was not installed: re-run this installer while online, or copy the official Bambu Studio plugins folder to %APPDATA%\\BambuStudioInternal\\plugins.",
    },

    # misc
    "default_path": {"zh": "D:\\OrcaSlicer", "tw": "D:\\OrcaSlicer", "en": "D:\\OrcaSlicer"},
    "shortcut_name": {"zh": "Brick Bite 砖砌版", "tw": "Brick Bite 磚砌版", "en": "Brick Bite"},
}

AGREEMENTS = {
    "zh": """第 1 条 · 许可证
本安装程序所安装的修改版程序，其修改部分（Brick Bite 补丁及相关文档）以 GNU Affero General Public License v3.0（AGPL-3.0）发布，与上游保持一致。
你被允许：自由使用、复制、修改、再分发，包括商业使用；你被要求：在分发（含通过网络提供服务）时公开对应源码，保留版权与许可声明。

第 2 条 · 免责声明（重要）
本软件按“现状”（AS IS）提供，不附带任何明示或暗示的担保，包括但不限于：适销性、特定用途适用性、不侵权，以及打印质量、尺寸精度、机械强度方面的任何保证。
使用本软件可能导致：打印失败、表面缺陷、尺寸偏差、材料与时间浪费、设备损坏等。上述风险由使用者自行承担。
作者与贡献者不对任何直接、间接、附带或后果性损失负责。

第 3 条 · 非官方声明
本程序是社区实验性修改，与 OrcaSlicer / Bambu Studio 官方及其维护者无任何隶属、合作或背书关系。

第 4 条 · 安全使用
请先在废料或测试模型上验证效果；不建议用于承力结构、医疗、航空等场景。

第 5 条 · 数据与隐私
本安装程序不收集、不上传任何数据，不包含遥测。

第 6 条 · 第三方组件
包含 OrcaSlicer、Bambu Studio、OpenCASCADE、Boost、wxWidgets、OpenVDB、TBB 等开源组件，许可证见安装目录中的 LICENSE 文件。

第 7 条 · 署名
想法 / 方向 / 测试：@CAT0998
分析 / 实现 / 编译 / 文档：AI — DeepSeek Harness / deepseek-flash

第 8 条 · 彩蛋条款
8.1 如果你真的把这份协议读到了这里，小鲸鱼向你敬个礼。
8.2 本软件不对“装完忘记打开砖砌咬合然后说没效果”负责。
8.3 一周连续打印超过 30 小时，请让机器休息一下。

第 9 条 · 使用边界
可以：用本算法打印模型并销售成品；在自己的项目里使用/移植本算法（需署名并遵守 AGPL-3.0）。
不可以：把本项目的安装器或预编译包改名后售卖、打包进付费软件、冒充作者、删除署名、就本算法申请专利。
简单说：可以商用，但不能把“我和你一起开发的这个免费插件”拿来卖钱。
安装器代码另有许可（INSTALLER-LICENSE.md），payload 中的程序遵循其上游 AGPL-3.0。

第 10 条 · 署名与使用规范
使用、移植或借鉴本算法时，请保留以下署名：
· 想法与方向：@CAT0998
· 实现、分析、编译与文档：AI — DeepSeek Harness / deepseek-flash
· 项目地址：https://github.com/CAT0998/brick-bite

明确禁止：删除或隐藏署名；把本项目补丁/安装器改名后当作自己的成果发布；把安装器原样打包售卖；
就本算法申请专利；以及任何违反 AGPL-3.0 的分发行为（不提供源码、不保留声明）。
本软件遵循 AGPL-3.0，允许商业使用，但必须保留声明并公开对应源码。
对冒充作者、原样转售安装器等行为，作者保留追究的权利（违者必究）。""",
    "tw": """第 1 條 · 授權
本安裝程式所安裝的修改版程式，其修改部分（Brick Bite 補丁及相關文件）以 GNU Affero General Public License v3.0（AGPL-3.0）發佈，與上游保持一致。
你被允許：自由使用、複製、修改、再散佈，包括商業使用；你被要求：在散佈（含透過網路提供服務）時公開對應原始碼，保留版權與授權聲明。

第 2 條 · 免責聲明（重要）
本軟體按「現狀」（AS IS）提供，不附帶任何明示或暗示的擔保，包括但不限於：適售性、特定用途適用性、不侵權，以及列印品質、尺寸精度、機械強度方面的任何保證。
使用本軟體可能導致：列印失敗、表面缺陷、尺寸偏差、材料與時間浪費、裝置損壞等。上述風險由使用者自行承擔。
作者與貢獻者不對任何直接、間接、附帶或後果性損失負責。

第 3 條 · 非官方聲明
本程式是社群實驗性修改，與 OrcaSlicer / Bambu Studio 官方及其維護者無任何隸屬、合作或背書關係。

第 4 條 · 安全使用
請先在廢料或測試模型上驗證效果；不建議用於承力結構、醫療、航空等場景。

第 5 條 · 資料與隱私
本安裝程式不收集、不上傳任何資料，不包含遙測。

第 6 條 · 第三方元件
包含 OrcaSlicer、Bambu Studio、OpenCASCADE、Boost、wxWidgets、OpenVDB、TBB 等開源元件，授權見安裝目錄中的 LICENSE 檔案。

第 7 條 · 署名
想法 / 方向 / 測試：@CAT0998
分析 / 實作 / 編譯 / 文件：AI — DeepSeek Harness / deepseek-flash

第 8 條 · 彩蛋條款
8.1 如果你真的把這份協議讀到了這裡，小鯨魚向你敬個禮。
8.2 本軟體不對「裝完忘記開啟磚砌咬合然後說沒效果」負責。
8.3 一週連續列印超過 30 小時，請讓機器休息一下。

第 9 條 · 使用邊界
可以：用本演算法列印模型並銷售成品；在自己的專案裡使用/移植本演算法（需署名並遵守 AGPL-3.0）。
不可以：把本專案的安裝程式或預編譯包改名後販售、打包進付費軟體、冒充作者、刪除署名、就本演算法申請專利。
簡單說：可以商用，但不能把「我和你一起開發的這個免費外掛」拿來賣錢。
安裝程式碼另有授權（INSTALLER-LICENSE.md），payload 中的程式遵循其上游 AGPL-3.0。

第 10 條 · 署名與使用規範
使用、移植或借鑑本演算法時，請保留以下署名：
· 想法與方向：@CAT0998
· 實作、分析、編譯與文件：AI — DeepSeek Harness / deepseek-flash
· 專案位址：https://github.com/CAT0998/brick-bite

明確禁止：刪除或隱藏署名；把本專案補丁/安裝程式改名後當作自己的成果發佈；把安裝程式原樣打包販售；
就本演算法申請專利；以及任何違反 AGPL-3.0 的散佈行為（不提供原始碼、不保留聲明）。
本軟體遵循 AGPL-3.0，允許商業使用，但必須保留聲明並公開對應原始碼。
對冒充作者、原樣轉售安裝程式等行為，作者保留追究的權利（違者必究）。""",
    "en": """Article 1 - License
The modifications installed by this program (the Brick Bite patch and related documents) are released under the GNU Affero General Public License v3.0 (AGPL-3.0), matching the upstream project.
You may: use, copy, modify and redistribute it freely, including commercially. You must: publish the corresponding source code when you distribute it (including over a network) and keep the copyright and license notices.

Article 2 - Disclaimer (important)
This software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to merchantability, fitness for a particular purpose, non-infringement, print quality, dimensional accuracy or mechanical strength.
Using it may cause print failures, surface defects, dimensional deviation, wasted material and time, or equipment damage. You accept these risks.
The authors and contributors are not liable for any direct, indirect, incidental or consequential damages.

Article 3 - Unofficial
This is a community experiment. It is not affiliated with, endorsed by, or supported by the OrcaSlicer or Bambu Studio projects.

Article 4 - Safe use
Validate the result on scrap or test models first. Do not use it for load-bearing, medical or aerospace parts.

Article 5 - Data and privacy
This installer collects nothing, uploads nothing and contains no telemetry.

Article 6 - Third-party components
This product includes open-source components such as OrcaSlicer, Bambu Studio, OpenCASCADE, Boost, wxWidgets, OpenVDB and TBB. See the LICENSE files in the installation folder.

Article 7 - Credits
Idea / direction / testing: @CAT0998
Analysis / implementation / build / documentation: AI - DeepSeek Harness / deepseek-flash

Article 8 - Easter eggs
8.1 If you actually read this far, the little whale salutes you.
8.2 We are not responsible for "I installed it, forgot to enable Brick wall mode, and saw no difference".
8.3 If you print more than 30 hours a week, give the machine a break.

Article 9 - Boundaries
Allowed: print models with this algorithm and sell the printed parts; use or port the algorithm in your own project (with credit and AGPL-3.0 compliance).
Not allowed: renaming and selling this installer or prebuilt packages, bundling them into paid software, claiming authorship, removing credits, or patenting the algorithm.
Installers are licensed separately (INSTALLER-LICENSE.md); the payload follows the upstream AGPL-3.0.

Article 10 - Attribution
When you use, port or borrow this algorithm, keep these credits:
- Idea and direction: @CAT0998
- Implementation, analysis, build and docs: AI - DeepSeek Harness / deepseek-flash
- Project: https://github.com/CAT0998/brick-bite

Explicitly forbidden: removing or hiding the credits; renaming this patch/installer and presenting it as your own; reselling the installer as-is;
patenting the algorithm; and any distribution that violates AGPL-3.0 (no source, no notices).
This software is AGPL-3.0: commercial use is allowed, but notices and source must be kept.
The authors reserve the right to pursue impersonation or resale of the installer as-is.""",
}


def T(key: str, **kwargs) -> str:
    entry = STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(LANG) or entry.get("en") or ""
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def agreement() -> str:
    return AGREEMENTS.get(LANG) or AGREEMENTS["en"]


def set_language(code: str) -> None:
    """Switch the active language at runtime ('zh' | 'tw' | 'en')."""
    global LANG
    if code in ("zh", "tw", "en"):
        LANG = code
