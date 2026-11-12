"""Crop and soil parameters.

APPROXIMATE values for a hackathon prototype. They encode relative differences
between crops (who needs more water, who fixes nitrogen), not exact agronomy.
TODO(team): check each row against FAO / Kazakh agronomy sources and cite them.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Crop:
    key: str
    name: str
    family: str          # cereal, legume, oilseed, pseudocereal, row, fallow
    t_min: float         # suitable Apr–Sep mean temperature range, °C
    t_max: float
    water_need: float    # seasonal water need, mm
    drought_tol: float   # 0..1
    soil_effect: float   # 0..1, contribution to soil health
    value: float         # 0..1, relative market value
    salt_tol: float = 0.3
    irrigated_only: bool = False


CROPS = {c.key: c for c in [
    Crop("wheat", "Wheat", "cereal", 12, 22, 330, 0.5, 0.30, 0.60, 0.5),
    Crop("barley", "Barley", "cereal", 11, 21, 290, 0.6, 0.30, 0.50, 0.7),
    Crop("oats", "Oats", "cereal", 11, 18, 330, 0.4, 0.40, 0.40, 0.4),
    Crop("millet", "Millet", "cereal", 17, 27, 250, 0.85, 0.40, 0.40, 0.5),
    Crop("maize", "Maize (grain)", "row", 18, 27, 500, 0.3, 0.20, 0.70, 0.3),
    Crop("sunflower", "Sunflower", "oilseed", 15, 24, 400, 0.7, 0.10, 0.75, 0.5),
    Crop("rapeseed", "Rapeseed (canola)", "oilseed", 11, 18, 360, 0.4, 0.50, 0.70, 0.4),
    Crop("flax", "Flax (linseed)", "oilseed", 12, 19, 280, 0.5, 0.40, 0.65, 0.3),
    Crop("peas", "Peas", "legume", 11, 19, 300, 0.4, 0.80, 0.55, 0.3),
    Crop("chickpea", "Chickpea", "legume", 15, 26, 250, 0.8, 0.70, 0.70, 0.4),
    Crop("lentil", "Lentil", "legume", 12, 22, 250, 0.7, 0.75, 0.65, 0.3),
    Crop("soybean", "Soybean", "legume", 18, 25, 450, 0.3, 0.75, 0.70, 0.3),
    Crop("buckwheat", "Buckwheat", "pseudocereal", 13, 20, 300, 0.4, 0.60, 0.50, 0.3),
    Crop("alfalfa", "Alfalfa", "legume", 13, 27, 600, 0.6, 0.95, 0.50, 0.6),
    Crop("cotton", "Cotton", "row", 21, 30, 700, 0.4, 0.10, 0.80, 0.7, irrigated_only=True),
    Crop("rice", "Rice", "cereal", 21, 30, 1100, 0.0, 0.20, 0.70, 0.6, irrigated_only=True),
    Crop("fallow", "Green manure / fallow", "fallow", -50, 50, 0, 1.0, 0.80, 0.00, 1.0),
]}


@dataclass(frozen=True)
class Soil:
    key: str
    name: str
    fertility: float     # 0..1
    water_hold: float    # plant-available water the profile can store, mm
    saline: bool = False


SOILS = {s.key: s for s in [
    Soil("chernozem", "Chernozem (black soil)", 0.9, 160),
    Soil("dark_chestnut", "Dark chestnut", 0.7, 130),
    Soil("light_chestnut", "Light chestnut / brown", 0.5, 100),
    Soil("sierozem", "Sierozem (grey desert soil)", 0.4, 80),
    Soil("saline", "Saline soil", 0.3, 70, saline=True),
]}

IRRIGATION_MM = 450  # extra seasonal water when the field is irrigated
