"""
Preprocess South Tyrol glacier shapefiles into slim outputs for the dashboard.

Reads three raw shapefile folders, produces:
  - data/south_tyrol/processed/glaciers_1997.geojson
  - data/south_tyrol/processed/glaciers_2005.geojson
  - data/south_tyrol/processed/glaciers_2017.geojson
  - data/south_tyrol/processed/glaciers_change.geojson
  - data/south_tyrol/processed/aggregate_stats.csv
  - data/south_tyrol/processed/regional_change.csv

Run once from the repo root:
    python src/preprocess_south_tyrol.py
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Paths — adjust RAW_DIR if you move the shapefiles into the repo later
# ---------------------------------------------------------------------------
RAW_DIR = Path(r"C:\My files\Unitn 1st year DS\Data Viz\Data shp")
OUT_DIR = Path("data/south_tyrol/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    1997: RAW_DIR / "SGIhom_1997" / "SGIhom_1997.shp",
    2005: RAW_DIR / "SGIhom_2005" / "SGIhom_2005.shp",
    2017: RAW_DIR / "SGIhom_2017" / "SGIhom_2017.shp",
}

AREA_COL = {1997: "AREA_97", 2005: "AREA_05", 2017: "AREA_17"}

# ---------------------------------------------------------------------------
# 1. Load and clean
# ---------------------------------------------------------------------------
def load_year(year: int) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(FILES[year])

    # Replace -9999 placeholders with NaN in numeric and string columns
    num_cols = ["ALT_MIN", "ALT_MAX", "ALT_MEAN", "ALT_MEDIAN",
                "SLOPE_MEAN", "ASPECT_AZM"]
    for c in num_cols:
        if c in gdf.columns:
            gdf[c] = gdf[c].replace(-9999, np.nan)
    for c in ["CGI_ID", "WGMS_ID", "NAME_D", "NAME_IT"]:
        if c in gdf.columns:
            gdf[c] = gdf[c].replace(["-9999", "", "None"], np.nan)
    
    # Fix known region name typos
    REGION_FIXES = {
        "Ortergruppe": "Ortlergruppe",
    }
    if "REGION" in gdf.columns:
        gdf["REGION"] = gdf["REGION"].replace(REGION_FIXES)

    return gdf

print("Loading shapefiles...")
gdfs = {yr: load_year(yr) for yr in FILES}
for yr, gdf in gdfs.items():
    print(f"  {yr}: {len(gdf)} parts, "
          f"total area = {gdf[AREA_COL[yr]].sum():.2f} km²")

# ---------------------------------------------------------------------------
# 2. Per-year GeoJSONs for the map (simplified geometry, slim attributes)
# ---------------------------------------------------------------------------
KEEP_COLS = ["HOM_ID", "NAME_D", "NAME_IT", "REGION",
             "ALT_MIN", "ALT_MAX", "ALT_MEDIAN"]

# Simplify in the metric CRS, then reproject to WGS84 for web display
SIMPLIFY_TOL_M = 20   # meters; raise to 50 for even smaller files

for yr, gdf in gdfs.items():
    area_col = AREA_COL[yr]
    slim = gdf[KEEP_COLS + [area_col, "geometry"]].copy()
    slim = slim.rename(columns={area_col: "area_km2"})
    slim["geometry"] = slim.geometry.simplify(SIMPLIFY_TOL_M,
                                              preserve_topology=True)
    slim = slim.to_crs("EPSG:4326")

    out = OUT_DIR / f"glaciers_{yr}.geojson"
    slim.to_file(out, driver="GeoJSON")
    print(f"  wrote {out}  ({out.stat().st_size / 1024:.0f} KB)")

# ---------------------------------------------------------------------------
# 3. Per-glacier change layer (HOM_ID level, geometry from 1997 = max extent)
# ---------------------------------------------------------------------------
def aggregate_by_glacier(gdf, area_col):
    return gdf.groupby("HOM_ID").agg(
        area=(area_col, "sum"),
        n_parts=(area_col, "size"),
        region=("REGION", "first"),
        name_d=("NAME_D", "first"),
        name_it=("NAME_IT", "first"),
    )

agg = {yr: aggregate_by_glacier(gdfs[yr], AREA_COL[yr]) for yr in gdfs}

# Merge 1997 with 2005 and 2017 areas
change = agg[1997][["area", "region", "name_d", "name_it"]].rename(
    columns={"area": "area_97"})
change = change.join(agg[2005]["area"].rename("area_05"), how="left")
change = change.join(agg[2017]["area"].rename("area_17"), how="left")

# % change 1997 → 2017. Glaciers that disappeared get -100%.
change["change_pct"] = np.where(
    change["area_17"].notna(),
    (change["area_17"] - change["area_97"]) / change["area_97"] * 100,
    -100.0,
)
change["status"] = np.where(change["area_17"].notna(), "present", "disappeared")

# Attach 1997 geometry, dissolved by HOM_ID so each glacier is one shape
geom_97 = gdfs[1997].dissolve(by="HOM_ID")[["geometry"]]
change_gdf = geom_97.join(change, how="inner")
change_gdf = gpd.GeoDataFrame(change_gdf, geometry="geometry",
                              crs=gdfs[1997].crs)
change_gdf["geometry"] = change_gdf.geometry.simplify(
    SIMPLIFY_TOL_M, preserve_topology=True)
change_gdf = change_gdf.to_crs("EPSG:4326")
change_gdf = change_gdf.reset_index()   # HOM_ID becomes a column

out = OUT_DIR / "glaciers_change.geojson"
change_gdf.to_file(out, driver="GeoJSON")
print(f"  wrote {out}  ({out.stat().st_size / 1024:.0f} KB)")

# ---------------------------------------------------------------------------
# 4. Aggregate stats CSV (3 rows × ~4 cols)
# ---------------------------------------------------------------------------
agg_stats = pd.DataFrame({
    "year":         list(gdfs.keys()),
    "total_area":   [gdfs[yr][AREA_COL[yr]].sum() for yr in gdfs],
    "n_parts":      [len(gdfs[yr]) for yr in gdfs],
    "n_glaciers":   [gdfs[yr]["HOM_ID"].nunique() for yr in gdfs],
    "avg_size":     [gdfs[yr][AREA_COL[yr]].mean() for yr in gdfs],
})
agg_stats = agg_stats.round(3)
agg_stats.to_csv(OUT_DIR / "aggregate_stats.csv", index=False)
print(f"  wrote {OUT_DIR / 'aggregate_stats.csv'}")
print(agg_stats)

# ---------------------------------------------------------------------------
# 5. Regional change CSV
# ---------------------------------------------------------------------------
# Build a region list that includes every region ever recorded across years
all_regions = set()
for yr in gdfs:
    all_regions.update(gdfs[yr]["REGION"].unique())

region_area = pd.DataFrame(index=sorted(all_regions))
for yr in gdfs:
    sums = gdfs[yr].groupby("REGION")[AREA_COL[yr]].sum()
    region_area[f"area_{str(yr)[-2:]}"] = sums

# Regions absent in a given year → 0 km² (genuinely disappeared, not missing)
region_area = region_area.fillna(0)

# Now compute percent changes. Avoid divide-by-zero by handling area_97 == 0.
def pct_change(start, end):
    return ((end - start) / start * 100).where(start > 0, other=None)

region_area["change_pct_97_17"] = pct_change(
    region_area["area_97"], region_area["area_17"])
region_area["change_pct_97_05"] = pct_change(
    region_area["area_97"], region_area["area_05"])
region_area["change_pct_05_17"] = pct_change(
    region_area["area_05"], region_area["area_17"])

region_area = region_area.round(2).reset_index().rename(columns={"index": "REGION"})
region_area.to_csv(OUT_DIR / "regional_change.csv", index=False)
print(f"  wrote {OUT_DIR / 'regional_change.csv'}")
print(region_area)