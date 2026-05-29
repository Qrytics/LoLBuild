"""
K'Sante Build Advisor
=====================
Reads the current League of Legends live game via the Riot Live Client Data API
(https://127.0.0.1:2999) and recommends the best items to build for K'Sante
based on enemy and allied champion composition.

Usage:
    python ksante_build.py

The script must be run while a League of Legends game is in progress.
"""

import json
import sys
import urllib.request
import ssl


# ---------------------------------------------------------------------------
# Live Client Data API helpers
# ---------------------------------------------------------------------------

LIVE_API_BASE = "https://127.0.0.1:2999/liveclientdata"

# The local API uses a self-signed certificate; we skip verification.
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


def _get(path: str) -> dict | list:
    url = LIVE_API_BASE + path
    try:
        with urllib.request.urlopen(url, context=_SSL_CTX, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        print(f"[ERROR] Could not reach the Live Client Data API at {url}.")
        print(f"        Make sure League of Legends is running and in-game.")
        print(f"        Detail: {exc}")
        sys.exit(1)


def fetch_game_data() -> dict:
    return _get("/allgamedata")


# ---------------------------------------------------------------------------
# Champion knowledge base
# ---------------------------------------------------------------------------

# Champions whose primary damage type is AP (magic).
AP_CHAMPIONS: set[str] = {
    "ahri", "akali", "amumu", "anivia", "annie", "aurelionsol", "aurora", "azir", "bard",
    "brand", "cassiopeia", "chogath", "corki", "diana", "ekko", "elise",
    "evelynn", "ezreal", "fiddlesticks", "fizz", "galio", "gangplank",
    "gragas", "heimerdinger", "hwei", "illaoi", "ivern", "janna",
    "jarvaniv", "jayce", "karma", "karthus", "kassadin", "katarina",
    "kayle", "kennen", "khazix", "kogmaw", "leblanc", "lissandra",
    "lillia", "lulu", "lux", "malphite", "malzahar", "maokai", "masteryi",
    "mordekaiser", "morgana", "nami", "nasus", "nautilus", "neeko",
    "nidalee", "nunu", "orianna", "pantheon", "poppy", "pyke", "qiyana",
    "quinn", "rumble", "ryze", "seraphine", "sett", "shyvana", "singed",
    "skarner", "sona", "soraka", "swain", "sylas", "syndra", "taric",
    "teemo", "thresh", "tristana", "twisted fate", "twitch", "urgot",
    "veigar", "velkoz", "vex", "viktor", "vladamir", "vlad", "vladimir",
    "xerath", "yasuo", "yone", "yuumi", "zac", "zed", "ziggs", "zilean",
    "zoe", "zyra",
}

# Ranged champions (auto-attack range > 350).
RANGED_CHAMPIONS: set[str] = {
    "ahri", "akshan", "anivia", "annie", "aphelios", "ashe",
    "aurelionsol", "aurora", "azir", "bard", "brand", "caitlyn", "cassiopeia",
    "corki", "draven", "elise", "ezreal", "fiddlesticks", "gangplank",
    "graves", "heimerdinger", "hwei", "jayce", "jhin", "jinx", "karma",
    "karthus", "kayle", "kennen", "khazix", "kogmaw", "leblanc",
    "lissandra", "lucian", "lulu", "lux", "malzahar", "miss fortune",
    "missfortune", "morgana", "nami", "neeko", "nidalee", "orianna",
    "quinn", "rumble", "ryze", "seraphine", "senna", "sion", "sivir",
    "smolder",
    "sona", "soraka", "swain", "syndra", "teemo", "thresh", "tristana",
    "twisted fate", "twistedfate", "twitch", "urgot", "varus", "veigar",
    "velkoz", "vex", "viktor", "xayah", "xerath", "yuumi",
    "ziggs", "zilean", "zoe", "zyra",
}

# Champions that build critical strike (marksmen + some fighters).
CRIT_CHAMPIONS: set[str] = {
    "aphelios", "ashe", "caitlyn", "corki", "draven", "ezreal", "graves",
    "jhin", "jinx", "kayle", "khazix", "kogmaw", "lucian", "masteryi",
    "miss fortune", "missfortune", "nilah", "quinn", "samira", "senna", "sivir", "smolder",
    "tristana", "tryndamere", "twitch", "urgot", "varus", "xayah",
    "yasuo", "yone", "zeri",
}

# Champions with significant damage-over-time / burn effects.
DOT_CHAMPIONS: set[str] = {
    "brand", "cassiopeia", "karthus", "lillia", "malzahar", "singed", "teemo",
    "mordekaiser", "swain", "zyra",
}

# AP champions with high burst windows (combo/one-shot patterns).
BURST_AP_CHAMPIONS: set[str] = {
    "ahri", "akali", "annie", "aurora", "diana", "ekko", "evelynn", "fizz",
    "kassadin", "katarina", "leblanc", "lissandra", "lux", "neeko", "orianna",
    "syndra", "veigar", "vex", "zoe",
}

# AP champions that deal primarily sustained DPS over time.
SUSTAINED_AP_CHAMPIONS: set[str] = {
    "anivia", "aurelionsol", "azir", "brand", "cassiopeia", "heimerdinger", "hwei",
    "karthus", "kayle", "lillia", "malzahar", "mordekaiser", "rumble", "ryze",
    "singed", "swain", "teemo", "viktor", "vladimir", "xerath", "ziggs", "zyra",
}

# AP assassins / diver-like AP burst threats.
AP_ASSASSIN_CHAMPIONS: set[str] = {
    "akali", "diana", "ekko", "evelynn", "fizz", "kassadin", "katarina", "leblanc",
}

# AD assassins with high backline burst.
AD_ASSASSIN_CHAMPIONS: set[str] = {
    "kayn", "khazix", "naafiri", "qiyana", "rengar", "talon", "zed",
}

# Typical top-lane champion pool used for lane-opponent fallback detection.
TOP_LANE_CHAMPIONS: set[str] = {
    "aatrox", "akali", "akshan", "camille", "chogath", "darius", "drmundo", "fiora",
    "gangplank", "garen", "gnar", "gragas", "gwen", "heimerdinger", "illaoi", "irelia",
    "jax", "jayce", "kennen", "kled", "malphite", "maokai", "mordekaiser", "nasus",
    "olaf", "ornn", "pantheon", "poppy", "quinn", "renekton", "rengar", "riven",
    "rumble", "sett", "shen", "singed", "sion", "teemo", "trundle", "tryndamere",
    "urgot", "vayne", "volibear", "warwick", "wukong", "yasuo", "yorick", "zac",
}

# Champions whose kit has notable anti-heal (grievous wounds application).
ANTI_HEAL_CHAMPIONS: set[str] = {
    "katarina", "kled", "mordekaiser", "varus", "braum", "miss fortune",
    "missfortune", "fizz", "singed",
}

# Champions with notable true damage (armor shred / true DMG threats).
TRUE_DAMAGE_CHAMPIONS: set[str] = {
    "camille", "cho'gath", "chogath", "darius", "fiora", "garen", "gwen",
    "illaoi", "irelia", "jax", "olaf", "vayne",
}

# Champions with significant armor shred in their kit.
ARMOR_SHRED_CHAMPIONS: set[str] = {
    "black cleaver users",  # placeholder category, checked by item
    "corki", "jayce", "kayle", "lucian", "nasus", "renekton", "talon",
    "vi", "warwick", "yorick",
}

# Heavy auto-attack reliant champions (benefit most from Frozen Heart / Randuin's).
AA_CHAMPIONS: set[str] = {
    "aphelios", "ashe", "bel'veth", "belveth", "briar", "caitlyn", "corki",
    "draven", "ezreal", "graves", "irelia", "jax", "jhin", "jinx", "kayle", "kogmaw", "lucian",
    "masteryi", "miss fortune", "missfortune", "quinn", "samira", "senna",
    "sivir", "smolder", "tristana", "tryndamere", "twitch", "urgot", "varus",
    "vayne", "warwick", "xayah", "yasuo", "yone", "zeri",
}

# Known carry roles (ADC / fed assassin / fed mage) – if YOUR TEAM has one.
CARRY_CHAMPION_ROLES: set[str] = {
    "aphelios", "ashe", "caitlyn", "corki", "draven", "ezreal", "graves",
    "jhin", "jinx", "kayle", "kogmaw", "lucian", "miss fortune",
    "missfortune", "nilah", "quinn", "samira", "senna", "sivir", "smolder", "tristana",
    "twitch", "urgot", "varus", "xayah", "yasuo", "yone", "zeri",
    "akali", "diana", "ekko", "irelia", "katarina", "khazix", "leblanc",
    "masteryi", "nidalee", "talon", "zed",
}


def _normalize(name: str) -> str:
    """Lowercase and strip spaces/apostrophes for champion-name comparison."""
    return name.lower().replace("'", "").replace(" ", "").replace(".", "")


def _normalized_set(champions: set[str]) -> set[str]:
    return {_normalize(champion) for champion in champions}


AP_CHAMPIONS_NORM = _normalized_set(AP_CHAMPIONS)
RANGED_CHAMPIONS_NORM = _normalized_set(RANGED_CHAMPIONS)
CRIT_CHAMPIONS_NORM = _normalized_set(CRIT_CHAMPIONS)
DOT_CHAMPIONS_NORM = _normalized_set(DOT_CHAMPIONS)
BURST_AP_CHAMPIONS_NORM = _normalized_set(BURST_AP_CHAMPIONS)
SUSTAINED_AP_CHAMPIONS_NORM = _normalized_set(SUSTAINED_AP_CHAMPIONS)
AA_CHAMPIONS_NORM = _normalized_set(AA_CHAMPIONS)
ANTI_HEAL_CHAMPIONS_NORM = _normalized_set(ANTI_HEAL_CHAMPIONS)
TRUE_DAMAGE_CHAMPIONS_NORM = _normalized_set(TRUE_DAMAGE_CHAMPIONS)
CARRY_CHAMPION_ROLES_NORM = _normalized_set(CARRY_CHAMPION_ROLES)
AP_ASSASSIN_CHAMPIONS_NORM = _normalized_set(AP_ASSASSIN_CHAMPIONS)
AD_ASSASSIN_CHAMPIONS_NORM = _normalized_set(AD_ASSASSIN_CHAMPIONS)
TOP_LANE_CHAMPIONS_NORM = _normalized_set(TOP_LANE_CHAMPIONS)

TOP_POSITION_TAGS = {"top", "toplane", "top_lane"}


def is_ap(champ: str) -> bool:
    return _normalize(champ) in AP_CHAMPIONS_NORM


def is_ranged(champ: str) -> bool:
    return _normalize(champ) in RANGED_CHAMPIONS_NORM


def is_crit(champ: str) -> bool:
    return _normalize(champ) in CRIT_CHAMPIONS_NORM


def is_dot(champ: str) -> bool:
    return _normalize(champ) in DOT_CHAMPIONS_NORM


def is_burst_ap(champ: str) -> bool:
    return _normalize(champ) in BURST_AP_CHAMPIONS_NORM


def is_sustained_ap(champ: str) -> bool:
    return _normalize(champ) in SUSTAINED_AP_CHAMPIONS_NORM


def is_aa_heavy(champ: str) -> bool:
    return _normalize(champ) in AA_CHAMPIONS_NORM


def is_anti_heal(champ: str) -> bool:
    return _normalize(champ) in ANTI_HEAL_CHAMPIONS_NORM


def is_true_damage(champ: str) -> bool:
    return _normalize(champ) in TRUE_DAMAGE_CHAMPIONS_NORM


def is_ap_assassin(champ: str) -> bool:
    return _normalize(champ) in AP_ASSASSIN_CHAMPIONS_NORM


def is_ad_assassin(champ: str) -> bool:
    return _normalize(champ) in AD_ASSASSIN_CHAMPIONS_NORM


def is_carry(champ: str) -> bool:
    return _normalize(champ) in CARRY_CHAMPION_ROLES_NORM


def is_top_laner(champ: str) -> bool:
    return _normalize(champ) in TOP_LANE_CHAMPIONS_NORM


# ---------------------------------------------------------------------------
# Item recommendation engine
# ---------------------------------------------------------------------------

def analyze_composition(
    enemy_champs: list[str],
    ally_champs: list[str],
    lane_opponent: str | None = None,
) -> list[dict]:
    """
    Return a list of item recommendations sorted by priority, each entry:
        { "item": str, "tier": str, "reason": str, "recommended": bool }
    """

    # --- Enemy breakdown ---
    n_enemies = len(enemy_champs)
    ap_count = sum(1 for c in enemy_champs if is_ap(c))
    ad_count = n_enemies - ap_count
    ranged_count = sum(1 for c in enemy_champs if is_ranged(c))
    melee_count = n_enemies - ranged_count
    crit_count = sum(1 for c in enemy_champs if is_crit(c))
    dot_champs = [c for c in enemy_champs if is_dot(c)]
    burst_ap_champs = [c for c in enemy_champs if is_burst_ap(c)]
    sustained_ap_champs = [c for c in enemy_champs if is_sustained_ap(c)]
    ap_assassin_champs = [c for c in enemy_champs if is_ap_assassin(c)]
    ad_assassin_champs = [c for c in enemy_champs if is_ad_assassin(c)]
    aa_count = sum(1 for c in enemy_champs if is_aa_heavy(c))
    anti_heal_present = any(is_anti_heal(c) for c in enemy_champs)
    true_dmg_present = any(is_true_damage(c) for c in enemy_champs)

    # --- Ally breakdown ---
    allied_carries = [c for c in ally_champs if is_carry(c)]
    has_allied_carry = len(allied_carries) > 0
    ally_ap_count = sum(1 for c in ally_champs if is_ap(c))

    # Convenience flags
    heavy_ap = ap_count >= 2
    heavy_ad = ad_count >= 3
    heavy_ranged = ranged_count >= 3
    heavy_melee = melee_count >= 3
    has_crit = crit_count >= 1
    heavy_crit = crit_count >= 2
    has_dot = len(dot_champs) >= 1
    has_aa = aa_count >= 2
    burst_ap_count = len(burst_ap_champs)
    sustained_ap_count = len(sustained_ap_champs)
    assassin_count = len(ap_assassin_champs) + len(ad_assassin_champs)
    burst_ap_heavy = burst_ap_count >= 2
    assassin_heavy = assassin_count >= 2

    lane_champ = lane_opponent or ""
    lane_known = bool(lane_champ)
    lane_is_ap = is_ap(lane_champ) if lane_known else False
    lane_is_burst_ap = is_burst_ap(lane_champ) if lane_known else False
    lane_is_sustained_ap = is_sustained_ap(lane_champ) if lane_known else False
    lane_is_ranged = is_ranged(lane_champ) if lane_known else False
    lane_is_aa = is_aa_heavy(lane_champ) if lane_known else False
    lane_has_true_dmg = is_true_damage(lane_champ) if lane_known else False
    lane_is_crit = is_crit(lane_champ) if lane_known else False

    recommendations: list[dict] = []

    def add(item, tier, recommended, reason, lane_priority=0, lane_reason=""):
        recommendations.append({
            "item": item,
            "tier": tier,
            "recommended": recommended,
            "reason": reason,
            "lane_priority": lane_priority,
            "lane_reason": lane_reason,
        })

    # -----------------------------------------------------------------------
    # S-Tier
    # -----------------------------------------------------------------------
    # Jak'Sho — reliable in almost any game
    add(
        "Jak'Sho, The Protean", "S",
        True,
        "Resistance-scaling staple — good in virtually every game.",
    )

    # Spirit Visage — great with ≥2 AD / limited AP, innate shield/heal synergy
    spirit_visage_recommended = not heavy_ap
    spirit_visage_reason = (
        "Synergises with K'Sante's innate shields and healing; "
        + ("ideal here because enemy AP threat is limited." if spirit_visage_recommended
           else "less valuable with heavy AP — consider Kaenic Rookern or Force of Nature instead.")
    )
    spirit_lane_priority = 2 if lane_known and lane_is_ap and not lane_is_burst_ap else 0
    spirit_lane_reason = (
        f"Helpful early lane MR/sustain into {lane_champ}."
        if spirit_lane_priority > 0
        else ""
    )
    add(
        "Spirit Visage",
        "S",
        spirit_visage_recommended,
        spirit_visage_reason,
        spirit_lane_priority,
        spirit_lane_reason,
    )

    # Kaenic Rookern — counter heavy magic burst
    kaenic_lane_priority = 3 if lane_known and (lane_is_burst_ap or is_ap_assassin(lane_champ)) else 0
    kaenic_recommended = heavy_ap or burst_ap_heavy or len(ap_assassin_champs) >= 1 or kaenic_lane_priority > 0
    kaenic_reason = (
        (
            "Premier MR item against burst AP threats"
            + (f" ({', '.join(burst_ap_champs)})" if burst_ap_champs else "")
            + (f" and AP assassins ({', '.join(ap_assassin_champs)})." if ap_assassin_champs else ".")
        )
        if kaenic_recommended
        else "Skip unless you need dedicated MR (consider Spirit Visage instead)."
    )
    add(
        "Kaenic Rookern",
        "S",
        kaenic_recommended,
        kaenic_reason,
        kaenic_lane_priority,
        (f"Top lane burst/AP pressure from {lane_champ} makes early MR very high value." if kaenic_lane_priority > 0 else ""),
    )

    # Randuin's Omen — vs crit or as kidnap tool
    randuins_lane_priority = 2 if lane_known and (lane_is_crit or lane_is_aa) else 0
    randuins_recommended = has_crit or heavy_ad or randuins_lane_priority > 0
    randuins_reason = (
        "70% slow guarantees kidnaps; passive counters crit"
        + (f" ({crit_count} crit champion(s) detected)." if has_crit else ".")
        + ("" if randuins_recommended else " Less impactful without crit targets; still decent for the slow.")
    )
    add(
        "Randuin's Omen",
        "S",
        randuins_recommended,
        randuins_reason,
        randuins_lane_priority,
        (f"Strong lane armor buy into auto-attack lane opponent {lane_champ}." if randuins_lane_priority > 0 else ""),
    )

    # Iceborn Gauntlet — great melee tool, falls off vs ranged
    iceborn_recommended = not heavy_ranged
    iceborn_reason = (
        "Core bread-and-butter item for landing spells and auto-combos."
        if iceborn_recommended
        else f"Loses significant value here — {ranged_count} ranged enemies make it hard to land autos."
    )
    iceborn_lane_priority = 2 if lane_known and not lane_is_ranged and not lane_is_ap else 0
    add(
        "Iceborn Gauntlet",
        "S",
        iceborn_recommended,
        iceborn_reason,
        iceborn_lane_priority,
        (f"Great lane stickiness into melee lane opponent {lane_champ}." if iceborn_lane_priority > 0 else ""),
    )

    # Knight's Vow — only when you have a carry to protect
    knights_vow_recommended = has_allied_carry
    knights_vow_reason = (
        f"Redirect damage to protect your allied carry"
        + (f" ({', '.join(allied_carries)})." if allied_carries else ".")
        if has_allied_carry
        else "Skip — Knight's Vow only shines when you have a fed carry to redirect damage to."
    )
    add("Knight's Vow", "S", knights_vow_recommended, knights_vow_reason)

    # -----------------------------------------------------------------------
    # A-Tier
    # -----------------------------------------------------------------------
    # Protoplasm Harness — great health/AH and E-shield scaling
    protoplasm_lane_priority = 1 if lane_known else 0
    add(
        "Protoplasm Harness", "A",
        True,
        "Cost-effective health, ability haste, and a lifeline passive that boosts E shield scaling.",
        protoplasm_lane_priority,
        (f"Safe lane-stabilizing first buy when matchup vs {lane_champ} is volatile." if protoplasm_lane_priority > 0 else ""),
    )

    # Unending Despair — vs 3+ melee without anti-heal
    unending_recommended = heavy_melee and not anti_heal_present
    unending_reason = (
        f"Strong drain item in this melee-heavy matchup ({melee_count} melee enemies)."
        if heavy_melee and not anti_heal_present
        else (
            f"Enemy anti-heal reduces effectiveness." if anti_heal_present
            else f"Only {melee_count} melee enemies — value drops below 3."
        )
    )
    unending_lane_priority = 2 if lane_known and not lane_is_ranged and not lane_is_ap and not anti_heal_present else 0
    add(
        "Unending Despair",
        "A",
        unending_recommended,
        unending_reason,
        unending_lane_priority,
        (f"Lane drain value is good into sustained melee lane from {lane_champ}." if unending_lane_priority > 0 else ""),
    )

    # Zeke's Convergence — alternative first item when enemies are ranged
    zekes_recommended = heavy_ranged
    zekes_reason = (
        f"Better first item than Iceborn vs ranged-heavy enemy team ({ranged_count} ranged)."
        if zekes_recommended
        else "Prefer Iceborn Gauntlet in this composition."
    )
    add("Zeke's Convergence", "A", zekes_recommended, zekes_reason)

    # Frozen Heart — vs auto-attack heavy, no health but great armor scaling
    frozen_lane_priority = 3 if lane_known and lane_is_aa and not lane_is_ap else 0
    frozen_heart_recommended = has_aa or frozen_lane_priority > 0
    frozen_heart_reason = (
        f"Great armor + aura vs auto-attack heavy team ({aa_count} heavy AA champions)."
        if has_aa
        else "Less impactful without heavy auto-attackers."
    )
    add(
        "Frozen Heart",
        "A",
        frozen_heart_recommended,
        frozen_heart_reason,
        frozen_lane_priority,
        (f"Excellent lane armor spike into AA-heavy lane opponent {lane_champ}." if frozen_lane_priority > 0 else ""),
    )

    # Dead Man's Plate — compensates for K'Sante's low base movement speed
    add(
        "Dead Man's Plate", "A",
        assassin_heavy or (lane_known and lane_is_ranged),
        (
            f"Useful into assassin-heavy comps ({assassin_count} assassins) for mobility and chase/disengage."
            if assassin_heavy or (lane_known and lane_is_ranged)
            else "Situational sleeper pick — compensates for K'Sante's low base movement speed and adds slow resistance."
        ),
        (2 if lane_known and lane_is_ranged else 0),
        (f"Prioritize lane movement into ranged top {lane_champ}." if lane_known and lane_is_ranged else ""),
    )

    # Force of Nature — vs DoT / burn champs
    fon_lane_priority = 2 if lane_known and (lane_is_sustained_ap or is_dot(lane_champ)) else 0
    fon_recommended = has_dot or (heavy_ap and sustained_ap_count >= 2) or fon_lane_priority > 0
    fon_reason = (
        f"Strong pickup against burn/DoT champions in this game: {', '.join(dot_champs)}."
        if has_dot
        else (
            f"Good MR stacking option into sustained AP DPS threats ({', '.join(sustained_ap_champs)})."
            if fon_recommended
            else "Skip unless you face significant burn/DoT or sustained AP sources."
        )
    )
    add(
        "Force of Nature",
        "A",
        fon_recommended,
        fon_reason,
        fon_lane_priority,
        (f"Strong lane MR stacking into sustained magic damage from {lane_champ}." if fon_lane_priority > 0 else ""),
    )

    # Anathema's Chains — single-target burst control when assassins are present.
    anathema_recommended = assassin_heavy or burst_ap_heavy
    anathema_reason = (
        "Strong anti-carry option vs burst threats"
        + (f" (AP burst: {', '.join(burst_ap_champs)})." if burst_ap_champs else ".")
        if anathema_recommended
        else "Niche buy when you need to reduce one fed target's damage."
    )
    add("Anathema's Chains", "B", anathema_recommended, anathema_reason)

    # -----------------------------------------------------------------------
    # B/C-Tier
    # -----------------------------------------------------------------------
    # Thornmail — if behind vs auto-attackers (don't rush; Bramble Vest preferred early)
    thornmail_lane_priority = 2 if lane_known and lane_is_aa and not lane_is_ap else 0
    thornmail_recommended = (has_aa and ad_count >= 3) or thornmail_lane_priority > 0
    add(
        "Thornmail", "B",
        thornmail_recommended,
        "Decent if behind vs heavy auto-attackers, but prefer sitting on Bramble Vest — "
        "completing the full item can accidentally draw tower aggro and ruin Demolish procs.",
        thornmail_lane_priority,
        (f"Lane anti-heal/armor pressure is valuable into {lane_champ}." if thornmail_lane_priority > 0 else ""),
    )

    # Fimbulwinter — vs true damage / armor shred
    fimbul_lane_priority = 2 if lane_known and lane_has_true_dmg else 0
    fimbulwinter_recommended = true_dmg_present or fimbul_lane_priority > 0
    fimbulwinter_reason = (
        f"Niche shield-stacking pick to counter true damage / armor shred"
        + (" — relevant this game." if true_dmg_present else " — not a high priority here.")
    )
    add(
        "Fimbulwinter",
        "B",
        fimbulwinter_recommended,
        fimbulwinter_reason,
        fimbul_lane_priority,
        (f"Lane shielding helps absorb true-damage trades from {lane_champ}." if fimbul_lane_priority > 0 else ""),
    )

    # Locket of the Iron Solari — vs team AOE / burn ultimates (Karthus etc.)
    locket_champs = [c for c in enemy_champs if _normalize(c) in {"karthus", "orianna", "amumu"}]
    locket_recommended = len(locket_champs) > 0 or (has_allied_carry and (burst_ap_heavy or assassin_heavy))
    locket_reason = (
        f"Niche shield-burst item, effective against team-wide AOE ultimates: {', '.join(locket_champs)}."
        if len(locket_champs) > 0
        else (
            "Protective teamfight shield value is high when enemies have burst/assassin threat and you have a carry."
            if locket_recommended
            else "Situational — best into team-wide AOE ults or high burst threat against your carry."
        )
    )
    add("Locket of the Iron Solari", "C", locket_recommended, locket_reason)

    # Abyssal Mask — when multiple fed AP allies need magic shred
    abyssal_recommended = ally_ap_count >= 2
    abyssal_reason = (
        f"Shreds MR for {ally_ap_count} AP teammates — worthwhile if they are carrying."
        if abyssal_recommended
        else "Low-priority; only buy to shred MR when multiple fed AP allies are on your team."
    )
    add("Abyssal Mask", "C", abyssal_recommended, abyssal_reason)

    # -----------------------------------------------------------------------
    # D-Tier (to avoid)
    # -----------------------------------------------------------------------
    for item, reason in [
        ("Bandal Pipes",           "Not optimal for top-lane K'Sante."),
        ("Sunfire Aegis",          "Highly inefficient — K'Sante has enough wave clear in his kit already."),
        ("Hollow Radiance",        "Highly inefficient — K'Sante has enough wave clear in his kit already."),
        ("Warmog's Armor",         "Completely outclassed by Protoplasm Harness if you need a pure health item."),
        ("Heartsteel",             "Too expensive and lacks the immediate utility that Protoplasm Harness provides."),
    ]:
        add(item, "D", False, reason)

    return recommendations


def get_build_order(recommendations: list[dict]) -> list[dict]:
    build_order = [
        r for r in recommendations
        if r["recommended"] and r["tier"] not in ("D",)
    ]
    tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}
    # Lane-priority can override tier so critical laning buys show up first.
    build_order.sort(
        key=lambda r: (
            -r.get("lane_priority", 0),
            tier_rank.get(r["tier"], 99),
        )
    )
    return build_order


def detect_lane_opponent(all_players: list[dict], enemy_team: str) -> str | None:
    # Primary path: use explicit role/position tags from live data if present.
    for player in all_players:
        if player.get("team", "") != enemy_team:
            continue
        pos = _normalize(player.get("position", ""))
        if pos in TOP_POSITION_TAGS:
            return player.get("championName", "")

    # Fallback: pick the first enemy that is in a known top-lane champion pool.
    for player in all_players:
        if player.get("team", "") != enemy_team:
            continue
        champ = player.get("championName", "")
        if is_top_laner(champ):
            return champ

    return None


# ---------------------------------------------------------------------------
# Output formatter
# ---------------------------------------------------------------------------

TIER_ORDER = ["S", "A", "B", "C", "D"]
TIER_LABELS = {
    "S": "S-Tier (Core & Best Items)",
    "A": "A-Tier (Strong & Situational)",
    "B": "B-Tier (Niche Utility)",
    "C": "C-Tier (Niche Utility)",
    "D": "D-Tier (Avoid)",
}
CHECKMARK = "\u2713"
CROSS = "\u2717"


def print_recommendations(
    ksante_team: str,
    enemy_champs: list[str],
    ally_champs: list[str],
    recommendations: list[dict],
    lane_opponent: str | None = None,
) -> None:
    print()
    print("=" * 60)
    print("  K'SANTE BUILD ADVISOR")
    print("=" * 60)
    print(f"\nYour team  : {ksante_team}")
    print(f"Allies     : {', '.join(ally_champs) if ally_champs else '(none detected)'}")
    print(f"Enemies    : {', '.join(enemy_champs) if enemy_champs else '(none detected)'}")
    print(f"Lane enemy : {lane_opponent if lane_opponent else '(not confidently detected)'}")
    print()

    for tier in TIER_ORDER:
        tier_items = [r for r in recommendations if r["tier"] == tier]
        if not tier_items:
            continue
        print(f"--- {TIER_LABELS[tier]} ---")
        for rec in tier_items:
            symbol = CHECKMARK if rec["recommended"] else CROSS
            print(f"  [{symbol}] {rec['item']}")
            print(f"       {rec['reason']}")
            if rec.get("lane_priority", 0) > 0:
                print(f"       Laning priority ({rec['lane_priority']}/3): {rec.get('lane_reason', 'Strong lane value.')}" )
        print()

    print("=" * 60)
    print("  RECOMMENDED BUILD ORDER (prioritised)")
    print("=" * 60)
    build_order = get_build_order(recommendations)
    for i, rec in enumerate(build_order, 1):
        lane_tag = " [LANE]" if rec.get("lane_priority", 0) > 0 else ""
        print(f"  {i:2}. [{rec['tier']}] {rec['item']}{lane_tag}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Fetching live game data...")
    data = fetch_game_data()

    all_players: list[dict] = data.get("allPlayers", [])
    active_player: dict = data.get("activePlayer", {})

    if not all_players:
        print("[ERROR] No players found in live game data.")
        sys.exit(1)

    # Identify active player's summoner name and champion
    active_summoner = active_player.get("summonerName", "")

    # Find active player's team
    ksante_team: str | None = None
    for player in all_players:
        if player.get("summonerName", "") == active_summoner:
            ksante_team = player.get("team", "")
            break

    # If active summoner name not found (some patch versions omit it),
    # fall back to the first player tagged as K'Sante.
    if not ksante_team:
        for player in all_players:
            if _normalize(player.get("championName", "")) == "ksante":
                ksante_team = player.get("team", "")
                break

    if not ksante_team:
        print(
            "[WARNING] Could not determine which team K'Sante is on. "
            "Assuming you are on the ORDER (blue) side."
        )
        ksante_team = "ORDER"

    enemy_team = "CHAOS" if ksante_team == "ORDER" else "ORDER"

    ally_champs: list[str] = []
    enemy_champs: list[str] = []

    for player in all_players:
        champ = player.get("championName", "Unknown")
        team = player.get("team", "")
        if team == ksante_team:
            # Exclude K'Sante himself from ally list to avoid confusing carry detection
            if _normalize(champ) != "ksante":
                ally_champs.append(champ)
        elif team == enemy_team:
            enemy_champs.append(champ)

    if not enemy_champs:
        print("[WARNING] Enemy champions not detected yet (loading screen?). Try again in-game.")
        sys.exit(0)

    lane_opponent = detect_lane_opponent(all_players, enemy_team)

    recommendations = analyze_composition(enemy_champs, ally_champs, lane_opponent=lane_opponent)
    print_recommendations(
        ksante_team,
        enemy_champs,
        ally_champs,
        recommendations,
        lane_opponent=lane_opponent,
    )


if __name__ == "__main__":
    main()
