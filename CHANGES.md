# Changes in this build / このビルドの変更点

[English](#english) | [日本語](#日本語)

---

## English

This is an **unofficial, modified build** of [MCLauncher](https://github.com/MCMrARM/mc-w10-version-launcher) by MCMrARM. It is not affiliated with the original author, so please do not report problems with this build to them.

The modifications are applied automatically on top of the upstream source by [`tools/apply_fixes.py`](tools/apply_fixes.py) in GitHub Actions. This repository does not contain a modified copy of the source code. Each release comes with the complete corresponding source (`...-tweaked-source.zip`).

### Which versions are released

- If the fixes apply to the latest upstream release, this repository publishes the same tag and title as upstream, e.g. `0.7.0`.
- If the latest upstream release is older than the code the fixes were written for, the upstream default branch is built instead and published as a **pre-release** tagged `<upstream tag>+master.<commit>`, e.g. `0.7.0+master.4a4e213`.
- A fix is skipped automatically once upstream contains it.

### List of changes

**Version list**
- Accept gzip/brotli compressed responses (smaller downloads).
- UWP list: request the official endpoint and the mirror at the same time and use the first valid answer, so a dead endpoint no longer delays startup. A custom endpoint is used on its own.
- UWP default endpoint: the old default (`mrarm.io`, returns 502) is replaced by the [mirror](https://github.com/ddf8196/mc-w10-versiondb-auto-update). An endpoint saved in `preferences.json` by older versions is migrated back to the default.
- Keep the cached list on screen and only insert versions that are new (at the top), instead of clearing the list and re-adding everything after the download. Imported versions are loaded before the download.
- Log how long downloading and parsing the UWP/GDK lists took.

**Launching**
- Before the installed package is replaced, check that `Minecraft.Windows.exe` is a valid Windows program. If it is missing, damaged or still encrypted, an error is shown and nothing is changed, so the currently installed Minecraft is not replaced by a broken one.
- If the activation is accepted but the game does not start within about 10 seconds, start `Minecraft.Windows.exe` directly (GDK versions only).

**Dialogs and settings**
- The "failed to update version list" dialog now shows which endpoint failed and why, in a single dialog.
- Endpoints are trimmed, so stray spaces or newlines pasted into `preferences.json` or the dialog no longer break the URL. A blank value means "default".
- Changing the endpoints in the dialog takes effect immediately, without restarting the launcher. The dialog also shows the current GDK endpoint.
- The per-version Remove button asks for confirmation first.

**Build**
- Optionally embeds a custom icon into `MCLauncher.exe` (`tools/app-icon.ico`).

### License

GPLv3, the same as upstream (see [`LICENSE.txt`](LICENSE.txt)). The upstream copyright and license remain; the changes above are by the maintainer of this repository.

---

## 日本語

[MCMrARM 氏の MCLauncher](https://github.com/MCMrARM/mc-w10-version-launcher) の**非公式の改変ビルド**です。元の作者とは無関係ですので、このビルドの不具合を元の作者に報告しないでください。

改変は GitHub Actions で、[`tools/apply_fixes.py`](tools/apply_fixes.py) が公式ソースに自動で適用しています。このリポジトリに改変済みのソースコードは置いていません。各 Release には、対応するソースコード一式（`...-tweaked-source.zip`）を添付しています。

### 公開されるバージョン

- 公式の最新 release に修正が適用できる場合は、公式と同じタグ・タイトル（例: `0.7.0`）で公開します。
- 公式の最新 release が、修正の前提としているコードより古い場合は、公式の既定ブランチをビルドして、`<公式タグ>+master.<コミット>`（例: `0.7.0+master.4a4e213`）の**プレリリース**として公開します。
- 公式側に同じ修正が入った場合、その修正は自動でスキップされます。

### 変更内容

**バージョン一覧**
- gzip/brotli 圧縮のレスポンスに対応しました（ダウンロード量が減ります）。
- UWP一覧: 公式エンドポイントとミラーに同時にリクエストして、最初に有効だった応答を使います。死んでいるエンドポイントがあっても起動が遅れません。カスタムエンドポイントを指定した場合は、それだけを使います。
- UWPの既定エンドポイント: 旧既定（`mrarm.io`、502を返す）を[ミラー](https://github.com/ddf8196/mc-w10-versiondb-auto-update)に置き換えました。古いバージョンが `preferences.json` に保存した旧エンドポイントは、既定に戻します。
- キャッシュした一覧を表示したまま、新しいバージョンだけを先頭に追加します（これまでは一覧を空にして、ダウンロード後に全部入れ直していました）。インポート済みバージョンは、ダウンロード前に読み込みます。
- UWP/GDK一覧のダウンロードと解析にかかった時間をログに出します。

**起動**
- インストール済みのパッケージを置き換える前に、`Minecraft.Windows.exe` が正しい Windows プログラムか検査します。ファイルが無い・壊れている・暗号化されたままの場合はエラーを表示し、何も変更しません。壊れたバージョンで、いま入っている Minecraft を上書きしてしまうことがなくなります。
- アクティベーションは受け付けられたのに約10秒たってもゲームが起動しない場合は、`Minecraft.Windows.exe` を直接起動します（GDK版のみ）。

**ダイアログと設定**
- 「バージョン一覧の更新に失敗しました」のダイアログに、どのエンドポイントがなぜ失敗したかを、1つのダイアログにまとめて表示します。
- エンドポイントの前後の空白を取り除きます。`preferences.json` やダイアログに混入した空白・改行で URL が壊れることがなくなります。空欄は「既定」として扱います。
- ダイアログでエンドポイントを変更すると、ランチャーを再起動しなくても反映されます。ダイアログには、現在の GDK エンドポイントも表示します。
- バージョンごとの削除ボタンは、先に確認を求めます。

**ビルド**
- 任意で、`MCLauncher.exe` に独自のアイコンを埋め込みます（`tools/app-icon.ico`）。

### ライセンス

上流と同じ GPLv3 です（[`LICENSE.txt`](LICENSE.txt) 参照）。元の著作権とライセンスはそのまま残り、上記の変更はこのリポジトリの管理者によるものです。
