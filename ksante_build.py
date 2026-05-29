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
    "ahri", "akali", "anivia", "annie", "aurelionsol", "azir", "bard",
    "brand", "cassiopeia", "chogath", "corki", "diana", "ekko", "elise",
    "evelynn", "ezreal", "fiddlesticks", "fizz", "galio", "gangplank",
    "gragas", "heimerdinger", "hwei", "illaoi", "ivern", "janna",
    "jarvaniv", "jayce", "karma", "karthus", "kassadin", "katarina",
    "kayle", "kennen", "khazix", "kogmaw", "leblanc", "lissandra",
    "lulu", "lux", "malphite", "malzahar", "maokai", "masteryi",
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
    "ahri", "akshan", "alistar", "anivia", "annie", "aphelios", "ashe",
    "aurelionsol", "azir", "bard", "brand", "caitlyn", "cassiopeia",
    "corki", "draven", "elise", "ezreal", "fiddlesticks", "gangplank",
    "graves", "heimerdinger", "hwei", "jayce", "jhin", "jinx", "karma",
    "karthus", "kayle", "kennen", "khazix", "kogmaw", "leblanc",
    "lissandra", "lucian", "lulu", "lux", "malzahar", "miss fortune",
    "missfortune", "morgana", "nami", "neeko", "nidalee", "orianna",
    "quinn", "rumble", "ryze", "seraphine", "senna", "sion", "sivir",
    "sona", "soraka", "swain", "syndra", "teemo", "thresh", "tristana",
    "twisted fate", "twistedfate", "twitch", "urgot", "varus", "veigar",
    "velkoz", "vex", "viktor", "xayah", "xerath", "yasuo", "yuumi",
    "ziggs", "zilean", "zoe", "zyra",
}

# Champions that build critical strike (marksmen + some fighters).
CRIT_CHAMPIONS: set[str] = {
    "aphelios", "ashe", "caitlyn", "corki", "draven", "ezreal", "graves",
    "jhin", "jinx", "kayle", "khazix", "kogmaw", "lucian", "masteryi",
    "miss fortune", "missfortune", "quinn", "samira", "senna", "sivir",
    "tristana", "tryndamere", "twitch", "urgot", "varus", "xayah",
    "yasuo", "yone", "zeri",
}

# Champions with significant damage-over-time / burn effects.
DOT_CHAMPIONS: set[str] = {
    "brand", "cassiopeia", "malzahar", "singed", "teemo", "karthus",
    "mordekaiser", "swain", "zyra",
}

# Champions whose kit has notable anti-heal (grievous wounds application).
ANTI_HEAL_CHAMPIONS: set[str] = {
    "katarina", "kled", "mordekaiser", "varus", "braum", "miss fortune",
    "missfortune", "fizz", "singed",
}

# Champions with notable true damage (armor shred / true DMG threats).
TRUE_DAMAGE_CHAMPIONS: set[str] = {
    "camille", "cho'gath", "chogath", "fiora", "garen", "illaoi",
    "irelia", "jax", "olaf", "vayne",
}

# Champions with significant armor shred in their kit.
ARMOR_SHRED_CHAMPIONS: set[str] = {
    "black cleaver users",  # placeholder category, checked by item
    "corki", "jayce", "kayle", "lucian", "nasus", "renekton", "talon",
    "vi", "warwick", "yorick",
}

# Heavy auto-attack reliant champions (benefit most from Frozen Heart / Randuin's).
AA_CHAMPIONS: set[str] = {
    "aphelios", "ashe", "caitlyn", "corki", "draven", "ezreal", "graves",
    "irelia", "jax", "jhin", "jinx", "kayle", "kogmaw", "lucian",
    "masteryi", "miss fortune", "missfortune", "quinn", "samira", "senna",
    "sivir", "tristana", "tryndamere", "twitch", "urgot", "varus",
    "vayne", "warwick", "xayah", "yasuo", "yone", "zeri",
}

# Known carry roles (ADC / fed assassin / fed mage) – if YOUR TEAM has one.
CARRY_CHAMPION_ROLES: set[str] = {
    "aphelios", "ashe", "caitlyn", "corki", "draven", "ezreal", "graves",
    "jhin", "jinx", "kayle", "kogmaw", "lucian", "miss fortune",
    "missfortune", "quinn", "samira", "senna", "sivir", "tristana",
    "twitch", "urgot", "varus", "xayah", "yasuo", "yone", "zeri",
    "akali", "diana", "ekko", "irelia", "katarina", "khazix", "leblanc",
    "masteryi", "nidalee", "talon", "zed",
}


def _normalize(name: str) -> str:
    """Lowercase and strip spaces/apostrophes for champion-name comparison."""
    return name.lower().replace("'", "").replace(" ", "").replace(".", "")


def is_ap(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in AP_CHAMPIONS}


def is_ranged(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in RANGED_CHAMPIONS}


def is_crit(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in CRIT_CHAMPIONS}


def is_dot(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in DOT_CHAMPIONS}


def is_aa_heavy(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in AA_CHAMPIONS}


def is_anti_heal(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in ANTI_HEAL_CHAMPIONS}


def is_true_damage(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in TRUE_DAMAGE_CHAMPIONS}


def is_carry(champ: str) -> bool:
    return _normalize(champ) in {_normalize(c) for c in CARRY_CHAMPION_ROLES}


# ---------------------------------------------------------------------------
# Item recommendation engine
# ---------------------------------------------------------------------------

def analyze_composition(
    enemy_champs: list[str],
    ally_champs: list[str],
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

    recommendations: list[dict] = []

    def add(item, tier, recommended, reason):
        recommendations.append({
            "item": item,
            "tier": tier,
            "recommended": recommended,
            "reason": reason,
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
    add("Spirit Visage", "S", spirit_visage_recommended, spirit_visage_reason)

    # Kaenic Rookern — counter heavy magic burst
    kaenic_recommended = heavy_ap
    kaenic_reason = (
        "Premier MR item against heavy AP burst."
        if kaenic_recommended
        else "Skip unless you need dedicated MR (consider Spirit Visage instead)."
    )
    add("Kaenic Rookern", "S", kaenic_recommended, kaenic_reason)

    # Randuin's Omen — vs crit or as kidnap tool
    randuins_recommended = has_crit or heavy_ad
    randuins_reason = (
        "70% slow guarantees kidnaps; passive counters crit"
        + (f" ({crit_count} crit champion(s) detected)." if has_crit else ".")
        + ("" if randuins_recommended else " Less impactful without crit targets; still decent for the slow.")
    )
    add("Randuin's Omen", "S", randuins_recommended, randuins_reason)

    # Iceborn Gauntlet — great melee tool, falls off vs ranged
    iceborn_recommended = not heavy_ranged
    iceborn_reason = (
        "Core bread-and-butter item for landing spells and auto-combos."
        if iceborn_recommended
        else f"Loses significant value here — {ranged_count} ranged enemies make it hard to land autos."
    )
    add("Iceborn Gauntlet", "S", iceborn_recommended, iceborn_reason)

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
    add(
        "Protoplasm Harness", "A",
        True,
        "Cost-effective health, ability haste, and a lifeline passive that boosts E shield scaling.",
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
    add("Unending Despair", "A", unending_recommended, unending_reason)

    # Zeke's Convergence — alternative first item when enemies are ranged
    zekes_recommended = heavy_ranged
    zekes_reason = (
        f"Better first item than Iceborn vs ranged-heavy enemy team ({ranged_count} ranged)."
        if zekes_recommended
        else "Prefer Iceborn Gauntlet in this composition."
    )
    add("Zeke's Convergence", "A", zekes_recommended, zekes_reason)

    # Frozen Heart — vs auto-attack heavy, no health but great armor scaling
    frozen_heart_recommended = has_aa
    frozen_heart_reason = (
        f"Great armor + aura vs auto-attack heavy team ({aa_count} heavy AA champions)."
        if has_aa
        else "Less impactful without heavy auto-attackers."
    )
    add("Frozen Heart", "A", frozen_heart_recommended, frozen_heart_reason)

    # Dead Man's Plate — compensates for K'Sante's low base movement speed
    add(
        "Dead Man's Plate", "A",
        False,
        "Situational sleeper pick — compensates for K'Sante's low base movement speed and adds slow resistance.",
    )

    # Force of Nature — vs DoT / burn champs
    fon_recommended = has_dot
    fon_reason = (
        f"Strong pickup against burn/DoT champions in this game: {', '.join(dot_champs)}."
        if has_dot
        else "Skip unless you face significant burn/DoT sources."
    )
    add("Force of Nature", "A", fon_recommended, fon_reason)

    # -----------------------------------------------------------------------
    # B/C-Tier
    # -----------------------------------------------------------------------
    # Thornmail — if behind vs auto-attackers (don't rush; Bramble Vest preferred early)
    thornmail_recommended = has_aa and ad_count >= 3
    add(
        "Thornmail", "B",
        thornmail_recommended,
        "Decent if behind vs heavy auto-attackers, but prefer sitting on Bramble Vest — "
        "completing the full item can accidentally draw tower aggro and ruin Demolish procs.",
    )

    # Fimbulwinter — vs true damage / armor shred
    fimbulwinter_recommended = true_dmg_present
    fimbulwinter_reason = (
        f"Niche shield-stacking pick to counter true damage / armor shred"
        + (" — relevant this game." if true_dmg_present else " — not a high priority here.")
    )
    add("Fimbulwinter", "B", fimbulwinter_recommended, fimbulwinter_reason)

    # Locket of the Iron Solari — vs team AOE / burn ultimates (Karthus etc.)
    locket_champs = [c for c in enemy_champs if _normalize(c) in {"karthus", "orianna", "amumu"}]
    locket_recommended = len(locket_champs) > 0
    locket_reason = (
        f"Niche shield-burst item, effective against team-wide AOE ultimates: {', '.join(locket_champs)}."
        if locket_recommended
        else "Situational — only buy against team-wide AOE or burn ultimates (e.g., Karthus)."
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
) -> None:
    print()
    print("=" * 60)
    print("  K'SANTE BUILD ADVISOR")
    print("=" * 60)
    print(f"\nYour team  : {ksante_team}")
    print(f"Allies     : {', '.join(ally_champs) if ally_champs else '(none detected)'}")
    print(f"Enemies    : {', '.join(enemy_champs) if enemy_champs else '(none detected)'}")
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
        print()

    print("=" * 60)
    print("  RECOMMENDED BUILD ORDER (prioritised)")
    print("=" * 60)
    build_order = [
        r for r in recommendations
        if r["recommended"] and r["tier"] not in ("D",)
    ]
    # Sort: S first, then A, B, C
    tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}
    build_order.sort(key=lambda r: tier_rank.get(r["tier"], 99))
    for i, rec in enumerate(build_order, 1):
        print(f"  {i:2}. [{rec['tier']}] {rec['item']}")
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

    recommendations = analyze_composition(enemy_champs, ally_champs)
    print_recommendations(ksante_team, enemy_champs, ally_champs, recommendations)


if __name__ == "__main__":
    main()
