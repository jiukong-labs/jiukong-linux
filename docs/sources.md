# 官方來源與授權查核

查核日期：2026-10-15。第三方來源可能改變；指紋或流程改變時安裝器應停止，由維護者重新查核。

- [Debian 13 發行公告](https://www.debian.org/News/2025/20250809)、[live-build 套件](https://packages.debian.org/trixie/live-build)、[lb_config 手冊](https://manpages.debian.org/trixie/live-build/lb_config.1.en.html)：使用 trixie、官方核心及 live installer。套件名稱另以 trixie main/non-free-firmware amd64 Packages 索引核對。
- [Debian 安裝手冊](https://www.debian.org/releases/trixie/amd64/)、[Debian 授權指引](https://www.debian.org/social_contract#guidelines)：保留各套件 `/usr/share/doc/*/copyright`。non-free-firmware 有個別重新散布條件，發行前須保存套件／版號清單逐項檢查。此專案不宣稱所有韌體為 MIT，也不移除原始授權文件。
- [VS Code 官方 Debian 安裝](https://code.visualstudio.com/docs/setup/linux)、[VS Code 授權](https://code.visualstudio.com/license)：Microsoft repository `https://packages.microsoft.com/repos/code`，key `https://packages.microsoft.com/keys/microsoft.asc`。目前主指紋 `BC528686B50D79E339D3721CEB3E94ADBE1229CF`；預建 VS Code 與原始碼授權不同，採使用者安裝，不收入 ISO。
- [Codex CLI 官方文件](https://learn.chatgpt.com/docs/codex/cli)、[IDE 文件](https://learn.chatgpt.com/docs/codex/ide)：採官方 npm 安裝選項。`@openai/codex` metadata 與鎖檔記錄 Apache-2.0、Node >=16；本專案使用 Debian 13 受支援的 Node >=20。版本與 integrity 寫入 lockfile，不包含下載的二進位。
- [ChatGPT Linux 官方文件](https://learn.chatgpt.com/docs/linux/linux-app)：Debian 13 x64 在 Linux preview 支援範圍。下載頁指向 `persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb`；已唯讀檢查此套件 control/postinst 的官方 APT URL。金鑰來源與主指紋 `3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4` 由 [官方 Linux installer](https://persistent.oaistatic.com/codex-app-prod/linux/install-arch.sh) 交叉核對。此專案使用同一 signed Debian repo，沒有執行 Arch 安裝器。
- [Claude Code setup](https://code.claude.com/docs/en/setup)、[VS Code 整合](https://code.claude.com/docs/en/vs-code)：支援 Debian、4 GB+；官方 signed APT stable。主指紋 `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`，來源 `https://downloads.claude.ai/keys/claude-code.asc`。
- [Claude Desktop Linux 官方安裝](https://support.claude.com/en/articles/10065433-install-claude-desktop)：Linux beta 支援 Debian 12+ x64，採 Anthropic 官方 APT。相同指紋、Desktop key URL `https://downloads.claude.ai/claude-desktop/key.asc`。Cowork 另需至少 8 GB，不符合本機目標。
- [Anthropic 消費者條款](https://www.anthropic.com/legal/consumer-terms)、[商業條款](https://www.anthropic.com/legal/commercial-terms)、[OpenAI 條款](https://openai.com/policies/terms-of-use/)：工具使用及帳號受各自條款約束。本專案沒有取得專有工具再散布授權，故只提供安裝器，不將它們或登入資料打包入 ISO。

VS Code Marketplace 擴充套件保留發布者授權，不打包進 ISO。發行韌體／ISO 前還須完成整份套件清單的授權審查與必要原始碼提供義務；目前尚未完成發行級授權審查，不應發布為正式 Release。
