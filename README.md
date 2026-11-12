# Field Shift KZ

Crop rotation decision support for Kazakhstan farms, built on NASA Earth observations.
NASA Space Apps Challenge 2026: *Field Shift: Adapting Farms with NASA Data*. Team DDT, Almaty.

**Live demo:** https://stalker-a-field-shift-kz-app-xokyoc.streamlit.app/

The farmer picks a region or coordinates, a soil type, a priority and the rotation they grow now. The app answers in four tabs:

1. **Climate shift.** The field in 2006–2025 against 1981–2000: growing-season temperature, rainfall, root-zone soil wetness, water deficit, frost-free season, last spring frost, hot days and the longest dry spell. Year-by-year and month-by-month charts show where the change comes from.
2. **Crop fit.** How well 16 crops fit the field now and in 2035, and which factor holds each one back: temperature, water, season length or soil salinity. The 2035 climate extends the observed trend; it is not a climate model.
3. **Rotation plan.** Three four-year rotations that follow basic agronomy rules, scored on soil health, water saving, income and climate resilience, each compared with the current rotation and explained in plain words.
4. **Data & method.** The NASA parameters used, how every score is computed, the limits of the tool, and the data as CSV.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Check on real data: `python tests/check_regions.py`

## Data

- **NASA POWER** daily point API (`community=AG`), 1981–2025, no key needed: `T2M`, `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`, `GWETROOT`.
- Reference evapotranspiration is computed from the daily temperatures with the Hargreaves method (FAO-56).
- The derived monthly and yearly tables are cached in `.cache/`. The twelve preset regions ship with the repository, so the demo works offline.
- Crop and soil parameters in `fieldshift/crops.py` are approximate prototype values.

## Code

| File | What |
|---|---|
| `fieldshift/nasa_power.py` | NASA POWER daily download |
| `fieldshift/dataset.py` | per-point tables and the disk cache |
| `fieldshift/climate.py` | monthly and yearly indicators, climate shift, trend profile |
| `fieldshift/crops.py` | crop and soil parameters |
| `fieldshift/rotation.py` | crop fit, rotation rules, scoring, search |
| `fieldshift/charts.py` | Plotly figures and the color palette |
| `fieldshift/regions.py` | preset farming regions |
| `app.py` | Streamlit UI |
| `.streamlit/config.toml` | dark theme |
