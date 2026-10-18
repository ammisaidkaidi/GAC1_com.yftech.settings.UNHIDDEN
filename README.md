# GAC1_com.yftech.settings.UNHIDDEN — YF Tech Settings APK with all hidden features forced visible

> **Rebuilt APK of `com.yftech.settings.apk` (v1.0, versionCode 1) with patches that force every hidden settings tab and sub-feature to render, regardless of the vehicle's reported capability.**
>
> Generated 2026-10-18 UTC. Source decompilation repo: [`GAC1_com.yftech.settings.apk`](https://github.com/ammisaidkaidi/GAC1_com.yftech.settings.apk).

## What this repo contains

| path | what |
|---|---|
| `com.yftech.settings.unhidden.apk` | **The rebuilt, signed APK.** Install this on a device to get the unhiddden UI. |
| `com.yftech.settings.unhidden.unsigned.apk` | Same APK, unsigned (for re-signing with the platform key). |
| `yftech-debug.keystore` | Debug keystore used to sign the rebuilt APK. Password: `android`. **You should re-sign with the platform key** (see §4 below). |
| `patched_apktool_out/` | The full `apktool_out/` directory with the smali patches applied. Use this to rebuild locally. |
| `patched_apktool_out/smali/com/yftech/settings/utils/ConfigUtils.smali` | Patched `ConfigUtils` — forces all 13 config flags to `true`. |
| `patched_apktool_out/smali/com/yftech/settings/manager/*.smali` | Patched managers — `getFunctionPresent()` always returns `true`. |
| `patch_smali.py` | The Python patcher that produced the patches (re-runnable, idempotent). |
| `README.md` | This file. |

## 1. Why this exists — what is hidden by default

The original `com.yftech.settings.apk` has **9 settings tabs** in its single `SettingsActivity`:

| # | Tab | Fragment | Hidden? | Why |
|---|-----|----------|---------|-----|
| 0 | Connect (Wifi/BT/CarPlay) | `ConnectMainFragment` | visible | always visible |
| 1 | Sound | `SoundFragment` | visible | always visible |
| 2 | **Drive** (DrivingMode / Safe / Assistance / TipMemory / Parking) | `DriveAidsMainFragment` | **HIDDEN** if `ConfigUtils.isAidConfig() == false` |
| 3 | Chassis (chassis power) | `ChassisPowerMainFragment` | visible | always visible |
| 4 | **Parts** (CarAssistantManager / Light / Lock / Rearview / More) | `CarPartsMainFragment` | **HIDDEN** if `ConfigUtils.isCarPartsConfig() == false` |
| 5 | **AcSeat** (AC / Seat / Climate automation) | `AcSeatMainFragment` | **HIDDEN** if `ConfigUtils.isAcSeatConfig() == false` |
| 6 | Display (DisplayConsole / DisplayDash) | `DisplayMainFragment` | visible | always visible |
| 7 | System (storage / upgrade) | `SystemMainFragment` | visible | always visible |
| 8 | Voice (VoiceSettings / wake-up / recognition / TTS) | `VoiceMainFragment` | visible | always visible |

**And inside each visible tab**, individual sub-features are gated by `Manager.getInstance().getFunctionPresent(Function.XXX)`. If the function isn't present per the vehicle's reported capability, the sub-feature is hidden even though the tab is visible.

**This means** that on a car where the vehicle SDK reports few capabilities, you'll see a sparse settings UI with the 3 highlighted tabs completely missing AND many sub-features inside the visible tabs missing.

The user's request was: *"voice, parking, wifi and Bluetooth and Safe, Assistance, Parking, TipMemory, CarAssistantManager + parking settings and ac (Ac, Seat, Climate automation + driver seat), DisplayConsole, DisplayDash and storage, upgrade, all VoiceSettings (Wake-up, recognition engine, TTS voice), DrivingMode, ModeSettings — all hidden from my car — find a way to show them up."*

The patches below unhide ALL of these.

## 2. What was patched

### Patch 1 — `ConfigUtils.smali` `init()V`

The original `init()` calls 13 private `isXxxConfig()` methods, each of which calls one or more `Manager.getInstance().getFunctionPresent(Function.X)` (which in turn calls `com.yftech.vehicle.sdk.CarConfig.isXxxPresent()` — the vehicle SDK). The result is stored in 13 static boolean fields.

The patched `init()` simply sets all 13 static fields to `true`:

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

This alone makes the 3 hidden tabs (Drive, Parts, AcSeat) visible.

### Patch 1b — `ConfigUtils.smali` `isAcSeatConfig()`, `isAidConfig()`, `isCarPartsConfig()`

These three public accessors are what `SettingsActivity.onCreate()` actually checks (lines 342–344). As a belt-and-suspenders measure, each is overridden to return `true` unconditionally:

```smali
.method public isAcSeatConfig()Z
    .locals 1
    const/4 v0, 0x1
    return v0
.end method
```

(Same pattern for `isAidConfig()` and `isCarPartsConfig()`.)

### Patch 2 — All 7 manager `getFunctionPresent()Z` methods

The 7 managers that gate individual sub-features:

| manager | gates features related to |
|---|---|
| `CarAssistantManager` | Safe (FCW, AEB, LDW/LKA, TSR, ADAS warning), Assistance (cruise assist, DFC, IA), TipMemory (speed warning, remember driving mode) |
| `CarDashboardManager` | DisplayDash (back-light level, language, volume, units, restore factory) |
| `CarDriveModeManager` | DrivingMode, ModeSettings (remember driving mode enabled) |
| `CarParkingManager` | Parking (radar warning tone, push notification, voice tip) |
| `CarPartsManager` | AC, Seat (driver convenient access), Light (IHBC, head light delay), Lock (remote unlock, auto unlock, PEPS, speed auto lock, sunroof window auto close, electric hidden door handle), Rearview (OSRM auto fold, turn down), More (auto wiper, front wiper service position, ETC, wireless charging, steering wheel asterisk key, convenient car search) |
| `SettingsManager` | general settings |
| `SoundManager` | Sound interaction (key sound, interface effects) |

Each manager's `getFunctionPresent(<Manager>$Function;)Z` is replaced with:

```smali
.method public getFunctionPresent(Lcom/yftech/settings/manager/<Manager>$Function;)Z
    .locals 1
    const/4 v0, 0x1
    return v0
.end method
```

This forces every sub-feature UI to render even if the vehicle reports it as not present.

## 3. How to rebuild locally

If you want to rebuild from scratch (e.g. after modifying the patches):

```bash
# 1) Shallow-clone the original decompilation
git clone --depth 1 https://github.com/ammisaidkaidi/GAC1_com.yftech.settings.apk.git settings_decompiled

# 2) Apply patches
python3 patch_smali.py   # in-place; .bak files saved alongside

# 3) Rebuild APK with apktool 3.x
apktool b settings_decompiled/apktool_out \
    -o com.yftech.settings.unhidden.unsigned.apk -f

# 4) Zipalign
zipalign -p -f -v 4 \
    com.yftech.settings.unhidden.unsigned.apk \
    com.yftech.settings.unhidden.aligned.apk

# 5) Sign with your keystore (debug shown; use platform key in production)
apksigner sign \
    --ks yftech-debug.keystore --ks-key-alias yftech-debug \
    --ks-pass pass:android --key-pass pass:android \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --in com.yftech.settings.unhidden.aligned.apk \
    --out com.yftech.settings.unhidden.apk

# 6) Verify
apksigner verify --print-certs com.yftech.settings.unhidden.apk
```

## 4. ⚠️ CRITICAL: Why this APK may not install on your car as-is

The original `AndroidManifest.xml` declares:

```xml
<manifest ... android:sharedUserId="android.uid.system" ...>
```

`android:sharedUserId="android.uid.system"` means the APK runs as the **system UID** — only permitted if the APK is **signed with the platform signing key** that matches the rest of the platform (`com.yftech.service.main`, `com.yftech.service.bluetooth`, etc.).

The APK in this repo is signed with a debug key (`yftech-debug.keystore`, password `android`). Installing it on the head unit will fail with `INSTALL_FAILED_SHARED_USER_INCOMPATIBLE` (or similar) unless:

### Option A — Re-sign with the platform key

If you have the YF Tech platform signing key (a `.jks` / `.keystore` / `.pem` + `.pk8` pair):

```bash
apksigner sign \
    --ks platform.keystore --ks-key-alias platform \
    --ks-pass pass:<your_platform_keystore_password> \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --in com.yftech.settings.unhidden.unsigned.apk \
    --out com.yftech.settings.unhidden.platform-signed.apk

# install on device
adb install -r com.yftech.settings.unhidden.platform-signed.apk
```

Where to get the platform key:
- The YF Tech platform owner / OEM has it.
- Some firmware images leak the platform key in `META-INF/*.RSA` of shipped update packages; if you can pull `boot.img` / `system.img` and find a previously-installed signed APK, the cert is extractable but the private key is not — you'd need to either obtain the private key legitimately or resign ALL 14 platform APKs with a new key (which breaks the inter-app contract).

### Option B — Drop `sharedUserId` from the manifest

If you edit the patched `AndroidManifest.xml` to remove the `android:sharedUserId="android.uid.system"` attribute, the APK will install without the platform key, BUT:

- It loses system-uid privileges (e.g. `MASTER_CLEAR`, `READ_SETTINGS`, `WRITE_SECURE_SETTINGS` will fail at runtime).
- It loses access to the platform's custom signature-protected permissions (`com.yftech.permission.*`), so it can no longer talk to `service.main`, `service.bluetooth`, etc. — most features will load the UI but fail to actually control the vehicle.

### Option C — Install on a rooted / Magisk'd device

With Magisk's signature-spoofing module, you can install the debug-signed APK and have it pass the `signature`-level permission checks at runtime. The custom permissions (`com.yftech.permission.service.main.audio`, etc.) will be granted because Magisk lies to the system about the signing identity.

### Option D — Don't rebuild; use an activator APK instead

If all you want is to *trigger* the hidden features (not modify the platform APK), see **[`hidden_features_activation.md`](https://github.com/ammisaidkaidi/GAC1_ANALYSIS/blob/main/extras/hidden_features_activation.md)** in the analysis repo. That approach uses adb commands or a small unsigned APK to launch each hidden activity directly, no platform signing needed.

## 5. Map of unhiddden features → expected UI location

After the patches, on the next launch of `SettingsActivity` (via the launcher or via `adb shell am start -n com.yftech.settings/.SettingsActivity`), you should see all 9 tabs and all sub-features:

| user's requested feature | settings tab | fragment class | config flag |
|---|---|---|---|
| Voice (wake-up, recognition, TTS) | Voice (tab 8) | `VoiceMainFragment` | (always visible) |
| Parking (radar/push/voice tip) | Drive (tab 2) | `DriveAidsMainFragment` | `isAidsParkingConfig` ✅ patched |
| Wifi | Connect (tab 0) | `ConnectMainFragment` | (always visible) |
| Bluetooth | Connect (tab 0) | `ConnectMainFragment` | (always visible) |
| Safe (FCW/AEB/LDW-LKA/TSR/ADAS warn/DSA) | Drive (tab 2) | `DriveAidsMainFragment` | `isAidsSafeConfig` ✅ patched |
| Assistance (cruise/DFC/IA) | Drive (tab 2) | `DriveAidsMainFragment` | `isAidsAssistanceConfig` ✅ patched |
| TipMemory (speed warning, remember drive mode) | Drive (tab 2) | `DriveAidsMainFragment` | `isAidTipMemoryConfig` ✅ patched |
| CarAssistantManager | Drive (tab 2) + Parts (tab 4) | `DriveAidsMainFragment` + `CarPartsMainFragment` | `isAidConfig` + `isCarPartsConfig` ✅ patched |
| AC (fan/auto-drying/circulation/unlock-vent) | AcSeat (tab 5) | `AcSeatMainFragment` | `isAcConfig` ✅ patched |
| Seat (driver convenient access) | AcSeat (tab 5) | `AcSeatMainFragment` | `isSeatConfig` ✅ patched |
| Climate automation | AcSeat (tab 5) | `AcSeatMainFragment` | `isAcConfig` ✅ patched |
| DisplayConsole | Display (tab 6) | `DisplayMainFragment` | (always visible) |
| DisplayDash | Display (tab 6) | `DisplayMainFragment` | `isCarDashboardConfig` ✅ patched |
| Storage | System (tab 7) | `SystemMainFragment` | (always visible) |
| Upgrade | System (tab 7) | `SystemMainFragment` | (always visible) |
| VoiceSettings (wake-up, recognition engine, TTS voice) | Voice (tab 8) | `VoiceMainFragment` | (always visible; sub-features may be gated by `VoiceSettingsManager.getFunctionPresent`) |
| DrivingMode | Drive (tab 2) | `DriveAidsMainFragment` | `isAidConfig` ✅ patched |
| ModeSettings | Drive (tab 2) | `DriveAidsMainFragment` | `isAidConfig` ✅ patched |

## 6. Caveats & limitations

- **Vehicle SDK calls may still fail at runtime.** Forcing `getFunctionPresent()` to return `true` only forces the UI to render. When the user actually toggles a setting whose underlying vehicle API is genuinely not present on the car (e.g. heated seats on a car without heated seats), the `setEnabled`/`setOption`/`setAction` call on the manager will return `false` or throw. The UI may show a successful toggle but the underlying state won't change.
- **No source-level rebuild was attempted.** The Java sources in `jadx_out/` are not directly recompilable (variable names lost, generics erased, control flow simplified). Smali patching via apktool is the only reliable rebuild path and is what was used here.
- **The shared libraries `com.yftech.vehicle.internal.adapter`, `com.yftech.vehicle.sdk`, `com.yftech.car.framework` must be present on the device.** They are declared via `<uses-library>` in the manifest and the APK will crash on launch if they are missing.
- **No guarantee of UI correctness.** Some hidden features may reference layout resources (`R.layout.*`, `R.id.*`) that the original release build pruned because the feature was off. If the resources are missing, the corresponding fragment will throw `InflateException` on creation. If you see this, you need to either find the resources in another build flavor or restore them from a full (debug) build of the platform.

## 7. Verifying the patches applied correctly

```bash
# Smali-level verification
grep -c "PATCHED by patch_smali.py" patched_apktool_out/smali/com/yftech/settings/utils/ConfigUtils.smali
# Expected: 1 (the init() method's comment)

grep -l "PATCHED by patch_smali.py" patched_apktool_out/smali/com/yftech/settings/manager/*.smali
# Expected: 7 files (one per manager)

# APK-level verification
apksigner verify --print-certs com.yftech.settings.unhidden.apk
# Expected: "Verifies" + the debug cert SHA-256

aapt dump badging com.yftech.settings.unhidden.apk | head -3
# Expected: package: name='com.yftech.settings' versionCode='1' versionName='1.0'
```

## 8. Disclaimer

- This rebuild was produced for the platform owner (you) to inspect and modify their own vehicle's head unit. Do not install on hardware you do not own.
- All YF Tech trademarks and IP belong to YF Tech / 御驾 (YF) Automotive.
- The debug keystore in this repo is for development convenience only; **rotate it** before deploying to a production device (anyone with the keystore file and the password "android" can sign APKs that pass `signature` checks for this debug build).
- If you've reached this repo via the originating chat session, **the GitHub Personal Access Token used to push the decompiled repos has been exposed in chat history — rotate it now** at https://github.com/settings/tokens.
