# What is different from the official MCLauncher

This is an **unofficial, modified version** of [MCLauncher](https://github.com/MCMrARM/mc-w10-version-launcher) by MCMrARM. It is not affiliated with the original author, so please do not report problems with this version to them.

## What is changed in the app

**Version list**
- The server that the launcher uses by default for the older (UWP) versions is no longer responding (it returns an error), so this version uses a working copy of the list instead. It switches automatically.
- The launcher asks both servers at once and uses whichever answers first, so it does not wait for a slow or unavailable server.
- The list from last time stays on screen while the launcher checks for updates, and new versions are added at the top. The list is not emptied while it loads.
- Downloads use compression, so they are a little smaller.

**Launching and removing**
- Before launching a version, the launcher checks that the game's main file is not damaged. If it is damaged, a message is shown and **your currently installed Minecraft is left untouched**. (Without this check, a damaged version could replace the one that is working.)
- If you launch a newer (GDK) version and the game does not open at all, the launcher starts it directly.
- The Remove button asks "Are you sure?" before deleting a version.

**Messages and settings**
- When the version list cannot be updated, the message says which server failed and why, instead of only saying "failed".
- Changing the version list server address in the settings takes effect right away, without restarting the launcher. Extra spaces typed or pasted into the address are ignored.

**Other**
- An icon is added to the EXE file.

If the official version later makes the same change on its own, the matching change here is skipped automatically, so the two do not conflict.

## Which version should I download?

Download from this repository's **Releases** page.

- A release named like `0.7.0` is the official `0.7.0` with the changes above.
- A release named like `0.7.0+master.4a4e213` is marked **pre-release**. It is based on the newest official code, which is newer than the official `0.7.0` release but has not been officially released yet. It may be less tested.

## For developers

- The changes are applied automatically to the official source by [`tools/apply_fixes.py`](tools/apply_fixes.py) in GitHub Actions, which then builds the app. This repository does not contain a modified copy of the source code.
- Each release has the complete corresponding source attached (`...-tweaked-source.zip`).
- Licensed under GPLv3, the same as the official version (see [`LICENSE.txt`](LICENSE.txt)). The original copyright and license remain; the changes above are by the maintainer of this repository.
