import DrawDownAnalysis as dda

def main():
    # Parameters
    multiplier = 2            # Discharge function multiplier
    diam = 36/12              # Outlet diameter (ft)
    loss_factor = 3           # Equivalent loss factor
    initial_elev = 2224       # Starting elevation (max certified pool)
    initial_head = 85         # Initial head (MPWSE - El. at D/S outlet)
    target_elev = 2209.6      # Final/target drawdown elevation

    # Area Capacity Curves
    area     = r"./area-capacity-curve/elev-area-curve-1977.csv"
    capacity = r"./area-capacity-curve/elev-storage-curve-1977.csv"

    # Analysis
    Analysis = dda.DrawDownAnalysis(dt=1, n_steps=1100)
    Analysis.assignOutletParams(multiplier, diam, loss_factor)
    Analysis.assignResevoirParams(initial_elev, initial_head)
    Analysis.assignAreaCapacityCurves(area, capacity)
    Analysis.assignDrawDownTargetElev(target_elev, note="10% resevoir head in 7 days")
    Analysis.runDrawdownAnalysis()
    Analysis.summarize()
    Analysis.saveResultsToCSV()
    Analysis.sensitivityAnalysis()

if __name__ == '__main__':
    main()