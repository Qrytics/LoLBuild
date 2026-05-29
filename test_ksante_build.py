"""
Tests for the K'Sante build advisor recommendation engine.
Run with: python -m pytest test_ksante_build.py -v
"""

import pytest
from ksante_build import analyze_composition, _normalize


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
        enemies = ["Darius", "Malphite", "Vi", "Jinx", "Brand"]
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
