# Changes in this build

This is an **unofficial, modified build** of [MCLauncher](https://github.com/MCMrARM/mc-w10-version-launcher) by MCMrARM. It is not affiliated with the original author, so please do not report problems with this build to them.

The modifications are applied automatically on top of the upstream source by [`tools/apply_fixes.py`](tools/apply_fixes.py) in GitHub Actions. This repository does not contain a modified copy of the source code. Each release comes with the complete corresponding source (`...-tweaked-source.zip`).

## Which versions are released

- If the fixes apply to the latest upstream release, this repository publishes the same tag and title as upstream, e.g. `0.7.0`.
- If the latest upstream release is older than the code the fixes were written for, the upstream default branch is built instead and published as a **pre-release** tagged `<upstream tag>+master.<commit>`, e.g. `0.7.0+master.4a4e213`.
- A fix is skipped automatically once upstream contains it.

## List of changes

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

## License

GPLv3, the same as upstream (see [`LICENSE.txt`](LICENSE.txt)). The upstream copyright and license remain; the changes above are by the maintainer of this repository.
