import json
import numpy as np
import matplotlib.pyplot as plt
import pyproj

from py_wake.literature.gaussian_models import Bastankhah_PorteAgel_2014
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine

# --- Turbine model: SG 8.0-167 DD ---
class SG_80_167_DD(GenericWindTurbine):
    def __init__(self):
        GenericWindTurbine.__init__(self,
            name='SG 8.0 167 DD',
            diameter=167,
            hub_height=119,
            power_norm=8000,
            turbulence_intensity=0.07
        )

# --- Site model: GWA Weibull Distribution ---
class SouthForkGWA(UniformWeibullSite):
    def __init__(self, ti=0.07):
        f = np.array([6.4452, 7.6731, 6.4733, 6.0399, 4.8786, 4.5663,
                      7.3180, 11.7882, 13.8072, 11.7932, 9.7412]) * 0.01
        f = f / f.sum()

        a = np.array([10.26, 10.44, 9.52, 8.96, 9.58, 9.72,
                      11.48, 12.38, 12.77, 11.86, 11.13])

        k = np.array([2.225, 2.697, 1.877, 1.899, 2.123, 1.755,
                      2.401, 2.366, 2.186, 2.385, 2.404])

        UniformWeibullSite.__init__(self, f, a, k, ti=ti)

# --- Load GeoJSON Data ---
with open("SouthForkpoint.geojson") as f:
    turbines_geojson = json.load(f)
with open("SouthForkpolygon.geojson") as f:
    boundary_geojson = json.load(f)

turbines_lonlat = [feat["geometry"]["coordinates"] for feat in turbines_geojson["features"]
                   if feat["geometry"]["type"] == "Point"]
boundary_lonlat = next(
    feat["geometry"]["coordinates"][0]
    for feat in boundary_geojson["features"]
    if feat["geometry"]["type"] == "Polygon"
)

# --- Convert coordinates to UTM Zone 19N ---
project = pyproj.Transformer.from_crs("EPSG:4326", "+proj=utm +zone=19 +datum=WGS84", always_xy=True).transform
utm_turbines = np.array([project(lon, lat) for lon, lat in turbines_lonlat])
utm_boundary = np.array([project(lon, lat) for lon, lat in boundary_lonlat])
x, y = utm_turbines[:, 0], utm_turbines[:, 1]

# --- Run Wake Simulation ---
site = SouthForkGWA()
turbine = SG_80_167_DD()
wake_model = Bastankhah_PorteAgel_2014(site, turbine, k=0.04)

wd = np.arange(0, 360, 30)[:11]
sim_res = wake_model(x, y, wd=wd)
aep = sim_res.aep().sum()

# --- Print AEP ---
print(f" Total AEP for South Fork Wind: {aep:.2f} GWh/year")

# --- Plot Wind Farm Layout with AEP ---
plt.figure(figsize=(10, 8))
plt.plot(utm_boundary[:, 0], utm_boundary[:, 1], 'b-', label="Boundary")
plt.scatter(x, y, color='purple', label="Turbines", zorder=5)
plt.title(f"South Fork Wind Farm Layout\nTotal AEP: {aep:.2f} GWh/year")
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
