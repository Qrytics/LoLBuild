"""
Tests for the K'Sante build advisor recommendation engine.
Run with: python -m pytest test_ksante_build.py -v
"""

import pytest
from ksante_build import (
    analyze_composition,
    detect_lane_opponent,
    get_build_order,
    _normalize,
    is_ap,
    is_ranged,
    is_crit,
    is_dot,
    is_burst_ap,
    is_sustained_ap,
    is_aa_heavy,
    is_true_damage,
    is_ap_assassin,
    is_ad_assassin,
    is_carry,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get_rec(recommendations, item_name):
    """Return the recommendation dict for a given item name (case-insensitive)."""
    for rec in recommendations:
        if _normalize(rec["item"]) == _normalize(item_name):
            return rec
    return None


# ---------------------------------------------------------------------------
# S-Tier tests
# ---------------------------------------------------------------------------

class TestJakSho:
    def test_always_recommended(self):
        """Jak'Sho should be recommended in every composition."""
        for enemies in [
            ["Garen", "Darius", "Vi", "Jinx", "Lux"],
            ["Syndra", "Orianna", "Zoe", "Lux", "Brand"],
            ["Teemo", "Varus", "Zed", "Karthus", "Miss Fortune"],
        ]:
            recs = analyze_composition(enemies, [])
            rec = get_rec(recs, "Jak'Sho, The Protean")
            assert rec is not None
            assert rec["recommended"] is True, f"Jak'Sho should always be recommended, enemies={enemies}"


class TestSpiritVisage:
    def test_recommended_vs_ad_heavy(self):
        enemies = ["Garen", "Darius", "Vi", "Jinx", "Tryndamere"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Spirit Visage")
        assert rec["recommended"] is True

    def test_not_recommended_vs_heavy_ap(self):
        enemies = ["Syndra", "Brand", "Lux", "Karthus", "Orianna"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Spirit Visage")
        assert rec["recommended"] is False


class TestKaenicRookern:
    def test_recommended_vs_heavy_ap(self):
        enemies = ["Syndra", "Brand", "Lux", "Karthus", "Orianna"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Kaenic Rookern")
        assert rec["recommended"] is True

    def test_not_recommended_vs_ad(self):
        enemies = ["Garen", "Darius", "Vi", "Jinx", "Tryndamere"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Kaenic Rookern")
        assert rec["recommended"] is False


class TestRanduinsOmen:
    def test_recommended_vs_crit(self):
        enemies = ["Jinx", "Caitlyn", "Draven", "Yasuo", "Tryndamere"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Randuin's Omen")
        assert rec["recommended"] is True

    def test_recommended_vs_heavy_ad(self):
        enemies = ["Darius", "Garen", "Vi", "Wukong", "Jarvan IV"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Randuin's Omen")
        assert rec["recommended"] is True


class TestIcebornGauntlet:
    def test_recommended_vs_melee_heavy(self):
        enemies = ["Darius", "Garen", "Vi", "Wukong", "Jarvan IV"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Iceborn Gauntlet")
        assert rec["recommended"] is True

    def test_not_recommended_vs_heavy_ranged(self):
        enemies = ["Caitlyn", "Lux", "Teemo", "Jinx", "Syndra"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Iceborn Gauntlet")
        assert rec["recommended"] is False


class TestKnightsVow:
    def test_recommended_with_allied_carry(self):
        allies = ["Jinx", "Amumu", "Lux", "Nasus"]
        enemies = ["Darius", "Vi", "Garen", "Brand", "Syndra"]
        recs = analyze_composition(enemies, allies)
        rec = get_rec(recs, "Knight's Vow")
        assert rec["recommended"] is True

    def test_not_recommended_without_carry(self):
        allies = ["Amumu", "Sion", "Galio", "Nasus"]
        enemies = ["Darius", "Vi", "Garen", "Brand", "Syndra"]
        recs = analyze_composition(enemies, allies)
        rec = get_rec(recs, "Knight's Vow")
        assert rec["recommended"] is False


# ---------------------------------------------------------------------------
# A-Tier tests
# ---------------------------------------------------------------------------

class TestProtoplasm:
    def test_always_recommended(self):
        recs = analyze_composition(["Garen", "Jinx", "Brand", "Vi", "Lux"], [])
        rec = get_rec(recs, "Protoplasm Harness")
        assert rec["recommended"] is True


class TestUnendingDespair:
    def test_recommended_vs_3_melee_no_anti_heal(self):
        enemies = ["Darius", "Garen", "Vi", "Brand", "Syndra"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Unending Despair")
        assert rec["recommended"] is True

    def test_not_recommended_vs_anti_heal(self):
        # Katarina applies anti-heal
        enemies = ["Darius", "Garen", "Vi", "Katarina", "Syndra"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Unending Despair")
        assert rec["recommended"] is False

    def test_not_recommended_vs_ranged_heavy(self):
        enemies = ["Caitlyn", "Lux", "Teemo", "Jinx", "Syndra"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Unending Despair")
        assert rec["recommended"] is False


class TestZekesConvergence:
    def test_recommended_vs_ranged_heavy(self):
        enemies = ["Caitlyn", "Lux", "Teemo", "Jinx", "Syndra"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Zeke's Convergence")
        assert rec["recommended"] is True

    def test_not_recommended_vs_melee(self):
        enemies = ["Darius", "Garen", "Vi", "Wukong", "Jarvan IV"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Zeke's Convergence")
        assert rec["recommended"] is False


class TestFrozenHeart:
    def test_recommended_vs_aa_heavy(self):
        enemies = ["Jinx", "Caitlyn", "Master Yi", "Draven", "Yasuo"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Frozen Heart")
        assert rec["recommended"] is True

    def test_not_recommended_vs_casters(self):
        enemies = ["Syndra", "Lux", "Brand", "Karthus", "Orianna"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Frozen Heart")
        assert rec["recommended"] is False


class TestForceOfNature:
    def test_recommended_vs_dot_champs(self):
        enemies = ["Brand", "Teemo", "Garen", "Vi", "Jarvan IV"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Force of Nature")
        assert rec["recommended"] is True

    def test_not_recommended_without_dot(self):
        enemies = ["Garen", "Darius", "Vi", "Jinx", "Lux"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Force of Nature")
        assert rec["recommended"] is False


# ---------------------------------------------------------------------------
# B/C-Tier tests
# ---------------------------------------------------------------------------

class TestFimbulwinter:
    def test_recommended_vs_true_damage(self):
        enemies = ["Fiora", "Vayne", "Garen", "Camille", "Lux"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Fimbulwinter")
        assert rec["recommended"] is True

    def test_not_recommended_without_true_damage(self):
        # None of these champions have notable true-damage in their kits
        enemies = ["Sett", "Malphite", "Vi", "Jinx", "Brand"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Fimbulwinter")
        assert rec["recommended"] is False


class TestLocket:
    def test_recommended_vs_karthus(self):
        enemies = ["Karthus", "Darius", "Vi", "Jinx", "Garen"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Locket of the Iron Solari")
        assert rec["recommended"] is True

    def test_not_recommended_without_aoe_ult(self):
        enemies = ["Syndra", "Darius", "Vi", "Jinx", "Garen"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Locket of the Iron Solari")
        assert rec["recommended"] is False


class TestAbyssalMask:
    def test_recommended_with_multiple_ap_allies(self):
        allies = ["Syndra", "Brand", "Lux", "Jinx"]
        enemies = ["Garen", "Vi", "Darius", "Wukong", "Jarvan IV"]
        recs = analyze_composition(enemies, allies)
        rec = get_rec(recs, "Abyssal Mask")
        assert rec["recommended"] is True

    def test_not_recommended_with_few_ap_allies(self):
        allies = ["Syndra", "Jinx", "Wukong", "Garen"]
        enemies = ["Garen", "Vi", "Darius", "Wukong", "Jarvan IV"]
        recs = analyze_composition(enemies, allies)
        rec = get_rec(recs, "Abyssal Mask")
        assert rec["recommended"] is False


# ---------------------------------------------------------------------------
# D-Tier tests (always avoid)
# ---------------------------------------------------------------------------

class TestDTierItems:
    @pytest.mark.parametrize("item", [
        "Bandal Pipes",
        "Sunfire Aegis",
        "Hollow Radiance",
        "Warmog's Armor",
        "Heartsteel",
    ])
    def test_never_recommended(self, item):
        recs = analyze_composition(
            ["Garen", "Darius", "Vi", "Jinx", "Lux"],
            ["Syndra", "Brand", "Amumu", "Caitlyn"],
        )
        rec = get_rec(recs, item)
        assert rec is not None, f"Item '{item}' not found in recommendations"
        assert rec["recommended"] is False, f"D-Tier item '{item}' should never be recommended"
        assert rec["tier"] == "D"


# ---------------------------------------------------------------------------
# Build order tests
# ---------------------------------------------------------------------------

class TestBuildOrder:
    def test_no_d_tier_in_recommended(self):
        recs = analyze_composition(
            ["Garen", "Darius", "Vi", "Jinx", "Lux"],
            ["Syndra", "Jinx", "Amumu", "Caitlyn"],
        )
        recommended = [r for r in recs if r["recommended"]]
        for rec in recommended:
            assert rec["tier"] != "D", f"D-tier item '{rec['item']}' should not be in recommended list"

    def test_jakSho_always_in_build(self):
        recs = analyze_composition(["Garen", "Jinx", "Brand", "Vi", "Lux"], [])
        recommended_names = [_normalize(r["item"]) for r in recs if r["recommended"]]
        assert _normalize("Jak'Sho, The Protean") in recommended_names

    def test_protoplasm_always_in_build(self):
        recs = analyze_composition(["Garen", "Jinx", "Brand", "Vi", "Lux"], [])
        recommended_names = [_normalize(r["item"]) for r in recs if r["recommended"]]
        assert _normalize("Protoplasm Harness") in recommended_names

    def test_lane_priority_can_override_tier_order(self):
        recs = analyze_composition(
            ["Vayne", "Lux", "Syndra", "Vi", "Jarvan IV"],
            [],
            lane_opponent="Vayne",
        )
        build_order = get_build_order(recs)
        assert build_order[0]["item"] == "Frozen Heart"
        assert build_order[0]["lane_priority"] >= 3


# ---------------------------------------------------------------------------
# Normalisation tests
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_strips_apostrophe(self):
        assert _normalize("K'Sante") == "ksante"

    def test_strips_spaces(self):
        assert _normalize("Miss Fortune") == "missfortune"

    def test_lowercase(self):
        assert _normalize("GAREN") == "garen"


# ---------------------------------------------------------------------------
# Champion knowledge base regression tests
# ---------------------------------------------------------------------------

class TestChampionKnowledgeBase:
    def test_aurora_is_ap_and_ranged(self):
        assert is_ap("Aurora") is True
        assert is_ranged("Aurora") is True

    def test_smolder_is_crit_aa_and_carry(self):
        assert is_crit("Smolder") is True
        assert is_aa_heavy("Smolder") is True
        assert is_carry("Smolder") is True

    def test_lillia_is_dot(self):
        assert is_dot("Lillia") is True

    def test_burst_vs_sustained_ap_classification(self):
        assert is_burst_ap("Syndra") is True
        assert is_sustained_ap("Syndra") is False
        assert is_sustained_ap("Cassiopeia") is True

    def test_gwen_and_darius_are_true_damage(self):
        assert is_true_damage("Gwen") is True
        assert is_true_damage("Darius") is True

    def test_belveth_name_variants_are_aa_heavy(self):
        assert is_aa_heavy("Bel'Veth") is True
        assert is_aa_heavy("Belveth") is True

    def test_assassin_classification(self):
        assert is_ap_assassin("LeBlanc") is True
        assert is_ad_assassin("Zed") is True


class TestKnowledgeImpactOnRecommendations:
    def test_aurora_counts_toward_heavy_ap_for_kaenic(self):
        enemies = ["Aurora", "Syndra", "Garen", "Vi", "Jinx"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Kaenic Rookern")
        assert rec["recommended"] is True

    def test_smolder_counts_toward_randuins(self):
        enemies = ["Smolder", "Garen", "Vi", "Brand", "Syndra"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Randuin's Omen")
        assert rec["recommended"] is True

    def test_deadmans_recommended_vs_assassin_heavy(self):
        enemies = ["Zed", "Talon", "Garen", "Jinx", "Lux"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Dead Man's Plate")
        assert rec["recommended"] is True

    def test_kaenic_recommended_vs_burst_ap_profile(self):
        enemies = ["Syndra", "LeBlanc", "Garen", "Vi", "Jinx"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Kaenic Rookern")
        assert rec["recommended"] is True

    def test_locket_recommended_with_carry_vs_burst(self):
        enemies = ["Syndra", "LeBlanc", "Garen", "Vi", "Jinx"]
        allies = ["Jinx", "Amumu", "Nasus", "Lulu"]
        recs = analyze_composition(enemies, allies)
        rec = get_rec(recs, "Locket of the Iron Solari")
        assert rec["recommended"] is True

    def test_anathemas_recommended_vs_assassins(self):
        enemies = ["Zed", "Kha'Zix", "Garen", "Jinx", "Lux"]
        recs = analyze_composition(enemies, [])
        rec = get_rec(recs, "Anathema's Chains")
        assert rec["recommended"] is True

    def test_kaenic_lane_priority_vs_ap_lane(self):
        enemies = ["Garen", "Vi", "Jinx", "Sett", "Draven"]
        recs = analyze_composition(enemies, [], lane_opponent="Akali")
        rec = get_rec(recs, "Kaenic Rookern")
        assert rec["recommended"] is True
        assert rec["lane_priority"] >= 3

    def test_fimbulwinter_lane_priority_vs_true_damage_lane(self):
        enemies = ["Lux", "Jinx", "Vi", "Amumu", "Leona"]
        recs = analyze_composition(enemies, [], lane_opponent="Fiora")
        rec = get_rec(recs, "Fimbulwinter")
        assert rec["recommended"] is True
        assert rec["lane_priority"] >= 2


class TestLaneOpponentDetection:
    def test_detects_enemy_top_from_position(self):
        all_players = [
            {"team": "ORDER", "championName": "K'Sante", "position": "TOP"},
            {"team": "CHAOS", "championName": "Teemo", "position": "TOP"},
            {"team": "CHAOS", "championName": "Vi", "position": "JUNGLE"},
        ]
        lane = detect_lane_opponent(all_players, "CHAOS")
        assert lane == "Teemo"

    def test_fallback_detects_top_pool_champion(self):
        all_players = [
            {"team": "CHAOS", "championName": "Jinx", "position": ""},
            {"team": "CHAOS", "championName": "Darius", "position": ""},
            {"team": "CHAOS", "championName": "Vi", "position": ""},
        ]
        lane = detect_lane_opponent(all_players, "CHAOS")
        assert lane == "Darius"
