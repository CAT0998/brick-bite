本次更新：适配 OrcaSlicer **v2.4.2** 官方源码，并提供 Windows 预编译安装器。

## 新增
- `brick_bite_2.4.2.patch`：2.4.2 源码补丁（已在 v2.4.2 上编译验证）
- `INSTALLER.md`：安装器说明
- 两个安装器（Release 附件 / 桌面打包）：
  - **BrickBite-Installer-2.4.2**：适用于 OrcaSlicer v2.4.2
  - **BrickBite-Installer-2.3.2**：适用于 2.3.2-dev 构建

## 安装器特性
- 自动检测 / 手动指定 OrcaSlicer 目录
- 按 SHA256 逐个文件比对，只替换有差异的文件（resources 目录通常完全跳过）
- 替换前自动备份为 *.brickbite.bak，可恢复
- 许可与免责声明、鲸鱼娘界面、进度与日志

## 验证
- 2.4.2 构建产物 OrcaSlicer.dll 已确认包含「砖砌咬合：首圈半宽交替 (Brick bite)」及两种模式字符串
- 补丁可干净应用到 v2.4.2 源码（git apply --check 通过）

## 署名
- 想法 / 方向 / 测试：**@CAT0998**
- 分析 / 实现 / 编译 / 文档 / 安装器：**AI — DeepSeek Harness / deepseek-flash（DeepSeek-V4.1-Flash，build 1017）**
