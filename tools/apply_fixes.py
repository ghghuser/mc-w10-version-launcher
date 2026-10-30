#!/usr/bin/env python3
"""Apply local fixes to a fresh checkout of MCMrARM/mc-w10-version-launcher.

Usage: python apply_fixes.py <path-to-upstream-checkout>

Every fix looks for an exact "before" text and replaces it with "after":
  before found (exactly once)  -> APPLIED
  "after" already present      -> ALREADY  (upstream fixed it, or it was applied before)
  neither                      -> NOT FOUND (upstream changed this code; update the fix below)
The exit code is 1 if any fix is NOT FOUND / AMBIGUOUS, unless ALLOW_MISSING=1.
Line endings (LF/CRLF) and a UTF-8 BOM are preserved.
"""
import os
import re
import sys

APPLIED, ALREADY, SKIPPED, NOT_FOUND, AMBIGUOUS = "APPLIED", "ALREADY", "SKIPPED", "NOT FOUND", "AMBIGUOUS"

NEW_UWP_URL = "https://raw.githubusercontent.com/ddf8196/mc-w10-versiondb-auto-update/master/versions.json.min"

MAIN = "MCLauncher/MainWindow.xaml.cs"
DIALOG = "MCLauncher/VersionListEndpointDialog.xaml.cs"


def B(s):
    """Blocks are written on their own lines for readability; drop the surrounding newlines."""
    return s.strip("\n")


def exact(name, before, after, already=None):
    """already: marker text that is only present once the fix has been applied
    (needed when `after` is a substring of `before`)."""
    before, after = B(before), B(after)
    marker = already if already is not None else after

    def run(text):
        if marker in text:
            return text, ALREADY
        n = text.count(before)
        if n == 1:
            return text.replace(before, after, 1), APPLIED
        return text, (NOT_FOUND if n == 0 else AMBIGUOUS)

    return name, run


def uwp_default_url():
    # Regex based on purpose: only the old, broken mrarm.io default is replaced.
    pat = re.compile(r'(private static readonly string VERSIONS_API_UWP = )"([^"]*)";')

    def run(text):
        m = pat.search(text)
        if not m:
            return text, NOT_FOUND
        if NEW_UWP_URL in m.group(2):
            return text, ALREADY
        if "mrarm.io" not in m.group(2):
            return text, SKIPPED  # upstream already moved to another endpoint; leave it alone
        return pat.sub(lambda mm: mm.group(1) + '"' + NEW_UWP_URL + '";', text, count=1), APPLIED

    return "UWP default endpoint (mrarm.io returns 502)", run


VERSIONLIST = "MCLauncher/VersionList.cs"
CSPROJ = "MCLauncher/MCLauncher.csproj"
ICON_NAME = "app-icon.ico"  # the workflow copies the fork's app-icon.ico to MCLauncher/app-icon.ico
ROOT = ""  # set in main()


def app_icon():
    # Embeds the icon into MCLauncher.exe. Does nothing when the fork has no app-icon.ico.
    tag = "<ApplicationIcon>" + ICON_NAME + "</ApplicationIcon>"
    anchor = re.compile(r"(?m)^([ \t]*)<OutputType>WinExe</OutputType>[ \t]*$")

    def run(text):
        if tag in text:
            return text, ALREADY
        if not os.path.isfile(os.path.join(ROOT, "MCLauncher", ICON_NAME)):
            return text, SKIPPED  # no icon provided
        if "<ApplicationIcon>" in text:
            return text, SKIPPED  # upstream defines its own icon now; leave it alone
        m = anchor.search(text)
        if not m:
            return text, NOT_FOUND
        return text[:m.end()] + "\n" + m.group(1) + tag + text[m.end():], APPLIED

    return "Embed " + ICON_NAME + " into MCLauncher.exe", run


FIXES = {
    CSPROJ: [
        app_icon(),
    ],
    VERSIONLIST: [
        # The list is downloaded as gzip/brotli when the server supports it (much less to transfer).
        exact("Accept compressed responses", r'''
        private readonly HttpClient _client = new HttpClient();
''', r'''
        private readonly HttpClient _client = new HttpClient(new HttpClientHandler { AutomaticDecompression = System.Net.DecompressionMethods.All });
'''),

        # UWP list: ask the official endpoint and the mirror at the same time, use the first valid answer.
        # An unreachable/dead endpoint therefore never delays the startup. A custom endpoint is used alone.
        exact("UWP list: try the official endpoint and the mirror in parallel (helpers)", r'''
        public WPFDataTypes.Version AddEntry(string name, string path, PackageType packageType) {
''', r'''
        private const string UWP_ENDPOINT_OFFICIAL = "https://mrarm.io/r/w10-vdb";
        private const string UWP_ENDPOINT_MIRROR = "@MIRROR@";

        // The known endpoints are all tried (the configured one first); a custom endpoint is used on its own.
        private List<string> GetUwpEndpoints() {
            var configured = (VersionsApiUWP ?? "").Trim();
            var known = new[] { UWP_ENDPOINT_OFFICIAL, UWP_ENDPOINT_MIRROR };
            if (configured == "" || known.Any(k => string.Equals(k, configured, StringComparison.OrdinalIgnoreCase))) {
                var result = new List<string>();
                if (configured != "") result.Add(configured);
                foreach (var k in known) {
                    if (!result.Any(r => string.Equals(r, k, StringComparison.OrdinalIgnoreCase))) result.Add(k);
                }
                return result;
            }
            return new List<string> { configured };
        }

        // Requests all URLs at the same time and returns the first valid response; the others are cancelled.
        // Only fails if every URL fails.
        private async Task<string> FetchFirstSuccessful(List<string> urls, Action<string> validate) {
            using (var cts = new System.Threading.CancellationTokenSource()) {
                var pending = urls.Select(url => FetchAndValidate(url, validate, cts.Token)).ToList();
                var errors = new List<Exception>();
                while (pending.Count > 0) {
                    var finished = await Task.WhenAny(pending);
                    pending.Remove(finished);
                    try {
                        var data = await finished;
                        cts.Cancel();
                        return data;
                    } catch (Exception e) {
                        errors.Add(e);
                    }
                }
                throw new AggregateException(errors);
            }
        }

        private async Task<string> FetchAndValidate(string url, Action<string> validate, System.Threading.CancellationToken token) {
            try {
                var resp = await _client.GetAsync(url, token);
                resp.EnsureSuccessStatusCode();
                var data = await resp.Content.ReadAsStringAsync(token);
                validate(data);
                Trace.WriteLine("Version list received from " + url);
                return data;
            } catch (Exception e) {
                throw new Exception(url + ": " + e.Message, e);
            }
        }

        public WPFDataTypes.Version AddEntry(string name, string path, PackageType packageType) {
'''.replace("@MIRROR@", NEW_UWP_URL), already="private List<string> GetUwpEndpoints()"),

        exact("UWP list: use the parallel download + log timings", r'''
            var resp = await _client.GetAsync(VersionsApiUWP);
            resp.EnsureSuccessStatusCode();
            var data = await resp.Content.ReadAsStringAsync();
            File.WriteAllText(_cacheFileUWP, data);
            ParseListUWP(JArray.Parse(data), false);
''', r'''
            var sw = Stopwatch.StartNew();
            var data = await FetchFirstSuccessful(GetUwpEndpoints(), s => JArray.Parse(s));
            Trace.WriteLine("UWP version list: downloaded after " + sw.ElapsedMilliseconds + " ms");
            File.WriteAllText(_cacheFileUWP, data);
            ParseListUWP(JArray.Parse(data), false);
            Trace.WriteLine("UWP version list: parsed and added after " + sw.ElapsedMilliseconds + " ms");
'''),

        exact("GDK list: log timings", r'''
            var resp = await _client.GetAsync(VersionsApiGDK);
            resp.EnsureSuccessStatusCode();
            var data = await resp.Content.ReadAsStringAsync();
            File.WriteAllText(_cacheFileGDK, data);
            ParseDataGDK(JObject.Parse(data), false);
''', r'''
            var sw = Stopwatch.StartNew();
            var resp = await _client.GetAsync(VersionsApiGDK);
            resp.EnsureSuccessStatusCode();
            var data = await resp.Content.ReadAsStringAsync();
            Trace.WriteLine("GDK version list: downloaded after " + sw.ElapsedMilliseconds + " ms (" + data.Length + " chars, " + VersionsApiGDK + ")");
            File.WriteAllText(_cacheFileGDK, data);
            ParseDataGDK(JObject.Parse(data), false);
            Trace.WriteLine("GDK version list: parsed and added after " + sw.ElapsedMilliseconds + " ms");
'''),

        # Keep the cached list on screen and only insert versions that are new, instead of
        # removing everything and re-adding it after the download.
        exact("Version list: helper to find entries that are already shown", r'''
        public void PrepareForReload() {
''', r'''
        // True if a downloaded (non-imported) entry with this name and package type is already in the list.
        private bool HasEntry(string name, PackageType packageType) {
            foreach (var v in this) {
                if (v.Name == name && v.PackageType == packageType && v.VersionType != WPFDataTypes.VersionType.Imported)
                    return true;
            }
            return false;
        }

        public void PrepareForReload() {
'''),

        exact("Version list (UWP): insert position for new versions", r'''
            foreach (JArray o in data.AsEnumerable().Reverse()) {
''', r'''
            int insertAt = 0; // new versions (not in the cached list) are inserted at the top
            foreach (JArray o in data.AsEnumerable().Reverse()) {
'''),

        exact("Version list (UWP): only add versions that are not shown yet", r'''
                Add(new WPFDataTypes.Version(o[1].Value<string>(), o[0].Value<string>(), (WPFDataTypes.VersionType)versionType, isNew, _commands, PackageType.UWP, null));
''', r'''
                if (!isCache && HasEntry(o[0].Value<string>(), PackageType.UWP)) continue; // already shown from the cache
                var entry = new WPFDataTypes.Version(o[1].Value<string>(), o[0].Value<string>(), (WPFDataTypes.VersionType)versionType, isNew, _commands, PackageType.UWP, null);
                if (isCache) Add(entry); else Insert(insertAt++, entry);
'''),

        exact("Version list (GDK): insert position for new versions", r'''
            foreach (var keyValue in data.Properties().Reverse()) {
''', r'''
            int insertAt = 0; // new versions (not in the cached list) are inserted at the top
            foreach (var keyValue in data.Properties().Reverse()) {
'''),

        exact("Version list (GDK): only add versions that are not shown yet", r'''
                Add(new WPFDataTypes.Version(WPFDataTypes.Version.UNKNOWN_UUID, versionName, versionType, isNew, _commands, PackageType.GDK, downloadUrls));
''', r'''
                if (!isCache && HasEntry(versionName, PackageType.GDK)) continue; // already shown from the cache
                var entry = new WPFDataTypes.Version(WPFDataTypes.Version.UNKNOWN_UUID, versionName, versionType, isNew, _commands, PackageType.GDK, downloadUrls);
                if (isCache) Add(entry); else Insert(insertAt++, entry);
'''),
    ],
    MAIN: [
        exact("Launch: check Minecraft.Windows.exe before replacing the installed package (helper)", r'''
        private void InvokeLaunch(Version v) {
''', r'''
        // Returns null when the game executable looks fine (or can't be checked), otherwise a description of the problem.
        // Launching re-registers the game and replaces the currently registered (Store) installation,
        // so a broken exe has to be caught BEFORE that happens.
        private static string? CheckGameExecutable(Version v) {
            try {
                string exePath = Path.Combine(Path.GetFullPath(v.GameDirectory), "Minecraft.Windows.exe");
                if (!File.Exists(exePath)) {
                    return v.PackageType == PackageType.GDK ? "Minecraft.Windows.exe was not found:\n" + exePath : null;
                }
                string invalid = "Minecraft.Windows.exe is not a valid Windows program (the file is damaged or still encrypted):\n" + exePath;
                using (var fs = new FileStream(exePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite)) {
                    var header = new byte[64];
                    if (fs.Read(header, 0, header.Length) < header.Length || header[0] != (byte)'M' || header[1] != (byte)'Z') {
                        return invalid;
                    }
                    int peOffset = BitConverter.ToInt32(header, 0x3C);
                    if (peOffset < 0 || peOffset > fs.Length - 4) {
                        return invalid;
                    }
                    fs.Seek(peOffset, SeekOrigin.Begin);
                    var sig = new byte[4];
                    if (fs.Read(sig, 0, sig.Length) < sig.Length || sig[0] != (byte)'P' || sig[1] != (byte)'E' || sig[2] != 0 || sig[3] != 0) {
                        return invalid;
                    }
                }
            } catch (Exception e) {
                // If the file can't be inspected, don't block the launch.
                Trace.WriteLine("Couldn't check Minecraft.Windows.exe: " + e.ToString());
            }
            return null;
        }

        private void InvokeLaunch(Version v) {
'''),

        exact("Launch: check Minecraft.Windows.exe before replacing the installed package (call)", r'''
                v.StateChangeInfo = new VersionStateChangeInfo(VersionState.MovingData);
                if (!MoveMinecraftData(v.GamePackageFamily, v.PackageType)) {
''', r'''
                var exeProblem = CheckGameExecutable(v);
                if (exeProblem != null) {
                    Trace.WriteLine("Launch aborted, game executable check failed: " + exeProblem);
                    MessageBox.Show(
                        "Can't launch " + v.DisplayName + ".\n\n" + exeProblem + "\n\n" +
                            "Nothing was changed: the currently installed Minecraft was NOT replaced.\n" +
                            "Remove this version in the launcher and install it again. For GDK versions, make sure Minecraft is installed from the Store first.",
                        "Launch error"
                    );
                    _hasLaunchTask = false;
                    return;
                }
                v.StateChangeInfo = new VersionStateChangeInfo(VersionState.MovingData);
                if (!MoveMinecraftData(v.GamePackageFamily, v.PackageType)) {
'''),

        uwp_default_url(),

        exact("Trim endpoints read from preferences.json", r'''
            var versionsApiUWP = UserPrefs.VersionsApiUWP != "" ? UserPrefs.VersionsApiUWP : VERSIONS_API_UWP;
            var versionsApiGDK = UserPrefs.VersionsApiGDK != "" ? UserPrefs.VersionsApiGDK : VERSIONS_API_GDK;
''', r'''
            // Trim so that stray spaces/newlines pasted into preferences.json or the dialog don't break the URL.
            var versionsApiUWP = !string.IsNullOrWhiteSpace(UserPrefs.VersionsApiUWP) ? UserPrefs.VersionsApiUWP.Trim() : VERSIONS_API_UWP;
            var versionsApiGDK = !string.IsNullOrWhiteSpace(UserPrefs.VersionsApiGDK) ? UserPrefs.VersionsApiGDK.Trim() : VERSIONS_API_GDK;
'''),

        exact("Migrate the dead mrarm.io endpoint saved in preferences.json", r'''
            // Trim so that stray spaces/newlines pasted into preferences.json or the dialog don't break the URL.
''', r'''
            // Older launcher versions saved the (now dead) default endpoint into preferences.json
            // when the endpoint dialog was closed with an empty field. Treat it as "default" again.
            if (UserPrefs.VersionsApiUWP != null && UserPrefs.VersionsApiUWP.Contains("mrarm.io")) {
                UserPrefs.VersionsApiUWP = VERSIONS_API_UWP;
                RewritePrefs();
            }
            // Trim so that stray spaces/newlines pasted into preferences.json or the dialog don't break the URL.
'''),

        exact("Launch: start the game directly if activation did not start it", r'''
                    Trace.WriteLine("App launch finished!");
''', r'''
                    Trace.WriteLine("App launch finished!");
                    await EnsureGameProcessStarted(v, gameDir);
'''),

        exact("Launch: fallback helper methods", r'''
        private async Task DeploymentProgressWrapper(
''', r'''
        // On some systems the AppX activation is accepted (LaunchAsync succeeds) but the game never starts,
        // while starting Minecraft.Windows.exe directly works (and fixes later activations too).
        // If no game process shows up after the activation, start the executable directly.
        private async Task EnsureGameProcessStarted(Version v, string gameDir) {
            if (v.PackageType != PackageType.GDK)
                return;
            string exePath = Path.Combine(gameDir, "Minecraft.Windows.exe");
            if (!File.Exists(exePath))
                return;
            for (int i = 0; i < 30; i++) {
                if (IsGameRunningFrom(exePath))
                    return;
                await Task.Delay(500);
            }
            Trace.WriteLine("Game process did not start after activation, starting it directly: " + exePath);
            try {
                Process.Start(new ProcessStartInfo {
                    FileName = exePath,
                    WorkingDirectory = gameDir,
                    UseShellExecute = false
                });
            } catch (Exception e) {
                Trace.WriteLine("Direct game start failed:\n" + e.ToString());
                MessageBox.Show("Failed to start the game directly:\n" + e.ToString());
            }
        }

        private static bool IsGameRunningFrom(string exePath) {
            foreach (var p in Process.GetProcessesByName("Minecraft.Windows")) {
                try {
                    if (string.Equals(p.MainModule?.FileName, exePath, StringComparison.OrdinalIgnoreCase))
                        return true;
                } catch (Exception) {
                    return true; // can't inspect it: assume it's ours, so we never start a second instance
                } finally {
                    p.Dispose();
                }
            }
            return false;
        }

        private async Task DeploymentProgressWrapper(
''', already="private async Task EnsureGameProcessStarted("),

        exact("Error dialog: collect errors (start)", r'''
            LoadingProgressLabel.Content = "Downloading new GDK version data";
''', r'''
            // Collect failures so the user sees which endpoint failed and why, in a single dialog.
            var downloadErrors = new List<string>();

            LoadingProgressLabel.Content = "Downloading new GDK version data";
'''),

        exact("Error dialog: GDK failure", r'''
                await _versions.DownloadVersionsGDK();
            } catch (Exception e) {
                Trace.WriteLine("List download failed:\n" + e.ToString());
                MessageBox.Show("Failed to update version list from the internet. Some new versions might be missing.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
''', r'''
                await _versions.DownloadVersionsGDK();
            } catch (Exception e) {
                Trace.WriteLine("GDK list download failed (" + _versions.VersionsApiGDK + "):\n" + e.ToString());
                downloadErrors.Add("GDK: " + _versions.VersionsApiGDK + "\n    " + e.GetType().Name + ": " + e.Message);
            }
'''),

        exact("Error dialog: UWP failure + show", r'''
                await _versions.DownloadVersionsUWP();
            } catch (Exception e) {
                Trace.WriteLine("List download failed:\n" + e.ToString());
                MessageBox.Show("Failed to update version list from the internet. Some new versions might be missing.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
''', r'''
                await _versions.DownloadVersionsUWP();
            } catch (Exception e) {
                Trace.WriteLine("UWP list download failed (" + _versions.VersionsApiUWP + "):\n" + e.ToString());
                downloadErrors.Add("UWP: " + _versions.VersionsApiUWP + "\n    " + e.GetType().Name + ": " + e.Message);
            }

            if (downloadErrors.Count > 0) {
                MessageBox.Show("Failed to update version list from the internet. Some new versions might be missing.\n\n" + string.Join("\n\n", downloadErrors), "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
'''),

        exact("List loading: show imported versions at the end (moved up)", r'''
            LoadingProgressLabel.Content = "Loading imported versions";
            LoadingProgressBar.Value = 5;
            await _versions.LoadImported();

            LoadingProgressGrid.Visibility = Visibility.Collapsed;
''', r'''
            // (imported versions were already loaded before the download)
            LoadingProgressGrid.Visibility = Visibility.Collapsed;
'''),

        exact("List loading: keep the cached list and only add new versions", r'''
            _versions.PrepareForReload();

            // Collect failures so the user sees which endpoint failed and why, in a single dialog.
''', r'''
            // The cached list stays visible while the download runs; the download only adds versions that are new.
            LoadingProgressLabel.Content = "Loading imported versions";
            LoadingProgressBar.Value = 3;
            await _versions.LoadImported();

            // Collect failures so the user sees which endpoint failed and why, in a single dialog.
''', already="The cached list stays visible while the download runs"),

        exact("Remove button asks for confirmation", r'''
        public ICommand RemoveCommand => new RelayCommand((v) => InvokeRemove((Version)v));
''', r'''
        public ICommand RemoveCommand => new RelayCommand((v) => ConfirmAndInvokeRemove((Version)v));
'''),

        exact("Remove confirmation dialog", r'''
        private void InvokeRemove(Version v) {
            Task.Run(async () => await Remove(v));
        }
''', r'''
        private void InvokeRemove(Version v) {
            Task.Run(async () => await Remove(v));
        }

        // Used by the per-version Remove button: ask for confirmation first.
        // (Uninstall-all has its own confirmation and calls InvokeRemove directly.)
        private void ConfirmAndInvokeRemove(Version v) {
            var result = MessageBox.Show(
                "Are you sure you want to remove " + v.DisplayName + "?\n" +
                    "The game files for this version will be unregistered and deleted.\n" +
                    "Your data (worlds, etc.) won't be removed.",
                "Remove confirmation",
                MessageBoxButton.YesNo,
                MessageBoxImage.Question,
                MessageBoxResult.No
            );
            if (result == MessageBoxResult.Yes) {
                InvokeRemove(v);
            }
        }
'''),

        exact("Endpoint dialog: apply new endpoints to the running VersionList", r'''
            UserPrefs.VersionsApiUWP = newUwpIdsEndpoint == "" ? VERSIONS_API_UWP : newUwpIdsEndpoint;
            UserPrefs.VersionsApiGDK = newGdkPackageUrlsEndpoint == "" ? VERSIONS_API_GDK : newGdkPackageUrlsEndpoint;
''', r'''
            UserPrefs.VersionsApiUWP = string.IsNullOrWhiteSpace(newUwpIdsEndpoint) ? VERSIONS_API_UWP : newUwpIdsEndpoint.Trim();
            UserPrefs.VersionsApiGDK = string.IsNullOrWhiteSpace(newGdkPackageUrlsEndpoint) ? VERSIONS_API_GDK : newGdkPackageUrlsEndpoint.Trim();
            // The running VersionList keeps its own copy of the endpoints, so it must be updated too;
            // otherwise the new endpoint is ignored until the launcher is restarted.
            _versions.VersionsApiUWP = UserPrefs.VersionsApiUWP;
            _versions.VersionsApiGDK = UserPrefs.VersionsApiGDK;
'''),

        exact("Endpoint dialog: pass GDK endpoint too", r'''
            var dialog = new VersionListEndpointDialog(UserPrefs.VersionsApiUWP) {
''', r'''
            var dialog = new VersionListEndpointDialog(UserPrefs.VersionsApiUWP, UserPrefs.VersionsApiGDK) {
'''),
    ],
    DIALOG: [
        exact("Endpoint dialog: show the current GDK endpoint", r'''
        public VersionListEndpointDialog(string currentEndpoint) {
            InitializeComponent();
            EndpointTextBox.Text = currentEndpoint;
        }
''', r'''
        public VersionListEndpointDialog(string currentUwpEndpoint, string currentGdkEndpoint) {
            InitializeComponent();
            EndpointTextBox.Text = currentUwpEndpoint;
            GDKUrlsEndpointTextBox.Text = currentGdkEndpoint;
        }
'''),
    ],
}


def read_text(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    return text.replace("\r\n", "\n"), bom, crlf


def write_text(path, text, bom, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    global ROOT
    root = ROOT = sys.argv[1]
    if not os.path.isfile(os.path.join(root, "MCLauncher.sln")):
        print("MCLauncher.sln not found in " + root)
        return 2

    results = []
    for rel, fixes in FIXES.items():
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            results += [(rel, name, NOT_FOUND) for name, _ in fixes]
            continue
        text, bom, crlf = read_text(path)
        original = text
        for name, run in fixes:
            text, status = run(text)
            results.append((rel, name, status))
        if text != original:
            write_text(path, text, bom, crlf)

    lines = ["| Status | File | Fix |", "|---|---|---|"]
    for rel, name, status in results:
        lines.append("| %s | %s | %s |" % (status, rel, name))
    report = "\n".join(lines)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Applied fixes\n\n" + report + "\n")

    bad = [r for r in results if r[2] in (NOT_FOUND, AMBIGUOUS)]
    if bad:
        print("\n%d fix(es) could not be applied because upstream changed the code:" % len(bad))
        for rel, name, status in bad:
            print("  - [%s] %s: %s" % (status, rel, name))
        if os.environ.get("ALLOW_MISSING") == "1":
            print("ALLOW_MISSING=1, continuing anyway.")
            return 0
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
