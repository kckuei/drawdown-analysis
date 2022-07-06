import DrawDownAnalysis as dda

def main():
    # outlet parameters
    N_mult = 2                # Two (2) low-level outlets
    diam = 36/12              # 36" diameter outlets
    L1 = 35                   # Length of steel portion of outlet
    L2 = 15                   # Lenth of iron portion of outlet
    n1 = 0.012                # Manning's roughness coefficient for steel (max)
    n2 = 0.061                # Manning's roughness coefficient for ductile iron (typ)

    radius_h = diam/4                              # Hydraulic radius = area/(wetted perimeter)
    K_f1 = 29.1*(n1**2)*(L1/(radius_h**(4/3)))     # Loss due to pipe friction in steel
    K_f2 = 29.1*(n2**2)*(L2/(radius_h**(4/3)))     # Loss due to pipe friction in ductile iron
    K_f = K_f1 + K_f2                              # Total loss

    area_ratio = 0.62                              # Ratio of net through area to new trashrack area
    K_t = 1.45-0.45*(area_ratio)-(area_ratio)**2   # Loss due to trash rack
    K_e = 0.23                                     # Loss due to entrance
    K_gv = 0.10 + 0.10                             # Loss due to 2 gate valves (US + DS exit)
    K_b90 = 1.0                                    # Loss due to vertical 33-deg bend

    K_eq = K_f + K_t + K_e + K_gv + K_b90     # Equivalent loss coefficient

    # resevoir parameters
    elev_o = 2224              # Starting elevation (max certified pool)
    H_o = 85                   # Initial head (max certified pool - elevation at downstream outlet)
    elev_drawdown = 2209.6     # final drawdown elevation to satisfy Division requirements (just for plotting, and table query)

    # area/capacity curves
    path_area = r"./area-capacity-curve/elev-area-curve-1977.csv"
    path_cap = r"./area-capacity-curve/elev-storage-curve-1977.csv"

    # Run analysis
    Analysis = dda.DrawDownAnalysis(dt=1, n_steps=1100)
    Analysis.assignOutletParams(N_mult, diam, K_eq)
    Analysis.assignResevoirParams(elev_o, H_o)
    Analysis.assignAreaCapacityCurves(path_area, path_cap)
    Analysis.assignDrawDownTargetElev(elev_drawdown, note="10% resevoir head in 7 days")
    Analysis.runDrawdownAnalysis()
    Analysis.summarize(elev_drawdown)
    Analysis.saveResultsToCSV()
    Analysis.sensitivityAnalysis(elev_drawdown)
    print("Analysis successful.")


if __name__ == '__main__':
    main()