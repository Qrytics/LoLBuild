# LoLBuild: K'Sante Build Advisor

LoLBuild is a Python command-line tool that reads your current League of Legends match from the Riot Live Client Data API and recommends K'Sante itemization based on both team compositions.

It focuses on practical, matchup-driven tank item decisions and prints:
- Tiered recommendations (S, A, B, C, D)
- A lane-aware recommended build order using only items marked as recommended
- Human-readable reasons for every item

## What this project does

The script:
1. Connects to the local Live Client Data API at https://127.0.0.1:2999/liveclientdata.
2. Detects your team and enemy team from live match data.
3. Detects a likely lane opponent (enemy top) using live position data when available, with fallback heuristics.
4. Classifies enemy and ally champions into categories (AP, ranged, crit, DoT, anti-heal, true damage, burst AP, sustained AP, assassin profiles, etc.).
5. Applies rule-based logic to mark each item as recommended or not recommended.
6. Adds laning-priority scores to items that are especially valuable in lane matchups.
7. Prints an ordered build suggestion from recommended non-D-tier items, where critical lane picks can be prioritized early.

This project is deterministic and heuristic-based. It is not a machine learning model.

## Project structure

- ksante_build.py: Main script and recommendation engine.
- test_ksante_build.py: Pytest test suite for recommendation behavior.
- README.md: Project documentation.

## Requirements

- Python 3.10+ (the code uses modern type union syntax like dict | list)
- League of Legends client running
- An active in-progress game (not champion select, not post-game)

## Setup

### 1) Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install test dependency (optional but recommended)

```powershell
python -m pip install pytest
```

No runtime third-party packages are required for ksante_build.py itself.

## Running the advisor

Start a League game first, then run:

```powershell
python ksante_build.py
```

If the Live Client API is reachable and player data is present, you will get:
- Team and lane summary (your side, allies, enemies, likely lane opponent)
- Tiered item recommendations with reasons
- Prioritized recommended build order (lane-priority picks are tagged)

## Testing

Run all tests:

```powershell
python -m pytest -q
```

Current status in this workspace:
- 56 passed

The tests cover:
- Always-recommended core picks (for example, Jak'Sho, Protoplasm Harness)
- Composition-dependent picks (for example, Kaenic vs heavy AP, Iceborn vs low ranged pressure)
- Lane-opponent detection and lane-priority behavior
- Situational niche items (for example, Locket and Abyssal conditions)
- Never-recommended D-tier items
- Name normalization behavior

## Recommendation logic summary

The engine computes composition features and then applies item rules.

Enemy-side signals:
- AP vs AD distribution
- Ranged vs melee count
- Crit users
- Auto-attack-reliant champions
- DoT/burn champions
- Burst AP vs sustained AP profiles
- AP assassins and AD assassins
- Anti-heal presence
- True-damage presence

Lane-side signals:
- Detected lane opponent champion (enemy top)
- Lane damage profile (AP/AD, burst/sustained)
- Lane trade profile (ranged poke, AA-heavy, crit, true damage)

Ally-side signals:
- Presence of an allied carry (for Knight's Vow value)
- Number of AP allies (for Abyssal Mask value)

Item logic examples:
- Spirit Visage: generally good, but deprioritized into heavy AP.
- Kaenic Rookern: recommended into heavy AP.
- Iceborn Gauntlet: strong by default, weaker into very ranged-heavy comps.
- Zeke's Convergence: preferred first-item alternative into ranged-heavy comps.
- Unending Despair: best with multiple melee enemies and no anti-heal pressure.
- Force of Nature: elevated when DoT/burn threats are present.
- Fimbulwinter: niche response to true-damage/armor-shred contexts.

## Output format

The script prints:
1. Header with detected teams and champions.
2. Tier blocks:
	- S-Tier (Core & Best Items)
	- A-Tier (Strong & Situational)
	- B-Tier (Niche Utility)
	- C-Tier (Niche Utility)
	- D-Tier (Avoid)
3. Recommended Build Order:
	- Includes only items where recommended = True
	- Excludes D-tier
	- Lane-priority can override tier priority when matchup demands an early defensive spike
	- Lane-priority items are shown with [LANE]

## Data source and API notes

- Endpoint base: https://127.0.0.1:2999/liveclientdata
- Script endpoint used: /allgamedata
- Riot's local endpoint uses a self-signed certificate. The script disables TLS certificate verification for this local API connection.

## Known limitations

- Rules are static and handcrafted, not patch-adaptive.
- Champion category sets are manually maintained.
- Recommendations still do not inspect:
  - Gold spikes and exact item completion timings
  - Rune setups
	- Wave state and exact lane tempo
  - Summoner spell context
  - Live item inventories of all players
- Designed specifically for K'Sante.

## Troubleshooting

If you get API connection errors:
- Ensure League is open and you are actively in a match.
- Retry after loading fully into game.

If you see no players/enemies detected:
- Wait a few seconds and rerun.
- Verify the match has started and live data is available.

If tests do not run:
- Install pytest in your active environment:

```powershell
python -m pip install pytest
```

## Extending the project

Common improvements:
- Move champion category sets into a dedicated data file.
- Add patch/version metadata and changelog-driven updates.
- Add additional conditions per item (for example, lane archetype, snowball state).
- Add JSON output mode for integration with overlays or other tooling.
- Expand tests with edge cases and regression snapshots.

## Disclaimer

Item advice is heuristic and intended as a gameplay aid. Final decisions should account for your lane state, game tempo, and personal matchup comfort.
