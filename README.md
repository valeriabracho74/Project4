# Project_4 – Wind Farm AEP Simulation and Optimization

This repository contains all code and data used for Project 4 in ENGIN 480, which involves simulating and optimizing the Annual Energy Production (AEP) of offshore wind farms using PyWake and TopFarm.

## 📁 Project Structure

- Python scripts for AEP simulation (`.py`)
- TopFarm optimization scripts for each wind farm
- `.geojson` files for layout and boundaries (from SeaImpact)
- `.lib` files from Global Wind Atlas for wind speed and direction
- Output folders (e.g., `_TopFarm_out`) with convergence data and plots

## 🌬️ Wind Farms Included

1. **Vineyard Wind**
2. **Revolution SouthFork Wind**
3. **Coastal Virginia Offshore Wind**
4. **Yunlin Wind**

## ⚙️ Tools and Libraries

- Python 3.11 (via Anaconda)
- [PyWake](https://github.com/TopFarm/PyWake)
- [TopFarm](https://github.com/TopFarm/TopFarm2)
- NumPy, matplotlib, pyproj
- VSCode + GitHub for version control

## 🌀 Simulation Workflow (Delivery 1)

1. Load turbine layout and boundary from `.geojson`
2. Convert coordinates to UTM
3. Parse Weibull distribution values from `.lib`
4. Simulate AEP using PyWake
5. Plot layout with AEP result

## 🔧 Optimization Workflow (Delivery 2)

1. Use same wind farm data and site model
2. Treat turbine (x, y) as design variables
3. Optimize AEP with TopFarm (using spacing and boundary constraints)
4. Track results with `TopFarmListRecorder`
5. Plot convergence and optimized layout

## 📌 Notes

- Each wind farm has its own standalone simulation and optimization script.
- All simulations use the SG 8.0-167 DD turbine and the Bastankhah wake model.
- This repo is organized to make each part reusable, testable, and modular.
