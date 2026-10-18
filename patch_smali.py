#!/usr/bin/env python3
"""patch_smali.py — patch settings APK smali to unhide all features.

Two classes of patches:

1. ConfigUtils.smali — patch `init()V` to set all 13 config flags to `true`
   unconditionally (instead of calling the underlying vehicle SDK checks).
   This makes the 3 hidden tabs visible:
     - Drive tab (DriveAidsMainFragment — DrivingMode/Safe/Assistance/TipMemory/Parking)
     - Parts tab (CarPartsMainFragment — Light/Lock/Rearview/More)
     - AcSeat tab (AcSeatMainFragment — AC/Seat/Climate)

2. All managers that have `public getFunctionPresent(...)Function;)Z` — replace
   the method body with `return true`. This forces every individual sub-feature
   inside the visible tabs to render (instead of being gated on the vehicle's
   reported capability via com.yftech.vehicle.sdk.CarConfig.isXxxPresent()).

Input:  /home/z/my-project/rebuild_settings/settings_decompiled/apktool_out/smali/com/yftech/settings/
Output: patched in place (backups saved as .bak)
"""
import re
from pathlib import Path

SMALI_ROOT = Path("/home/z/my-project/rebuild_settings/settings_decompiled/apktool_out/smali/com/yftech/settings")
CONFIG_UTILS = SMALI_ROOT / "utils" / "ConfigUtils.smali"
MANAGER_DIR = SMALI_ROOT / "manager"

def backup(path):
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        bak.write_bytes(path.read_bytes())

# ---------- Patch 1: ConfigUtils.smali ----------
def patch_config_utils():
    p = CONFIG_UTILS
    backup(p)
    text = p.read_text(encoding="utf-8")

    # Replace the init()V method body — everything between `.method public init()V`
    # and the matching `.end method`.
    new_init = '''.method public init()V
    .locals 1

    # PATCHED by patch_smali.py — force all config flags to true.
    # Original code called CarPartsManager/CarAssistantManager/etc. and stored
    # the result; we set them all to true so every tab is visible regardless
    # of the vehicle's reported capability.

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
.end method'''

    # Regex: match `.method public init()V` ... `.end method`
    pattern = re.compile(r'\.method public init\(\)V.*?^\.end method', re.DOTALL | re.MULTILINE)
    new_text, n = pattern.subn(new_init, text)
    assert n == 1, f"expected 1 init()V replacement, got {n}"

    # Also: harden the 3 public accessors to always return true (belt + suspenders).
    # Even if some other code path bypasses init() or the static fields get reset,
    # these three public methods are what SettingsActivity actually calls.
    def replace_method(name, body):
        nonlocal new_text
        pat = re.compile(rf'\.method public {re.escape(name)}\(\)Z.*?^\.end method', re.DOTALL | re.MULTILINE)
        new_text, n2 = pat.subn(body, new_text)
        return n2
    n_ac = replace_method("isAcSeatConfig", f'''.method public isAcSeatConfig()Z
    .locals 1
    # PATCHED — always true
    const/4 v0, 0x1
    return v0
.end method''')
    n_aid = replace_method("isAidConfig", f'''.method public isAidConfig()Z
    .locals 1
    # PATCHED — always true
    const/4 v0, 0x1
    return v0
.end method''')
    n_parts = replace_method("isCarPartsConfig", f'''.method public isCarPartsConfig()Z
    .locals 1
    # PATCHED — always true
    const/4 v0, 0x1
    return v0
.end method''')

    p.write_text(new_text, encoding="utf-8")
    print(f"[patch] ConfigUtils.smali: init()=patched, isAcSeatConfig={n_ac}, isAidConfig={n_aid}, isCarPartsConfig={n_parts}")

# ---------- Patch 2: managers' getFunctionPresent ----------
def patch_managers():
    # For each manager smali file, replace `method public getFunctionPresent(...)` body with return-true
    managers = [
        "CarAssistantManager",
        "CarDashboardManager",
        "CarDriveModeManager",
        "CarParkingManager",
        "CarPartsManager",
        "SettingsManager",
        "SoundManager",
    ]
    for m in managers:
        p = MANAGER_DIR / f"{m}.smali"
        if not p.exists():
            print(f"[patch] {m}.smali: not found, skipping")
            continue
        backup(p)
        text = p.read_text(encoding="utf-8")
        # The method signature is `method public getFunctionPresent(Lcom/yftech/settings/manager/<Manager>$Function;)Z`
        pat = re.compile(
            r'\.method public getFunctionPresent\(Lcom/yftech/settings/manager/' + re.escape(m) + r'\$Function;\)Z.*?^\.end method',
            re.DOTALL | re.MULTILINE
        )
        new_body = f'''.method public getFunctionPresent(Lcom/yftech/settings/manager/{m}$Function;)Z
    .locals 1
    # PATCHED by patch_smali.py — always return true.
    # Original called CarConfig.isXxxPresent() in the vehicle SDK; we bypass
    # this so every sub-feature UI is shown regardless of the vehicle's reported
    # capability. Note: if the feature is genuinely not present on the car,
    # the underlying API call (when the user actually toggles the setting) may
    # fail; this patch only forces UI visibility.
    const/4 v0, 0x1
    return v0
.end method'''
        new_text, n = pat.subn(new_body, text)
        if n == 1:
            p.write_text(new_text, encoding="utf-8")
            print(f"[patch] {m}.smali: getFunctionPresent replaced (1 method)")
        else:
            print(f"[patch] {m}.smali: WARNING expected 1 method, got {n}")

# ---------- Run ----------
if __name__ == "__main__":
    print("=== Patching ConfigUtils.smali ===")
    patch_config_utils()
    print()
    print("=== Patching manager smali files ===")
    patch_managers()
    print()
    print("=== Done ===")
