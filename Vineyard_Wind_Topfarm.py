import numpy as np
import matplotlib.pyplot as plt
import json
import pyproj

from topfarm.cost_models.cost_model_wrappers import CostModelComponent
from topfarm import TopFarmProblem
from topfarm.plotting import XYPlotComp
from topfarm.constraint_components.boundary import XYBoundaryConstraint
from topfarm.constraint_components.spacing import SpacingConstraint
from topfarm.easy_drivers import EasyScipyOptimizeDriver
from topfarm.recorders import TopFarmListRecorder

from py_wake.literature.gaussian_models import Bastankhah_PorteAgel_2014
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine

# --- Load GeoJSON Data ---
with open("Vineyardwind_point.geojson") as f:
    turbines_geojson = json.load(f)

with open("Vineyardwind_boundary.geojson") as f:
    boundary_geojson = json.load(f)

turbines_lonlat = [feat["geometry"]["coordinates"] for feat in turbines_geojson["features"]
                   if feat["geometry"]["type"] == "Point"]

boundary_lonlat = next(
    feat["geometry"]["coordinates"][0]
    for feat in boundary_geojson["features"]
    if feat["geometry"]["type"] == "Polygon"
)

# --- Convert to UTM Zone 19N ---
project = pyproj.Transformer.from_crs("EPSG:4326", "+proj=utm +zone=19 +datum=WGS84", always_xy=True).transform
utm_turbines = np.array([project(lon, lat) for lon, lat in turbines_lonlat])
utm_boundary = np.array([project(lon, lat) for lon, lat in boundary_lonlat])
boundary_closed = np.vstack([utm_boundary, utm_boundary[0]])

xinit, yinit = utm_turbines[:, 0], utm_turbines[:, 1]
n_wt = len(xinit)

# --- Turbine Model ---
class SG_80_167_DD(GenericWindTurbine):
    def __init__(self):
        GenericWindTurbine.__init__(self,
            name='SG 8.0 167 DD',
            diameter=167,
            hub_height=119,
            power_norm=8000,
            turbulence_intensity=0.07
        )

# --- Site from GWA .lib values ---
class VineyardGWA(UniformWeibullSite):
    def __init__(self, ti=0.07):
        f = np.array([1] * 12)
        f = f / f.sum()
        a = np.array([10.26, 10.44, 9.52, 8.96, 9.58, 9.72,
                      11.48, 13.25, 12.46, 11.40, 12.35, 10.48])
        k = np.array([2.225, 1.697, 1.721, 1.689, 1.525, 1.498,
                      1.686, 2.143, 2.369, 2.186, 2.385, 2.404])
        UniformWeibullSite.__init__(self, f, a, k, ti=ti)

site = VineyardGWA()
wind_turbines = SG_80_167_DD()
wake_model = Bastankhah_PorteAgel_2014(site, wind_turbines, k=0.04)

# --- Objective Function with fixed wind directions ---
def aep_func(x, y):
    return wake_model(x, y, wd=np.arange(0, 360, 30)[:12]).aep().sum()

# --- Recorder ---
recorder = TopFarmListRecorder(None, ['AEP', 'x', 'y'])

# --- TopFarm Problem ---
problem = TopFarmProblem(
    design_vars={'x': xinit, 'y': yinit},
    cost_comp=CostModelComponent(
        input_keys=['x', 'y'],
        n_wt=n_wt,
        cost_function=aep_func,
        maximize=True,
        output_keys=[('AEP', 0)]
    ),
    constraints=[
        XYBoundaryConstraint(boundary_closed),
        SpacingConstraint(min_spacing=334)
    ],
    driver=EasyScipyOptimizeDriver(optimizer='SLSQP', maxiter=100, tol=1e-6),
    n_wt=n_wt,
    plot_comp=XYPlotComp(),
    recorder=recorder
)

# --- Run Optimization ---
cost, state, recorder = problem.optimize()

# --- Output Results ---
print("\nAEP over iterations:")
for i, aep in enumerate(recorder["AEP"]):
    print(f"Iteration {i + 1}: {aep:.2f} GWh")

print(f"\nFinal Optimized AEP for Vineyard Wind (GWA): {-cost:.2f} GWh/year")

# --- AEP Convergence Plot ---
plt.figure()
plt.plot(recorder['counter'], np.array(recorder['AEP']) / recorder['AEP'][-1], marker='o')
plt.xlabel('Iterations')
plt.ylabel('AEP / AEP_opt')
plt.title('AEP Convergence - Vineyard Wind (GWA)')
plt.grid(True)
plt.tight_layout()
plt.show()
print("done")
