# Streamlit Community Cloud deployment

The existing production app is
[Field Shift KZ](https://stalker-a-field-shift-kz-app-xokyoc.streamlit.app/).
It follows `main` in `Stalker-a/field-shift-kz`, entry point `app.py`.
Follow the workflow in `TZ.md`: feature branch → pull request → leader review
and merge. A feature PR does not change the production app until merged.

## Reproduce the environment

Python 3.11 is the locally verified runtime. `requirements.txt` pins the tested
direct dependencies, including Streamlit's stateful tabs and the Folium component.
Use Python 3.11 when creating a new Cloud deployment. Do not delete or recreate
the existing app just to change Python; check its current settings first.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python tests/check_regions.py
python tests/check_ui.py
streamlit run app.py
```

No API keys, secrets file, paid map account or system packages are required.
The `.streamlit/config.toml` dark theme is included in the repository. Streamlit
handles its host/port on Community Cloud; no local port is committed to config.

## Verify a release

1. Both Python checks must pass. Check the final diff before opening the PR.
2. Open the app and select Kostanay, then an irrigated southern region. Check
   the field summary, crop fit and rotation recommendations.
3. Open **Choose on map**, zoom/pan, and click a point. Coordinates should
   appear without changing the active field. **Use selected point** applies
   it and then loads NASA data. Outside 40–56°N / 46–88°E, applying is disabled.
4. Switch to **Custom coordinates** and submit both coordinates with **Apply
   coordinates**. Manual entry remains available if map tiles cannot load.
5. Use **Compare rotations**; change the priority and check that the selected
   tab remains active. `?tab=climate|crops|rotation|method` also opens a tab directly.
6. Download the field summary and check field coordinates, soil, irrigation,
   weights, current rotation, available options, explanations and limitations.
7. Check a narrow mobile viewport: sidebar access, map dialog and tab navigation.
8. After leader merge, Community Cloud normally rebuilds from `main`. Check
   build logs if needed, and repeat the UI smoke check at the production URL.
   Verify the new **Choose on map** and **Download field summary** controls.

## Network and recovery

All 12 preset regions ship with `.cache` monthly/yearly tables. Their analysis
works offline; map tiles and map JavaScript/CSS still need internet access.
Custom points require NASA POWER on first use. NASA data are rounded to 0.01°
by the existing loader and describe an area, not a field boundary. The supported
rectangle is a coordinate guard, not a Kazakhstan border polygon.

If NASA is unavailable, the UI offers **Try again** and **Use Kostanay demo**,
and keeps connection details in an expander. The cache is optional on hosts
with a read-only filesystem. A sleeping Community Cloud app can be woken with
its normal **Yes, get this app back up!** button; this does not deploy new code.

The map uses OpenStreetMap tiles with attribution. `streamlit-folium`
is loaded only when its dialog opens. It returns only `last_clicked`, so panning
and zooming do not trigger NASA requests. Map confirmation keeps existing soil,
irrigation, priorities and rotation settings.

References: [Community Cloud dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies),
[deployment settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy),
[streamlit-folium](https://github.com/randyzwitch/streamlit-folium).
