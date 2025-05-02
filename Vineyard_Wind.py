import json
import numpy as np
import matplotlib.pyplot as plt
import pyproj

from py_wake.literature.gaussian_models import Bastankhah_PorteAgel_2014
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine

# --- SG 8.0-167 DD Turbine ---
class SG_80_167_DD(GenericWindTurbine):
    def __init__(self):
        GenericWindTurbine.__init__(self,
            name='SG 8.0 167 DD',
            diameter=167,
            hub_height=119,
            power_norm=8000,
            turbulence_intensity=0.07
        )

# --- Weibull Site using Vineyard .lib data ---
class VineyardGWA(UniformWeibullSite):
    def __init__(self, ti=0.07):
        f = np.array([1]*12)
        f = f / f.sum()  # normalize

        a = np.array([10.26, 10.44, 9.52, 8.96, 9.58, 9.72,
                      11.48, 13.25, 12.46, 11.40, 12.35, 10.48])

        k = np.array([2.225, 1.697, 1.721, 1.689, 1.525, 1.498,
                      1.686, 2.143, 2.369, 2.186, 2.385, 2.404])

        UniformWeibullSite.__init__(self, f, a, k, ti=ti)

# --- Load GeoJSON ---
with open("Vineyardwind_point.geojson") as f:
    turbines_geojson = json.load(f)
with open("Vineyardwind_boundary.geojson") as f:
    boundary_geojson = json.load(f)

# Extract points
turbines_lonlat = [feat["geometry"]["coordinates"]
                   for feat in turbines_geojson["features"]
                   if feat["geometry"]["type"] == "Point"]

boundary_lonlat = next(
    feat["geometry"]["coordinates"][0]
    for feat in boundary_geojson["features"]
    if feat["geometry"]["type"] == "Polygon"
)

# Convert to UTM Zone 19N
project = pyproj.Transformer.from_crs("EPSG:4326", "+proj=utm +zone=19 +datum=WGS84", always_xy=True).transform
utm_turbines = np.array([project(lon, lat) for lon, lat in turbines_lonlat])
utm_boundary = np.array([project(lon, lat) for lon, lat in boundary_lonlat])

x, y = utm_turbines[:, 0], utm_turbines[:, 1]

# --- Simulate AEP ---
site = VineyardGWA()
turbine = SG_80_167_DD()
wake_model = Bastankhah_PorteAgel_2014(site, turbine, k=0.04)

wd = np.arange(0, 360, 30)[:12]  # 12 bins
sim_res = wake_model(x, y, wd=wd)
aep = sim_res.aep().sum()

# --- Print and Plot ---
print(f" Total AEP for Vineyard Wind (GWA): {aep:.2f} GWh/year")

plt.figure(figsize=(10, 8))
plt.plot(utm_boundary[:, 0], utm_boundary[:, 1], 'b-', label='Boundary')
plt.scatter(x, y, color='green', label='Turbines', zorder=5)
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.title(f"Vineyard Wind Farm Layout\nTotal AEP: {aep:.2f} GWh/year")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
