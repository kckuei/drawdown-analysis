 # 
 ```
    ___                       _                         _               _           _     
   /   \_ __ __ ___      ____| | _____      ___ __     /_\  _ __   __ _| |_   _ ___(_)___ 
  / /\ / '__/ _` \ \ /\ / / _` |/ _ \ \ /\ / / '_ \   //_\\| '_ \ / _` | | | | / __| / __|
 / /_//| | | (_| |\ V  V / (_| | (_) \ V  V /| | | | /  _  \ | | | (_| | | |_| \__ \ \__ \
/___,' |_|  \__,_| \_/\_/ \__,_|\___/ \_/\_/ |_| |_| \_/ \_/_| |_|\__,_|_|\__, |___/_|___/
                                                                          |___/           
```


Simple class implementation for performing drawdown analysis of dam outlet works using area capacity curves and discharge functions.

## Implementation Notes

* Based on USBR's [Design of Small Dams](https://www.usbr.gov/tsc/techreferences/mands/mands-pdfs/SmallDams.pdf) (1987), Chapter 10, Section 10.14 Pressure Flow in Outlet Conduits.
* This implementation uses the `diameter` (or `area`) and equivalent loss coefficient (`K_eq`) to characterize the drawdown function/discharge of a single outlet.
* The key discharge (drawdown) function is give by **Section 10, Eq. 8**, where, $Q$ is the discharge, $K_{eq}$ is the equivalent loss coefficient, $A$ is the outlet area, $g$ is the gravitational constant, and $H_T$ is the total head measured from the resevoir pool to the centerline of the outlet: 
$$Q=A\sqrt{\frac{2\cdot g\cdot H_T}{K_{eq}}}$$
* A multiplier (`N_mult`) is provided to scale the discharge for additional outlets (e.g., use `N_mult=2` for two identically sized outlets)

## Assumptions and Inputs

* Full conduit (pressure) flow applicable (section 10)
* Assumes _n_ identically sized outlets
* Minimum parameters required are the outlet diameter `diam`, equivalent loss coefficient `K_eq`, starting elevation `elev_o`, initial head `H_o`, and target drawdown elevation `elev_drawdown` 
* The area capacity curves must also be provided as input, either in the form of csv files, or pandas tables
* The loss coefficient should be determined through characterization of the outlet works by developing a loss model. An example is shown below.
  
![Loss Model Example][loss-model]
![Loss Table Example][loss-table]

## Example Usage

Example usage provided below. A more detailed notebook example is included with the repo.

```python
import DrawDownAnalysis as da

# Parameters
multiplier = 1            # Discharge function multiplier
diam = 36/12              # Outlet diameter (ft)
loss_factor = 3           # Equivalent loss factor
initial_elev = 2224       # Starting elevation (max certified pool)
initial_head = 85         # Initial head (MPWSE - El. at D/S outlet)
target_elev = 2209.6      # Final/target drawdown elevation

# Area Capacity Curves
area     = r"./area-capacity-curve/elev-area-curve-1977.csv"
capacity = r"./area-capacity-curve/elev-storage-curve-1977.csv"

# Analysis
Analysis = da.DrawDownAnalysis(dt=1, n_steps=1100)
Analysis.assignOutletParams(multiplier, diam, loss_factor)
Analysis.assignResevoirParams(initial_elev, initial_head)
Analysis.assignAreaCapacityCurves(area, capacity)
Analysis.assignDrawDownTargetElev(target_elev, note="10% resevoir head in 7 days")
Analysis.runDrawdownAnalysis()
Analysis.summarize()
Analysis.saveResultsToCSV()
Analysis.sensitivityAnalysis()
```

## To Do / Future Updates

* Unit system
* Outlet table implementation for distinct outlet configurations
* Command line implementation
* Excel output for printing to files

## Credit

* [text to ascii art generator](https://patorjk.com/software/taag/#p=display&f=Ogre&t=Drawdown%20Analysis)


[loss-model]: assets/loss-model.png
[loss-table]: assets/loss-table.png
