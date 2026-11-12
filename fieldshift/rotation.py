"""Crop suitability, rotation rules, scoring and search."""
from dataclasses import dataclass, field
from itertools import product

from .crops import CROPS, IRRIGATION_MM

ROTATION_YEARS = 4
TEMP_MARGIN = 4.0          # °C outside the range at which suitability reaches 0
MIN_SUITABILITY = 0.4      # crops below this are not used in recommendations
MAX_CANDIDATES = 10        # best-suited crops searched (plus fallow)
FALLOW_CARRYOVER = 0.4     # share of soil storage a fallow year adds for the next crop
CRITERIA = ("soil", "water", "profit", "resilience")


def available_water(climate, soil, irrigated):
    """Seasonal water a crop can use: rain + stored soil moisture + irrigation, mm."""
    stored = soil.water_hold * climate["season_wetness"]
    return climate["season_precip"] + stored + (IRRIGATION_MM if irrigated else 0)


def temp_fit(crop, temp):
    if crop.t_min <= temp <= crop.t_max:
        return 1.0
    gap = crop.t_min - temp if temp < crop.t_min else temp - crop.t_max
    return max(0.0, 1 - gap / TEMP_MARGIN)


def water_fit(crop, water):
    if crop.water_need == 0:
        return 1.0
    ratio = min(1.0, water / crop.water_need)
    # drought-tolerant crops lose less yield when water falls short
    return ratio ** (1 - 0.7 * crop.drought_tol)


def suitability(crop, climate, soil, irrigated, extra_water=0.0):
    if crop.irrigated_only and not irrigated:
        return 0.0
    water = available_water(climate, soil, irrigated) + extra_water
    s = temp_fit(crop, climate["season_temp"]) * water_fit(crop, water)
    if soil.saline:
        s *= 0.4 + 0.6 * crop.salt_tol
    return s


def _pairs(rot):
    """Consecutive (previous, next) pairs; a rotation repeats, so it wraps around."""
    return [(rot[i - 1], rot[i]) for i in range(len(rot))]


def rule_issues(rot):
    """Agronomic problems as (is_hard, text). Hard issues exclude a rotation from search."""
    issues = []
    counts = {k: rot.count(k) for k in set(rot)}
    for key, n in counts.items():
        limit = 2 if key == "wheat" else 1
        if n > limit:
            issues.append((True, f"{CROPS[key].name} is grown {n} times in {len(rot)} years"))
    for prev, nxt in _pairs(rot):
        a, b = CROPS[prev], CROPS[nxt]
        if prev == nxt:
            issues.append((True, f"{a.name} after {b.name}: pests and diseases build up"))
        elif a.family == b.family == "cereal":
            issues.append((False, f"{a.name} after {b.name}: cereal after cereal"))
        elif a.family == b.family and a.family in ("legume", "oilseed"):
            issues.append((True, f"{a.name} after {b.name}: same crop family twice"))
    return issues


@dataclass
class RotationResult:
    rotation: tuple
    scores: dict
    total: float
    issues: list = field(default_factory=list)
    reasons: list = field(default_factory=list)


def _clamp(x):
    return max(0.0, min(1.0, x))


def score_rotation(rot, now, future, soil, irrigated, weights):
    crops = [CROPS[k] for k in rot]
    water = available_water(now, soil, irrigated)
    real = [c for c in crops if c.family != "fallow"]

    cereal_pairs = sum(1 for a, b in _pairs(rot)
                       if CROPS[a].family == CROPS[b].family == "cereal")
    families = {c.family for c in real}
    has_legume = any(c.family == "legume" for c in crops)
    soil_score = (0.55 * sum(c.soil_effect for c in crops) / len(crops)
                  + 0.25 * min(1.0, len(families) / 3)
                  + 0.20 * has_legume
                  - 0.12 * cereal_pairs)

    water_parts, profit_parts = [], []
    for i, crop in enumerate(crops):
        prev = crops[i - 1]
        extra = soil.water_hold * FALLOW_CARRYOVER if prev.family == "fallow" else 0.0
        wf = water_fit(crop, water + extra)
        use = min(1.0, crop.water_need / (water + extra)) if water + extra > 0 else 1.0
        water_parts.append(0.6 * wf + 0.4 * (1 - use))

        suit = suitability(crop, now, soil, irrigated, extra)
        bonus = 1.15 if prev.family in ("legume", "fallow") else 1.0  # N credit / stored moisture
        profit_parts.append(crop.value * suit * (0.6 + 0.4 * soil.fertility) * bonus)

    resilience = sum(suitability(c, future, soil, irrigated) for c in real) / len(real)

    scores = {
        "soil": _clamp(soil_score),
        "water": _clamp(sum(water_parts) / len(crops)),
        "profit": _clamp(sum(profit_parts) / len(crops) / 0.75),  # 0.75 ≈ best realistic mean
        "resilience": _clamp(resilience),
    }
    w_sum = sum(weights.values()) or 1
    total = sum(scores[k] * weights[k] for k in CRITERIA) / w_sum
    return RotationResult(tuple(rot), scores, total, rule_issues(rot))


def explain(result, now, future_year, soil, irrigated):
    crops = [CROPS[k] for k in result.rotation]
    water = available_water(now, soil, irrigated)
    reasons = []
    for c in crops:
        if c.family == "legume":
            reasons.append(f"{c.name} fixes nitrogen from the air and feeds the next crop.")
            break
    families = {c.family for c in crops if c.family != "fallow"}
    if len(families) >= 3:
        reasons.append(f"{len(families)} different crop families break pest and disease cycles.")
    if any(c.family == "fallow" for c in crops):
        reasons.append("A green-manure / fallow year stores moisture and organic matter for the next crop.")
    thirsty = [c.name for c in crops if c.water_need > water]
    if thirsty:
        verb = "needs" if len(thirsty) == 1 else "need"
        reasons.append(f"Water risk: {', '.join(thirsty)} {verb} more than the ~{water:.0f} mm available.")
    else:
        reasons.append(f"Every crop fits within the ~{water:.0f} mm of water available in the season.")
    reasons.append(f"Stays {result.scores['resilience']:.0%} suitable under the {future_year} trend climate.")
    return reasons


def recommend(now, future, soil, irrigated, weights, top=3, future_year=2035):
    ranked = sorted(
        (k for k, c in CROPS.items() if c.family != "fallow"),
        key=lambda k: suitability(CROPS[k], now, soil, irrigated),
        reverse=True,
    )
    candidates = [k for k in ranked[:MAX_CANDIDATES]
                  if suitability(CROPS[k], now, soil, irrigated) >= MIN_SUITABILITY]
    candidates.append("fallow")

    seen, results = set(), []
    for rot in product(candidates, repeat=ROTATION_YEARS):
        canon = min(rot[i:] + rot[:i] for i in range(len(rot)))
        if canon in seen:
            continue
        seen.add(canon)
        if any(hard for hard, _ in rule_issues(rot)):
            continue
        results.append(score_rotation(rot, now, future, soil, irrigated, weights))

    results.sort(key=lambda r: r.total, reverse=True)
    picked, crop_sets = [], []
    for r in results:
        crop_set = set(r.rotation)
        if any(len(crop_set ^ s) < 2 for s in crop_sets):
            continue  # too similar to one already picked
        r.reasons = explain(r, now, future_year, soil, irrigated)
        picked.append(r)
        crop_sets.append(crop_set)
        if len(picked) == top:
            break
    return picked
