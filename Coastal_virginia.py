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

# --- Site Model Using GWA Weibull Inputs ---
class CoastalVirginiaGWA(UniformWeibullSite):
    def __init__(self, ti=0.07):
        f = np.array([1]*12)
        f = f / f.sum()
        a = np.array([10.87, 10.29, 8.68, 7.59, 7.55, 8.86,
                      11.16, 13.27, 13.81, 12.40, 11.94, 11.82])
        k = np.array([2.260, 2.166, 1.955, 1.627, 1.627, 1.936,
                      2.029, 2.256, 2.557, 2.393, 2.475, 2.650])
        UniformWeibullSite.__init__(self, f, a, k, ti=ti)

# --- Load GeoJSON Files ---
with open("Coastal_Virginia_point.geojson") as f:
    turbines_geojson = json.load(f)
with open("Coastal_Virginia_polygon.geojson") as f:
    boundary_geojson = json.load(f)

# Extract turbine and boundary coordinates
turbines_lonlat = [feat["geometry"]["coordinates"]
                   for feat in turbines_geojson["features"]
                   if feat["geometry"]["type"] == "Point"]

boundary_lonlat = next(
    feat["geometry"]["coordinates"][0]
    for feat in boundary_geojson["features"]
    if feat["geometry"]["type"] == "Polygon"
)

# Convert to UTM Zone 18N
project = pyproj.Transformer.from_crs("EPSG:4326", "+proj=utm +zone=18 +datum=WGS84", always_xy=True).transform
utm_turbines = np.array([project(lon, lat) for lon, lat in turbines_lonlat])
utm_boundary = np.array([project(lon, lat) for lon, lat in boundary_lonlat])

x, y = utm_turbines[:, 0], utm_turbines[:, 1]

# --- Simulate AEP ---
site = CoastalVirginiaGWA()
turbine = SG_80_167_DD()
wake_model = Bastankhah_PorteAgel_2014(site, turbine, k=0.04)

wd = np.arange(0, 360, 30)[:12]
sim_res = wake_model(x, y, wd=wd)
aep = sim_res.aep().sum()

# --- Print AEP ---
print(f" Total AEP for Coastal Virginia Wind (GWA): {aep:.2f} GWh/year")

# --- Plot Layout ---
plt.figure(figsize=(10, 8))
plt.plot(utm_boundary[:, 0], utm_boundary[:, 1], 'b-', label="Boundary")
plt.scatter(x, y, color='darkorange', label="Turbines", zorder=5)
plt.title(f"Coastal Virginia Wind Layout\nTotal AEP: {aep:.2f} GWh/year")
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
