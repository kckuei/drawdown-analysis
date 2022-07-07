# Drawdown Analysis

A simple class implementation for performing drawdown analysis of dam outlet works using area capacity curves and discharge functions.

## Implementation Notes

* Based on USBR's [Design of Small Dams](https://www.usbr.gov/tsc/techreferences/mands/mands-pdfs/SmallDams.pdf) (1987), Chapter 10, Section 10.14 Pressure Flow in Outlet Conduits
* This implementation uses the `diameter` (or `area`) and equivalent loss coefficient (`K_eq`) to characterize the drawdown function/discharge of a single outlet
* The key discharge/drawdown function is give by **Section 10, Eq. 8**, where, $Q$ is the discharge, $K_{eq}$ is the equivalent loss coefficient, $A$ is the outlet area, $g$ is the gravitational constant, and $H_T$ is the total head measured from the resevoir pool to the centerline of the outlet: 
$
\begin{align}
    Q=A\sqrt{\frac{2\cdot g\cdot H_T}{K_{eq}}}
\end{align}
$
* A multiplier (`N_mult`) is provided to scale the discharge for additional outlets (e.g., use `N_mult=2` for two identically sized outlets)

## Assumptions and Inputs

* Full Conduit (Pressure) Flow (Section 10 applicable)
* Minimum parameters required are the outlet diameter `diam`, equivalent loss coefficient `K_eq`, starting elevation `elev_o`, initial head `H_o`, and target drawdown elevation `elev_drawdown` 
* The area capacity curves must also be provided as input, either in the form of csv files, or pandas tables
* The equivalent loss coefficient should be determined through characterization/analysis of the outlet works by diagramming/developing a loss model.
  
![Loss Model Example][loss-model]

## Example Usage

The code below is a example snippet of the class usage. A more detailed notebook example is included. 

```
import DrawDownAnalysis as da

# Parameters
N_mult = 1                # Discharge function multiplier
diam = 36/12              # Outlet diameter (ft)
K_eq = 3                  # Equivalent loss factor
elev_o = 2224             # Starting elevation (max certified pool)
H_o = 85                  # Initial head (MPWSE - El. at D/S outlet)
elev_drawdown = 2209.6    # Final/target drawdown elevation

# Area Capacity Curves
path_area = r"./area-capacity-curve/elev-area-curve-1977.csv"
path_cap = r"./area-capacity-curve/elev-storage-curve-1977.csv"

# Analysis
Analysis = da.DrawDownAnalysis(dt=1, n_steps=1100)
Analysis.assignOutletParams(N_mult, diam, K_eq)
Analysis.assignResevoirParams(elev_o, H_o)
Analysis.assignAreaCapacityCurves(path_area, path_cap)
Analysis.assignDrawDownTargetElev(elev_drawdown, note="10% resevoir head in 7 days")
Analysis.runDrawdownAnalysis()
Analysis.summarize()
Analysis.saveResultsToCSV()
Analysis.sensitivityAnalysis()
print("Analysis successful.")
```


[loss-model]: assets/loss-model.png