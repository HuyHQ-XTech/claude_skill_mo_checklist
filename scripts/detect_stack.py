#!/usr/bin/env python3
"""Nhận diện stack của 1 repo Android xTech (chỉ đọc, stdlib).

  detect_stack.py [repo_dir] [--json]

In ra: mã app, applicationId, version xtechads/plugin (hoặc "không dùng SDK"), UI (Compose/XML),
DI (Koin/Hilt), navigation (Nav3/Nav2/Fragment), module, min/compile/target SDK, file mấu chốt cho
MO và lệnh verify (đọc từ CLAUDE.md / ~/.claude/night-dev/projects.yaml).
"""
import json
import os
import re
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"build", ".gradle", ".git", ".idea", "node_modules", ".claude", "intermediates", ".cxx",
             "generated", "baselineprofile"}
SRC_EXT = (".kt", ".java")

KEY_FILES = {
    "application": r"class\s+\w+\s*(?:\([^)]*\))?\s*:\s*(?:\w+\.)*(?:MultiDex)?Application\s*\(",
    "main_activity": r"class\s+MainActivity\b",
    "splash": r"(?:fun|class)\s+Splash(?:Screen|Activity|Fragment|ViewModel)\b",
    "ads_manager": r"class\s+\w*AdsManager\b",
    "prefs_rc": r"class\s+(?:SharedPrefs|AppPrefs|Prefs|\w*RemoteConfig\w*)\b",
    "notification_manager": r"class\s+\w*Noti\w*Manager\b",
    "notification_receiver": r"class\s+\w*(?:Noti\w*|Alarm)Receiver\b",
    "boot_receiver": r"class\s+\w*BootReceiver\b",
    "lockscreen": r"class\s+LockScreen(?:NotiManager|NotiWatcher|Activity)\b",
    "navigation": r"(?:fun|class)\s+\w*(?:AppNavigation|RootNavigation|MainNavigation|NavGraph)\b",
    "language_manager": r"(?:object|class)\s+LanguageManager\b",
    "shortcuts": r"(?:object|class)\s+\w*Shortcut\w*(?:Manager|Util|s)\b",
    "fcm": r"class\s+\w+\s*:\s*FirebaseMessagingService\b",
}


def run(cmd, cwd):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def walk(repo, exts):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in files:
            if fn.endswith(exts):
                yield os.path.join(root, fn)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def first(rx, text, group=1):
    m = re.search(rx, text, re.M)
    return m.group(group) if m else None


def gradle_text(repo):
    parts = {}
    for name in ("settings.gradle.kts", "settings.gradle", "build.gradle.kts", "build.gradle",
                 "gradle.properties", "gradle/libs.versions.toml"):
        p = os.path.join(repo, name)
        if os.path.exists(p):
            parts[name] = read(p)
    for p in walk(repo, (".gradle", ".gradle.kts")):
        rel = os.path.relpath(p, repo)
        if rel.count(os.sep) <= 3:
            parts.setdefault(rel, read(p))
    return parts


def toml_lib_version(toml, coord, key="module"):
    m = re.search(r'=\s*\{[^}]*' + key + r'\s*=\s*"' + re.escape(coord) + r'"[^}]*\}', toml)
    if not m:
        return None
    entry = m.group(0)
    v = first(r'version\s*=\s*"([^"]+)"', entry)
    if v:
        return v
    ref = first(r'version\.ref\s*=\s*"([^"]+)"', entry)
    return first(r'^\s*' + re.escape(ref) + r'\s*=\s*"([^"]+)"', toml) if ref else None


def detect_modules(settings):
    mods = re.findall(r"""include\s*\(?\s*((?:["']:[^"']+["']\s*,?\s*)+)""", settings)
    out = []
    for group in mods:
        out += re.findall(r"""["'](:[^"']+)["']""", group)
    return sorted(set(out))


def app_code(repo):
    try:
        with open(os.path.join(SKILL_DIR, "apps.json")) as f:
            apps = json.load(f)["apps"]
    except OSError:
        apps = {}
    base = os.path.basename(os.path.abspath(repo))
    for code, info in apps.items():
        if info.get("dir") and info["dir"] == base:
            return code
    m = re.search(r"\ba[_-]?0?(\d{2,3})\b", base, re.I)
    return f"a{int(m.group(1)):03d}" if m else None


def verify_command(repo, code):
    for name in ("CLAUDE.md", ".claude/rules/CLAUDE.md"):
        text = read(os.path.join(repo, name))
        cmds = re.findall(r"(\./gradlew\s+:?[\w:-]*assemble[\w]*)", text)
        if cmds:
            return cmds[0], name
    projects = os.path.expanduser("~/.claude/night-dev/projects.yaml")
    text = read(projects)
    base = os.path.basename(os.path.abspath(repo))
    block = re.search(r"path:\s*" + re.escape(base) + r"\b(.*?)(?:\n\s*\"|\Z)", text, re.S)
    if block:
        v = first(r"verify:\s*(.+)", block.group(1))
        if v:
            return v.strip(), "night-dev/projects.yaml"
    return "./gradlew :app:assembleDebug", "mặc định"


def gradle_version(repo):
    text = read(os.path.join(repo, "gradle", "wrapper", "gradle-wrapper.properties"))
    m = re.search(r"gradle-(\d+)\.(\d+)(?:\.\d+)?-(?:bin|all)\.zip", text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def max_runtime_jdk(gv):
    if not gv:
        return 21
    if gv >= (9, 1):
        return 25
    if gv >= (8, 14):
        return 24
    if gv >= (8, 10):
        return 23
    if gv >= (8, 8):
        return 22
    return 21


def required_jdk(all_gradle):
    found = [17]
    for rx in (r"JavaVersion\.VERSION_(\d+)", r"jvmTarget\s*[=(]\s*\"?(?:JvmTarget\.JVM_)?(\d+)", r"jvmToolchain\((\d+)\)"):
        found += [int(x.replace("_", "")) for x in re.findall(rx, all_gradle) if x.replace("_", "").isdigit()]
    found = [v if v >= 8 else 8 for v in found]
    return max(v for v in found if v < 100)


def jdk_candidates():
    import glob
    roots = glob.glob("/Applications/Android Studio*.app/Contents/jbr/Contents/Home")
    roots += glob.glob(os.path.expanduser("~/Library/Java/JavaVirtualMachines/*/Contents/Home"))
    roots += glob.glob("/Library/Java/JavaVirtualMachines/*/Contents/Home")
    for d in glob.glob(os.path.expanduser("~/.gradle/jdks/*")):
        if os.path.isdir(d):
            for sub in [d, os.path.join(d, "Contents", "Home")] + glob.glob(os.path.join(d, "*", "Contents", "Home")):
                if os.path.exists(os.path.join(sub, "release")):
                    roots.append(sub)
                    break
    if os.environ.get("JAVA_HOME"):
        roots.append(os.environ["JAVA_HOME"])
    out = {}
    for r in roots:
        v = first(r'^JAVA_VERSION="?(\d+)', read(os.path.join(r, "release")))
        if v:
            out[r] = int(v)
    return out


def suggest_jdk(repo, all_gradle):
    gv = gradle_version(repo)
    need, cap = required_jdk(all_gradle), max_runtime_jdk(gv)
    ok = sorted(((v, p) for p, v in jdk_candidates().items() if need <= v <= cap), reverse=True)
    return {
        "gradle": ".".join(map(str, gv)) if gv else None,
        "jdk_need": f">= {need}, <= {cap} (Gradle {'.'.join(map(str, gv)) if gv else '?'})",
        "jdk_suggest": (f"export JAVA_HOME=\"{ok[0][1]}\"  # JDK {ok[0][0]}" if ok else
                        "không thấy JDK phù hợp trên máy — báo user"),
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    repo = os.path.abspath(args[0] if args else os.getcwd())
    g = gradle_text(repo)
    all_gradle = "\n".join(g.values())
    settings = g.get("settings.gradle.kts") or g.get("settings.gradle") or ""
    toml = g.get("gradle/libs.versions.toml", "")

    xtechads = (toml_lib_version(toml, "com.xtech.sdk:xtechads")
                or first(r'^\s*xtechads\s*=\s*"([^"]+)"', toml)
                or first(r"com\.xtech\.sdk:xtechads:([\w.\-]+)", all_gradle)
                or first(r"xtechads(?:Version|_version|\.version)\s*=\s*([\w.\-]+)", all_gradle))
    plugin = (toml_lib_version(toml, "com.xtech.ads", key="id")
              or first(r'id\s*\(?\s*"com\.xtech\.ads"\s*\)?\s*version\s*"([^"]+)"', all_gradle))
    extra_sdk = sorted(set(re.findall(r"com\.xtech\.sdk:(xtech\w+)", all_gradle + toml)))
    for lib in ("xtechads", "xtechbilling", "xtechupdate", "xtechcore"):
        v = toml_lib_version(toml, "com.xtech.sdk:" + lib) or first(r'^\s*' + lib + r'\s*=\s*"([^"]+)"', toml)
        if v and lib not in extra_sdk:
            extra_sdk.append(f"{lib}")

    src_files = list(walk(repo, SRC_EXT))
    compose_files = 0
    fragment_files = 0
    key_files = {k: [] for k in KEY_FILES}
    signals = {"koin": False, "hilt": False, "nav3": False, "nav2": False, "own_ads_layer": False,
               "adjust": False, "appsflyer": False}
    for p in src_files:
        text = read(p)
        rel = os.path.relpath(p, repo)
        if "@Composable" in text:
            compose_files += 1
        if re.search(r":\s*(?:\w+\.)*\w*Fragment\s*\(", text) or re.search(r"\bFragment\(\)", text):
            fragment_files += 1
        if "startKoin" in text or "org.koin" in text:
            signals["koin"] = True
        if "@HiltAndroidApp" in text or "dagger.hilt" in text:
            signals["hilt"] = True
        if "androidx.navigation3" in text or "NavDisplay(" in text:
            signals["nav3"] = True
        if "androidx.navigation.compose" in text or "NavHost(" in text or "findNavController" in text:
            signals["nav2"] = True
        if re.search(r"\bConfigKey[A-D]\b|class\s+ConsentHelper\b", text):
            signals["own_ads_layer"] = True
        if "com.adjust.sdk" in text:
            signals["adjust"] = True
        if "AppsFlyerLib" in text:
            signals["appsflyer"] = True
        for k, rx in KEY_FILES.items():
            if len(key_files[k]) < 6 and re.search(rx, text):
                key_files[k].append(rel)
    layouts = [p for p in walk(repo, (".xml",)) if os.sep + "layout" in p and os.sep + "res" + os.sep in p]
    screen_layouts = [p for p in layouts if re.search(r"(activity|fragment)_\w+\.xml$", p)]
    ads_config = [os.path.relpath(p, repo) for p in walk(repo, (".json",)) if os.path.basename(p) == "ads_config.json"]
    manifests = [os.path.relpath(p, repo) for p in walk(repo, (".xml",)) if os.path.basename(p) == "AndroidManifest.xml"
                 and os.sep + "src" + os.sep + "main" + os.sep in p]

    app_gradle = g.get("app/build.gradle.kts") or g.get("app/build.gradle") or all_gradle
    def sdk_level(name):
        return (first(name + r'\s*[=(]?\s*(\d+)', app_gradle)
                or first(name + r'\s*\{[^}]*?release\((\d+)\)', app_gradle)
                or first(r'^\s*' + name.replace("Sdk", "-sdk").lower() + r'\s*=\s*"(\d+)"', toml)
                or first(r'^\s*' + name + r'\s*=\s*"(\d+)"', toml))

    if compose_files and len(screen_layouts) > 10:
        ui = f"Mixed (Compose {compose_files} file + XML {len(screen_layouts)} màn)"
    elif compose_files:
        ui = "Compose"
    else:
        ui = f"XML/View ({len(screen_layouts)} layout màn)"
    nav = "Navigation3" if signals["nav3"] else ("Navigation2" if signals["nav2"] else
                                                   ("Fragment/Activity" if fragment_files else "?"))
    if signals["nav3"] and signals["nav2"]:
        nav = "Navigation3 + Navigation2"
    code = app_code(repo)
    verify, verify_src = verify_command(repo, code)
    result = {
        "repo": repo,
        "app_code": code,
        "application_id": first(r'applicationId\s*=?\s*"([^"]+)"', app_gradle),
        "namespace": first(r'namespace\s*=?\s*"([^"]+)"', app_gradle),
        "branch": run(["git", "branch", "--show-current"], repo)
                  or ("detached@" + run(["git", "rev-parse", "--short", "HEAD"], repo)),
        "dirty_files": len([l for l in run(["git", "status", "--porcelain"], repo).splitlines() if l.strip()]),
        "xtechads": xtechads or None,
        "xtechads_plugin": plugin or None,
        "xtech_modules": extra_sdk,
        "sdk_mode": ("xtechads" if xtechads else ("ads tự viết (không SDK)" if signals["own_ads_layer"] else "không rõ")),
        "ui": ui,
        "di": "Koin" if signals["koin"] else ("Hilt" if signals["hilt"] else "?"),
        "navigation": nav,
        "modules": detect_modules(settings),
        "min_sdk": sdk_level("minSdk"),
        "compile_sdk": sdk_level("compileSdk"),
        "target_sdk": sdk_level("targetSdk"),
        "agp": first(r'^\s*agp\s*=\s*"([^"]+)"', toml) or first(r"com\.android\.tools\.build:gradle:([\w.\-]+)", all_gradle),
        "kotlin": first(r'^\s*kotlin\s*=\s*"([^"]+)"', toml),
        "adjust": signals["adjust"],
        "appsflyer": signals["appsflyer"],
        "ads_config": ads_config,
        "manifests": manifests,
        "key_files": {k: v for k, v in key_files.items() if v},
        "has_claude_md": os.path.exists(os.path.join(repo, "CLAUDE.md")),
        "verify": verify,
        "verify_source": verify_src,
        **suggest_jdk(repo, all_gradle),
    }
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return
    for k, v in result.items():
        if isinstance(v, dict):
            print(f"{k}:")
            for kk, vv in v.items():
                print(f"  {kk}: {', '.join(vv)}")
        elif isinstance(v, list):
            print(f"{k}: {', '.join(v) if v else '-'}")
        else:
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
