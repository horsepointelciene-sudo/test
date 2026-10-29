# 当前环境与版本（2026-10-23 核对）

| 项目 | 当前值 | 依据 |
|---|---|---|
| Sentaurus Workbench / gsub | W-2024.09-SP1 | 已有 GUI 记录及本次 `gsub -h` 横幅 |
| SDevice 实际运行版本 | W-2024.09-SP1 | 已有节点 15 的 `n15_des.log` 版本头，编译日期 2024-11-22 |
| SProcess 实际运行版本 | 待核对 | 本次没有对应运行日志，不能由 Workbench 版本推定 |
| 原版用户手册 | W-2024.09 | PDF 封面；来自 SP1 安装目录，不等于 SP1 修订说明 |
| TCAD Python | 3.11.1 | 直接解释器和 `gpythonsh` 均已实测导入 `swbpy2` |
| 安装根目录 | `/home/synopsys/sentaurus/W-2024.09-SP1` | 程序路径与目录检查 |
| STDB | `/home/liangxun/STDB` | SSH 环境实际值 |
| PDF 手册 | `$STROOT/tcad/$STRELEASE/manuals/PDFManual/data` | 目录存在；旧 `olh_sentaurus/pdf` 布局不适用 |
| 官方示例 | `$STROOT/tcad/$STRELEASE/Applications_Library` | 目录存在 |
| 教程 | `$STROOT/tcad/$STRELEASE/Sentaurus_Training` | 目录存在 |

## 当前连接与路径准备

在本机 PowerShell 使用现有入口：

```powershell
ssh.exe -F "$env:USERPROFILE\.ssh\tcad_a_20261022\config" -T -o BatchMode=yes tcad-b-jump whoami
```

服务器当前 SSH 会话未导出 `STROOT/STRELEASE`，但绝对路径工具正常。需要变量形式的命令时，仅在当前远端 shell 中设置：

```bash
export STROOT=/home/synopsys/sentaurus/W-2024.09-SP1
export STRELEASE=W-2024.09-SP1
export STDB=/home/liangxun/STDB
export PATH="$STROOT/bin:$PATH"
"$STROOT/tcad/$STRELEASE/linux64/bin/python3.11" -B -c 'import sys, swbpy2; print(sys.version); print(swbpy2.__file__)'
```

这些值仅适用于当前服务器，不修改登录脚本。实际项目路径由当前用户任务指定；版本识别、查询或回收不创建工程、不提交节点。

## 本地手册和脚本

- 当前本地官方手册根目录：`references/manuals/`。其中 `Sentaurus_W-2024.09-SP1_20261022/PDFManual/` 有 29 份 PDF，`Sentaurus_UserGuides_W-2024.09_20261022/` 有 26 份 PDF；两套资料中 24 份原版 User Guide 内容相同，按 SHA-256 去重后共 31 份可检索文档。
- 旧 H-2013.03 手册保留为基础参考；与当前版不同须说明差异。
- `build_index.sh` 默认递归读取上述本地手册根目录，按内容去重并用 `pdftotext -layout` 保留分页；`MANUAL_PDF_DIR` 可覆盖输入根目录。
- 建索引及搜索默认使用 `references/manual_index/W-2024.09-SP1/text`。两者均可用 `MANUAL_TEXT_DIR` 指向同一自定义目录；`SENTAURUS_TRAINING_DIR` 可覆盖本地教程路径。
- Python 3 辅助脚本不能交给服务器 `/usr/bin/python` 2.7.5；使用上述 3.11.1 或本机 Python 3。几何/曲线解析脚本不依赖固定 Sentaurus 发行版，实际输入格式仍需核对。

## 核对范围与证据

已核对安装路径、手册/示例目录、Python 导入、`Deck` 和 `Gtree` 主要 API 签名、`gsub` 帮助；没有创建工程、执行示例 deck 或提交仿真。SDE/SDevice 参考页保留示意内容，未运行部分标为待核对。

证据存于 `D:/onedrive/Desktop/TCAD_Work/project_notes/skill_version_update_20261023/`：`server_environment.json`、`python_examples_probe.json`、`swbpy2_api_probe.json`。节点日志依据来自已提交副本的实际路径，不改变后续默认在用户指定原工程运行的规则。
