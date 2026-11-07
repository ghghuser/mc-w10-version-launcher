# What is different from the official MCLauncher

This is an **unofficial, modified version** of [MCLauncher](https://github.com/MCMrARM/mc-w10-version-launcher) by MCMrARM. It is not affiliated with the original author, so please do not report problems with this version to them.

## What is improved in the app

**The version list works again, and shows up faster**
- The old server that the launcher used for the older (UWP) versions is down and returns an error, so the version list could not load. This version switches to a working copy automatically.
- If one server is slow or down, the launcher no longer waits for it. It asks both servers at once and uses whichever answers first.
- The list you saw last time stays on screen while the launcher checks for updates, and new versions are simply added at the top. You no longer see an empty list while it loads.
- Downloads are a little smaller, so the list loads quicker.

**Safer launching and removing**
- Before launching a version, the launcher checks that the game's main file is not damaged. If it is damaged, you get a message and **your currently installed Minecraft is left untouched**. (Before, a broken version could replace the working one.)
- If you launch a newer (GDK) version and the game does not open at all, the launcher now starts it directly.
- The Remove button now asks "Are you sure?" before deleting a version.

**Clearer messages and settings**
- When the version list cannot be updated, the message now says which server failed and why, instead of only saying "failed".
- Changing the version list server address in the settings takes effect right away, without restarting the launcher. Extra spaces typed or pasted into the address are ignored.

**Other**
- Added an icon to the EXE file..

Anything that the official version fixes on its own later is skipped automatically, so these changes do not pile up on top of the official ones.

## Which version should I download?

Download from this repository's **Releases** page.

- A release named like `0.7.0` is the official `0.7.0` with the changes above.
- A release named like `0.7.0+master.4a4e213` is marked **pre-release**. It is based on the newest official code, which is newer than the official `0.7.0` release but has not been officially released yet. It may be less tested.

## For developers

- The changes are applied automatically to the official source by [`tools/apply_fixes.py`](tools/apply_fixes.py) in GitHub Actions, which then builds the app. This repository does not contain a modified copy of the source code.
- Each release has the complete corresponding source attached (`...-tweaked-source.zip`).
- Licensed under GPLv3, the same as the official version (see [`LICENSE.txt`](LICENSE.txt)). The original copyright and license remain; the changes above are by the maintainer of this repository.
