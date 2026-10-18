# GAC1_com.yftech.settings.UNHIDDEN — YF Tech Settings APK with all hidden features forced visible (v2: separate package)

> **Rebuilt APK of `com.yftech.settings.apk` (v1.0, versionCode 1) with patches that force every hidden settings tab and sub-feature to render, AND repackaged under a new application ID (`com.yftech.settings.unhidden`) so it installs alongside the original platform-signed app — no signature conflict.**

## Two APK versions in this repo

| File | Package ID | Signed with | When to use |
|---|---|---|---|
| **`com.yftech.settings.unhidden_v2.apk`** ⭐ | `com.yftech.settings.unhidden` | debug keystore | **Install this** if the original `com.yftech.settings` is already on the device and you got `INSTALL_FAILED_UPDATE_INCOMPATIBLE`. This APK installs as a SEPARATE app, coexists with the original. |
| `com.yftech.settings.unhidden.apk` (v1) | `com.yftech.settings` (same as original) | debug keystore | Use ONLY if you have the YF Tech platform key to re-sign it (drops in as an in-place update of the original). |

## Why v2 exists

Installing v1 on a device that already has the original `com.yftech.settings` (platform-signed) fails with:

```
adb: failed to install s.apk: Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE:
Package com.yftech.settings signatures do not match previously installed version; ignoring!]
```

Android refuses to update a package with a different signing key. v2 solves this by:

1. **Renaming the package** from `com.yftech.settings` → `com.yftech.settings.unhidden` in the AndroidManifest. This makes Android treat it as a *new* app, not an update of the existing one. The original keeps running untouched; v2 installs alongside it.
2. **Removing `android:sharedUserId="android.uid.system"`** from the manifest. This attribute requires the APK to be signed with the platform key; without it, the renamed APK can be installed with any signing key (debug, release, your custom).

## Trade-offs from removing `sharedUserId`

The original app runs as the **system UID** (uid 1000) — that's how it gets `MASTER_CLEAR`, `READ_SETTINGS`, `WRITE_SECURE_SETTINGS`, etc. without runtime prompts, and how it can call into the platform's signature-protected custom permissions (`com.yftech.permission.service.main.audio`, `com.yftech.permission.service.bluetooth`, etc.).

The v2 APK runs as a normal app UID. Consequences:

| Capability | Original (system uid) | v2 (normal uid) |
|---|---|---|
| Launcher icon visible | ✅ | ✅ (new icon next to original) |
| All 9 settings tabs render | ✅ | ✅ (patches force this) |
| All sub-feature UIs render | ✅ | ✅ (patches force this) |
| `<uses-library>` shared libs load | ✅ | ✅ (works regardless of uid) |
| Read/modify vehicle state via `com.yftech.vehicle.sdk` | ✅ | ⚠️ depends — system-only APIs will throw `SecurityException` |
| `<uses-permission>` platform custom permissions granted | ✅ (auto, sig-protected) | ❌ silently denied |
| Android system perms (`MASTER_CLEAR`, `WRITE_SECURE_SETTINGS`, ...) | ✅ granted at install | ❌ not granted (signature\|privileged level) |
| App actually toggles the underlying vehicle feature | ✅ | ⚠️ best-effort — UI is correct, but the call to set the value may fail |

**Net effect**: with v2, you get to **see and explore every hidden settings tab and sub-feature**. If a sub-feature's underlying API requires a system-level permission that v2 doesn't have, the UI toggle may appear to do nothing (or may pop a "Permission denied" toast). That's the cost of not having the platform signing key.

For full functionality on the device, you have three further options documented below in §4.

## What was patched (v2 == v1 patches + manifest rename)

### Patch 1 — `ConfigUtils.smali` `init()V`

Replaces the body of `init()` to set all 13 static config flags to `true`:

```smali
.method public init()V
    .locals 1
    const/4 v0, 0x1
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isSoundInteractionConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isLinkConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isAidTipMemoryConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isAidsSafeConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isAidsAssistanceConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isAidsParkingConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isCarPartsLightConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isCarPartsRearviewConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isCarPartsLockConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isCarPartsMoreConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isAcConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isSeatConfig:Z
    sput-boolean v0, Lcom/yftech/settings/utils/ConfigUtils;->isCarDashboardConfig:Z
    return-void
.end method
```

### Patch 1b — `ConfigUtils.smali` `isAcSeatConfig()` / `isAidConfig()` / `isCarPartsConfig()`

Each replaced with `const/4 v0, 0x1; return v0`.

### Patch 2 — All 7 managers' `getFunctionPresent()` methods

Replaced with `const/4 v0, 0x1; return v0` for:

- `CarAssistantManager` (Safe / Assistance / TipMemory)
- `CarDashboardManager` (DisplayDash)
- `CarDriveModeManager` (DrivingMode / ModeSettings)
- `CarParkingManager` (Parking)
- `CarPartsManager` (AC / Seat / Light / Lock / Rearview / More)
- `SettingsManager` (general)
- `SoundManager` (Sound interaction)

### Patch 3 (v2-only) — AndroidManifest.xml

```diff
- <manifest ... android:sharedUserId="android.uid.system"
-           package="com.yftech.settings" ...>
+ <manifest ...
+           package="com.yftech.settings.unhidden" ...>
```

## Install v2

```bash
# from your PC with adb
adb install -r com.yftech.settings.unhidden_v2.apk

# expected output:
# Success

# verify both apps coexist
adb shell pm list packages | grep yftech
# expected: com.yftech.settings AND com.yftech.settings.unhidden
```

After install, your launcher will show **two** settings icons:
- The original "Settings" (platform-signed) — same as before.
- A second "Settings" (this v2 APK) — opens with all hidden tabs + sub-features visible.

## Unhiddden features → UI mapping (recap)

| user's requested feature | settings tab | fragment class | config flag patched |
|---|---|---|---|
| Voice (wake-up, recognition, TTS) | Voice (tab 8) | `VoiceMainFragment` | (always visible) |
| Parking | Drive (tab 2) | `DriveAidsMainFragment` | `isAidsParkingConfig` ✅ |
| Wifi | Connect (tab 0) | `ConnectMainFragment` | (always visible) |
| Bluetooth | Connect (tab 0) | `ConnectMainFragment` | (always visible) |
| Safe (FCW/AEB/LDW-LKA/TSR/ADAS/DSA) | Drive (tab 2) | `DriveAidsMainFragment` | `isAidsSafeConfig` ✅ |
| Assistance (cruise/DFC/IA) | Drive (tab 2) | `DriveAidsMainFragment` | `isAidsAssistanceConfig` ✅ |
| TipMemory (speed warning, remember drive mode) | Drive (tab 2) | `DriveAidsMainFragment` | `isAidTipMemoryConfig` ✅ |
| CarAssistantManager | Drive (tab 2) + Parts (tab 4) | `DriveAidsMainFragment` + `CarPartsMainFragment` | ✅ |
| AC (fan/auto-drying/circulation/unlock-vent) | AcSeat (tab 5) | `AcSeatMainFragment` | `isAcConfig` ✅ |
| Seat (driver convenient access) | AcSeat (tab 5) | `AcSeatMainFragment` | `isSeatConfig` ✅ |
| Climate automation | AcSeat (tab 5) | `AcSeatMainFragment` | `isAcConfig` ✅ |
| DisplayConsole | Display (tab 6) | `DisplayMainFragment` | (always visible) |
| DisplayDash | Display (tab 6) | `DisplayMainFragment` | `isCarDashboardConfig` ✅ |
| Storage | System (tab 7) | `SystemMainFragment` | (always visible) |
| Upgrade | System (tab 7) | `SystemMainFragment` | (always visible) |
| VoiceSettings (wake-up, recognition, TTS voice) | Voice (tab 8) | `VoiceMainFragment` | (always visible; sub-features patched via `SoundManager`) |
| DrivingMode | Drive (tab 2) | `DriveAidsMainFragment` | `isAidConfig` ✅ |
| ModeSettings | Drive (tab 2) | `DriveAidsMainFragment` | `isAidConfig` ✅ |

## Going further — getting full functionality

If the v2 APK loads the UI but the underlying vehicle commands don't take effect (because of the missing signature-protected permissions), here are your paths to full functionality:

### Path A — Frida runtime hooks (no rebuild needed, recommended)

Install Frida server on the device, then hook the permission check to always return `GRANTED`:

```javascript
Java.perform(function() {
    var Context = Java.use('android.app.ContextImpl');
    Context.checkSelfPermission.implementation = function(p) {
        console.log('perm check bypassed: ' + p);
        return 0;  // PERMISSION_GRANTED
    };
    Context.checkPermission.implementation = function(p, pid, uid) {
        return 0;
    };
});
```

```bash
# push frida-server to the device, then:
frida -U -n com.yftech.settings.unhidden -l bypass.js
```

### Path B — Magisk signature-spoofing module (one-time setup)

Install Magisk + a signature-spoofing module (e.g. "SmaliPatcher" or "Hide My Applist"). Configure it to spoof the v2 APK's signing identity as the platform key. Then the system grants signature-protected permissions at install time.

### Path C — Platform-key re-sign of v1

If you have the YF Tech platform private key:

```bash
apksigner sign \
    --ks platform.keystore --ks-key-alias platform \
    --ks-pass pass:<your_platform_keystore_password> \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --in com.yftech.settings.unhidden.unsigned.apk \
    --out com.yftech.settings.unhidden.platform-signed.apk

# uninstall v1 (original) first, then install platform-signed v1
adb uninstall com.yftech.settings
adb install -r com.yftech.settings.unhidden.platform-signed.apk
```

This keeps the original package name AND grants system uid + signature-protected permissions. **The best path if you have the platform key.**

### Path D — Engineering mode entry

Many YF Tech platforms have an engineering-mode entry that itself has the platform signing. Triggering it (`adb shell am start -n com.yftech.engineeringmode/.MainActivity`) lets you reach the privileged subsystems without modifying any APK. See [`GAC1_ANALYSIS/extras/hidden_features_activation.md`](https://github.com/ammisaidkaidi/GAC1_ANALYSIS/blob/main/extras/hidden_features_activation.md).

## Build v2 from scratch

```bash
# 1) clone the decompilation
git clone --depth 1 https://github.com/ammisaidkaidi/GAC1_com.yftech.settings.apk.git settings_decompiled

# 2) apply patches (ConfigUtils + 7 managers)
python3 patch_smali.py   # in-place patches the smali

# 3) rename package + drop sharedUserId
python3 -c '
import re
p = "settings_decompiled/apktool_out/AndroidManifest.xml"
t = open(p).read()
t = t.replace("package=\"com.yftech.settings\" ", "package=\"com.yftech.settings.unhidden\" ")
t = t.replace(" android:sharedUserId=\"android.uid.system\"", "")
open(p, "w").write(t)
'

# 4) rebuild
apktool b settings_decompiled/apktool_out -o com.yftech.settings.unhidden_v2.unsigned.apk -f

# 5) zipalign + sign
zipalign -p -f -v 4 com.yftech.settings.unhidden_v2.unsigned.apk com.yftech.settings.unhidden_v2.aligned.apk
apksigner sign \
    --ks yftech-debug.keystore --ks-key-alias yftech-debug \
    --ks-pass pass:android --key-pass pass:android \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --in com.yftech.settings.unhidden_v2.aligned.apk \
    --out com.yftech.settings.unhidden_v2.apk
```

## Files in this repo

| path | what |
|---|---|
| `com.yftech.settings.unhidden_v2.apk` | **v2 — install this.** Package `com.yftech.settings.unhidden`, debug-signed, no `sharedUserId`. |
| `com.yftech.settings.unhidden_v2.unsigned.apk` | v2 unsigned (for re-signing with platform key). |
| `com.yftech.settings.unhidden.apk` | v1 (same package as original, debug-signed, has `sharedUserId`). For platform-key re-signing only. |
| `com.yftech.settings.unhidden.unsigned.apk` | v1 unsigned. |
| `yftech-debug.keystore` | Debug keystore. Password: `android`. Rotate before production. |
| `patch_smali.py` | Re-runnable patcher (patches ConfigUtils + 7 managers). |
| `patched_smali/` | The 8 patched `.smali` files as drop-in replacements. |
| `patched_manifest/AndroidManifest.xml` | The v2 patched manifest (package renamed + sharedUserId removed). |
| `README.md` | This file. |

## Disclaimer

- This rebuild was produced for the platform owner (you) to inspect and modify their own vehicle's head unit. Do not install on hardware you do not own.
- All YF Tech trademarks and IP belong to YF Tech / 御驾 (YF) Automotive.
- The debug keystore in this repo is for development convenience only; **rotate it** before deploying to a production device.
- If you reached this repo via the originating chat session, **the GitHub Personal Access Token used to push these repos has been exposed in chat history — rotate it now** at https://github.com/settings/tokens.
