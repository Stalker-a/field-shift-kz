# Field Shift KZ

Crop rotation decision support for Kazakhstan farms, built on NASA Earth observations.
NASA Space Apps Challenge 2026: *Field Shift: Adapting Farms with NASA Data*. Team DDT, Almaty.

**Live demo:** https://stalker-a-field-shift-kz-app-xokyoc.streamlit.app/

1. **How your field's climate has shifted.** Growing-season temperature, rainfall and root-zone soil wetness, 1981–2000 compared with the last 20 years.
2. **Which crops fit now and in 2035.** Suitability by temperature, water and soil. The 2035 climate extends the observed trend; it is not a climate model.
3. **Recommended rotations.** Four-year rotations that follow basic agronomy rules, scored on soil health, water saving, income and climate resilience. The farmer sets the weights, and each option is compared with the current rotation.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Check on real data: `python tests/check_regions.py`

## Data

- **NASA POWER** monthly point API (`community=AG`), no key needed: `T2M`, `PRECTOTCORR`, `GWETROOT`. Responses are cached in `.cache/`.
- Crop and soil parameters in `fieldshift/crops.py` are approximate prototype values.

## Code

| File | What |
|---|---|
| `fieldshift/nasa_power.py` | NASA POWER download + cache |
| `fieldshift/climate.py` | yearly indicators, climate shift, trend profile |
| `fieldshift/crops.py` | crop and soil parameters |
| `fieldshift/rotation.py` | suitability, rotation rules, scoring, search |
| `fieldshift/regions.py` | preset farming regions |
| `app.py` | Streamlit UI |
