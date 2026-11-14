"""Crop and soil parameters.

Prototype parameters, with evidence and unresolved limits in ../SOURCES.md.
Selected water needs are nominal seasonal crop evapotranspiration (ETc), not
irrigation application depths or minimum water needed to survive. Rice's
field_water_need also includes paddy preparation and flooding. Temperature
bounds and relative scores remain uncalibrated prototype assumptions.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Crop:
    key: str
    name: str
    family: str          # cereal, legume, oilseed, pseudocereal, row, fallow
    t_min: float         # suitable Apr–Sep mean temperature range, °C
    t_max: float
    water_need: float    # nominal seasonal crop ETc, mm; see SOURCES.md
    drought_tol: float   # 0..1
    soil_effect: float   # 0..1, contribution to soil health
    value: float         # 0..1, relative market value
    salt_tol: float = 0.3  # heuristic 0..1, not a measured salinity threshold
    season_days: int = 0  # frost-free days needed from sowing to harvest; 0 = no limit
    irrigated_only: bool = False
    saturation_mm: float = 0.0  # one-off paddy preparation budget, before soil-water credit
    percolation_mm_day: float = 0.0  # percolation + seepage while flooded
    flooded_days: int = 0       # distinct from the sowing-to-harvest season_days
    water_layer_mm: float = 0.0  # establish once; maintenance is in percolation

    @property
    def field_water_need(self):
        """Seasonal field demand before rain/soil/irrigation credits, mm."""
        return (self.water_need + self.saturation_mm
                + self.percolation_mm_day * self.flooded_days + self.water_layer_mm)


# Six revised water needs use the lower end of FAO Manual 3, Table 14;
# rice uses the upper end for the hot southern growing season. These choices
# are model assumptions within published ranges, not Kazakhstan field estimates.
# All keys and crop forms are retained; spring cereals/rapeseed are assumed.
CROPS = {c.key: c for c in [
    Crop("wheat", "Wheat", "cereal", 12, 22, 450, 0.5, 0.30, 0.60, 0.5, season_days=100),
    Crop("barley", "Barley", "cereal", 11, 21, 450, 0.6, 0.30, 0.50, 0.7, season_days=90),
    Crop("oats", "Oats", "cereal", 11, 18, 450, 0.4, 0.40, 0.40, 0.4, season_days=95),
    Crop("millet", "Millet", "cereal", 17, 27, 250, 0.85, 0.40, 0.40, 0.5, season_days=90),
    Crop("maize", "Maize (grain)", "row", 18, 27, 500, 0.3, 0.20, 0.70, 0.3, season_days=130),
    Crop("sunflower", "Sunflower", "oilseed", 15, 24, 600, 0.7, 0.10, 0.75, 0.5, season_days=120),
    Crop("rapeseed", "Rapeseed (canola)", "oilseed", 11, 18, 360, 0.4, 0.50, 0.70, 0.4, season_days=100),
    Crop("flax", "Flax (linseed)", "oilseed", 12, 19, 280, 0.5, 0.40, 0.65, 0.3, season_days=95),
    Crop("peas", "Peas", "legume", 11, 19, 350, 0.4, 0.80, 0.55, 0.3, season_days=90),
    Crop("chickpea", "Chickpea", "legume", 15, 26, 250, 0.8, 0.70, 0.70, 0.4, season_days=100),
    Crop("lentil", "Lentil", "legume", 12, 22, 250, 0.7, 0.75, 0.65, 0.3, season_days=95),
    Crop("soybean", "Soybean", "legume", 18, 25, 450, 0.3, 0.75, 0.70, 0.3, season_days=125),
    Crop("buckwheat", "Buckwheat", "pseudocereal", 13, 20, 300, 0.4, 0.60, 0.50, 0.3, season_days=80),
    Crop("alfalfa", "Alfalfa", "legume", 13, 27, 800, 0.6, 0.95, 0.50, 0.6),
    Crop("cotton", "Cotton", "row", 21, 30, 700, 0.4, 0.10, 0.80, 0.7, season_days=160, irrigated_only=True),
    # FAO Manual 3 §4.4 scenario, not a Kazakhstan irrigation norm. Continuous
    # flooding from sowing until drainage 10 days before harvest (TNAU): 130-10.
    # Soil classes do not identify texture/puddling, so use FAO's mean 6 mm/day.
    Crop("rice", "Rice", "cereal", 21, 30, 700, 0.0, 0.20, 0.70, 0.6,
         season_days=130, irrigated_only=True, saturation_mm=200,
         percolation_mm_day=6, flooded_days=120, water_layer_mm=100),
    Crop("fallow", "Green fallow", "fallow", -50, 50, 0, 1.0, 0.80, 0.00, 1.0),
]}

# Display groups for the rotation timeline.
FAMILY_GROUPS = {
    "cereal": "Cereals",
    "legume": "Legumes",
    "oilseed": "Oilseeds, row and other crops",
    "row": "Oilseeds, row and other crops",
    "pseudocereal": "Oilseeds, row and other crops",
    "fallow": "Fallow / green manure",
}


@dataclass(frozen=True)
class Soil:
    key: str
    name: str
    fertility: float     # 0..1
    water_hold: float    # assumed profile storage, mm; depth unspecified (SOURCES.md)
    note: str = ""
    saline: bool = False


SOILS = {s.key: s for s in [
    Soil("chernozem", "Chernozem (black soil)", 0.9, 160,
         "Very fertile and stores a lot of water. Typical for the northern grain belt."),
    Soil("dark_chestnut", "Dark chestnut", 0.7, 130,
         "Good fertility, dry steppe."),
    Soil("light_chestnut", "Light chestnut / brown", 0.5, 100,
         "Moderate fertility, semi-desert steppe."),
    Soil("sierozem", "Sierozem (grey desert soil)", 0.4, 80,
         "Low in humus, southern foothills. Usually farmed with irrigation."),
    Soil("saline", "Saline soil", 0.3, 70,
         "Salt holds back most crops. Common on old irrigated land.", saline=True),
]}

IRRIGATION_MM = 450  # assumed seasonal field water input; excludes upstream delivery losses
