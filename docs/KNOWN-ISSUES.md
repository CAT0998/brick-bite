# 已知问题与处置（Known issues）

面向 **Brick Bite v1.3.1**（OrcaSlicer v2.5.2 / Bambu Studio 02.09.02.62 两个构建）。

---

## 1. Bambu Studio：提示「请在登陆前安装网络插件」，点了也装不上

### 现象

Bambu Studio 首页左上角出现橙色提示「请在登陆前安装网络插件」。点其中的「安装」会弹出
「正在下载Bambu网络插件」，随后报 **「插件下载失败。请检查您的防火墙设置和vpn软件」**，重试也无效。
切片、导出、砖砌咬合功能都正常，但登录 / 云打印 / 设备页用不了。

### 成因（三条叠加）

1. **这个构建是 internal testing 版，数据目录和官方不同。**
   `version.inc` 在非官方发布环境下把 `BBL_INTERNAL_TESTING` 置为 1，而
   `src/slic3r/GUI/GUI_App.cpp::init_app_config()` 里有：

   ```cpp
   #if BBL_INTERNAL_TESTING
       data_dir += BBL_INTERNAL_TESTING == 1 ? "Internal" : "Beta";
   #endif
   ```

   于是程序读写 `%APPDATA%\BambuStudioInternal`，而官方版用 `%APPDATA%\BambuStudio`。

2. **网络插件在官方目录里，新目录里没有。**
   插件是 7 个 DLL（`bambu_networking.dll`、`BambuSource.dll`、`agora_rtc_sdk.dll`、
   `libagora-ffmpeg.dll`、`libagora-soundtouch.dll`、`libaosl.dll`、`live555.dll`），
   装在 `<数据目录>\plugins` 下。程序在自己的目录里找不到插件，判定「未安装网络组件」。

3. **应用内下载在这类构建里是坏的。**
   它会先查
   `https://api.bambulab.com/v1/iot-service/api/slicer/resource?slicer/plugins/cloud=02.09.02.00`
   （返回插件 02.09.02.50 的下载地址），再下载约 47 MB 的 zip。**网络本身是通的**
   （实测该 zip 4~10 秒下完），失败发生在程序自己的 HTTP 栈：构建出来的二进制里写死了
   编译机上的证书路径 `D:\CAD_Workspace\08_orca_build\bambu_deps\usr\local/cert.pem`，
   该文件不存在时它无法校验 HTTPS，于是下载直接失败。

### 处置

- **v1.3.1 起的安装器自动处理**：复制完文件后，安装器读取 `bambu-studio.exe` 的版本 →
  向 Bambu 资源接口查询匹配的插件 → 下载并解包到 `%APPDATA%\BambuStudioInternal\plugins`；
  离线时退化为复制官方安装的 `plugins` 目录。完成页会显示「网络插件已就绪」。
- **已经装了 v1.3.0 的**：手动把 `%APPDATA%\BambuStudio\plugins` 整个目录复制到
  `%APPDATA%\BambuStudioInternal\plugins` 即可；或用 v1.3.1 安装器重跑一次（会拉到版本匹配的插件）。
- 首次加载插件时 Windows 防火墙会弹框，务必选 **「允许访问」**，否则设备发现 / 云打印不可用。
- **根本修复（下一个构建）**：用公开版配置构建（`-DBBL_INTERNAL_TESTING=0`），数据目录回到
  `%APPDATA%\BambuStudio`，插件与官方版本通用；同时把 deps 里 OpenSSL/curl 的 CA 路径改成
  安装目录内的相对路径并随包分发 ca-bundle。

---

## 2. OrcaSlicer：没有同样的问题

- 数据目录就是标准的 `%APPDATA%\OrcaSlicer`（`GUI_App.cpp::init_app_config()` 没有 Internal 后缀逻辑），
  装完 Brick Bite 版的 OrcaSlicer 仍然读你原来的配置、预设与最近文件。
- 网络插件按**版本化文件名**存放（`plugins\bambu_networking_<版本>.dll`），程序按配置项
  `network_plugin_version` 选版本，最老的 `02.03.00` 系列也能加载（仅个别新功能不可用）。
- 因此 OrcaSlicer 不会出现「装不上网络组件」的阻断。请注意版本：

  | 项 | 值 |
  |---|---|
  | 配置位置 | `%APPDATA%\OrcaSlicer\OrcaSlicer.conf` |
  | 键 | `"network_plugin_version"` |
  | 2.5.2 支持的最新系列 | `02.08.04`（文件 `bambu_networking_02.08.04.60.dll`） |
  | 回退系列 | `02.03.00` |

  想把旧版升级到最新系列：把 `win_02.08.04.60.zip` 里的 `bambu_networking.dll` 解出来，
  重命名为 `bambu_networking_02.08.04.60.dll` 放进 `%APPDATA%\OrcaSlicer\plugins\`，
  再把 `network_plugin_version` 改成 `02.08.04`。

---

## 3. Windows 防火墙

首次加载网络插件时系统会弹「Windows Defender 防火墙已阻止此应用的部分功能」。
勾选需要的网络类型后点「允许访问」。若曾误点「取消」，到「允许应用通过防火墙」里手动勾上
`bambu-studio.exe` 即可。

---

## 4. Bambu Studio 的安装目录必须是纯英文路径

中文或其它非 ASCII 路径会让程序启动即崩（`boost::filesystem::create_directories: Invalid argument`）。
安装器的「自动检测」给出的都是 ASCII 路径，手动指定时也请遵守。
