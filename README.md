# MCLauncher (tweaked build) / MCLauncher（tweaked ビルド）

[English](#english) | [日本語](#日本語) | [Original README / 公式のREADME](#mclauncher)

## English

This repository publishes an **unofficial, modified build** of [MCMrARM/mc-w10-version-launcher](https://github.com/MCMrARM/mc-w10-version-launcher). It is not affiliated with the original author.

- **Download**: the [Releases](../../releases) section of this repository. Unzip it somewhere and run `MCLauncher.exe`.
- **What is different**: see [CHANGES.md](CHANGES.md).
- **How it is built**: GitHub Actions takes the upstream source, applies [`tools/apply_fixes.py`](tools/apply_fixes.py) and builds it. Releases are published with the same tag as upstream; when the fixes do not apply to the latest upstream release, the upstream default branch is built and published as a pre-release tagged `<upstream tag>+master.<commit>`. This repository does not contain a modified copy of the source code; each release has the complete corresponding source attached (`...-tweaked-source.zip`).
- **License**: GPLv3, the same as upstream (see [LICENSE.txt](LICENSE.txt)).

The usage instructions below are the original ones from upstream. Replace the download location with this repository's [Releases](../../releases) if you want this build.

## 日本語

[MCMrARM/mc-w10-version-launcher](https://github.com/MCMrARM/mc-w10-version-launcher) の**非公式の改変ビルド**を公開するリポジトリです。元の作者とは無関係です。

- **ダウンロード**: このリポジトリの [Releases](../../releases) から取得して、好きな場所に展開し、`MCLauncher.exe` を実行してください。
- **違い**: [CHANGES.md](CHANGES.md) を参照してください。
- **ビルド方法**: GitHub Actions が公式ソースを取得して、[`tools/apply_fixes.py`](tools/apply_fixes.py) を適用してビルドします。Release は公式と同じタグで公開します。公式の最新 release に修正が適用できない場合は、公式の既定ブランチをビルドして、`<公式タグ>+master.<コミット>` のプレリリースとして公開します。このリポジトリに改変済みのソースコードは置いておらず、各 Release に対応するソースコード一式を添付しています（`...-tweaked-source.zip`）。
- **ライセンス**: 上流と同じ GPLv3 です（[LICENSE.txt](LICENSE.txt) 参照）。

以下は上流の元の README です（英語）。この改変ビルドを使う場合は、ダウンロード先をこのリポジトリの [Releases](../../releases) に読み替えてください。

---

# MCLauncher

This tool allows you to install several versions of Minecraft: Windows 10 Edition (Bedrock) side-by-side.
This is useful if you want to test beta versions, releases or anything else side-by-side without needing to uninstall and reinstall the game.

## Disclaimer
This tool will **not** help you to pirate the game; it requires that you have a Microsoft account which can be used to download Minecraft from the Store.

## Prerequisites
- A Microsoft account connected to Microsoft Store which **owns Minecraft for Windows 10**
- **Administrator permissions** on your user account (or access to an account that has)
- **Developer mode** enabled for app installation in Windows 10 Settings
- If you want to be able to use beta versions, you'll additionally need to **subscribe to the Minecraft Beta program using Xbox Insider Hub**.
- [Microsoft Visual C++ Redistributable](https://aka.ms/vs/16/release/vc_redist.x64.exe) installed.

## Setup
- Download the latest release from the [Releases](https://github.com/MCMrARM/mc-w10-version-launcher/releases) section. Unzip it somewhere.
- Run `MCLauncher.exe` to start the launcher.

## Common Pitfalls and Issues
Unfortunately the launcher has become quite unreliable with the migration to GDK.
Combined with Windows 11's steady worsening in quality and stability, most of these issues seem to be caused by Windows itself, while others are caused by the method the launcher uses to extract the game files.

As I (@dktapps) don't use Windows as my primary OS anymore, and find Windows very tiresome to deal with, it's not likely these will get significantly improved, so here are some known issues and workarounds.

### `Invalid argument` error when launching the game via the start menu
Move the launcher to a shorter path, and launch it at least one time from inside the launcher after moving it.

This seems to be a result of the path to `Minecraft.Windows.exe` being too long somehow, and the issue seems to occur on newer versions of Windows even if MAX_PATH is increased.
Older versions didn't have this issue, so it's not clear what caused the issue.

### Failed to decrypt Minecraft.Windows.exe
- Make sure you installed Minecraft (or Minecraft Preview) from the Store before using the launcher
- A valid license is required, you can't pirate the game using the launcher
- Sometimes using `Tools -> Cleanup for installing Minecraft from Microsoft Store` may help resolve issues
- Try rebooting the machine if all else fails. Sometimes Windows's services get glitchy for no obvious reason and cause issues that a reboot will sometimes clear out

### Invalid 16-bit application or SmartScreen saying "this app can't run on your PC"
This is usually a failure to get a decrypted version of the Minecraft exe. Try the steps above first, but also check `File -> Open log file` and see if any errors are present

### `minecraft://` and similar deeplinks not working
Check keys like `HKEY_CLASSES_ROOT\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\PackageRepository\Extensions\windows.protocol\minecraft` and similar keys for duplicate entries.

Sometimes the registry ends up with duplicate entries for these protocols for reasons that aren't yet clear.

Deleting the dead entries may help fix deeplinks.

## Compiling the launcher yourself
You'll need Visual Studio with Windows 10 SDK version 10.0.17763 and .NET Framework 4.6.1 SDK installed. You can find these in the Visual Studio Installer if you don't have them out of the box.
The project should build out of the box with VS as long as you haven't done anything bizarre.

## Frequently Asked Questions
**Does this allow running multiple instances of Minecraft: Bedrock at the same time?**

At the time of writing, no. It allows you to _install_ multiple versions, but only one version can run at a time.
