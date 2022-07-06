# import dependencies
import os
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import matplotlib as mpl
from datetime import datetime
from itertools import cycle

# pandas table formatting
pd.options.display.float_format = "{:,.2f}".format

class DrawDownAnalysis:
    """
    Class for performing drawdown analysis of dam outlet works
    """
    # constants and unit conversions
    GRAVITY = 32.2 # ft/s/s
    CUBIC_FT_TO_ACRE_FT = 1/43559.9
    CFS_TO_ACREFT_PERHOUR = 0.08264462912563
    
    def __init__(self, dt=1, n_steps=1200):
        """ Constructor Function
        dt - time step [hrs]
        n_steps - number of analysis steps
        """
        # analysis settings
        self.dt = dt
        self.n_steps = n_steps
        
        # initialize variables
        self.drawdown_elev = None
        self.N_mult = None
        self.diam = None
        self.K_eq = None
        self.area = None
        self.radius_h = None
        
        # initialize tables
        self.path_area = None
        self.path_cap = None
        self.df_results = pd.DataFrame()
        self.df_capacity = pd.DataFrame()
        self.df_area = pd.DataFrame()

        print(f"Instantiated drawdown object...: dt: {dt}, n_steps: {n_steps}")
        
        
    def assignOutletParams(self, N_mult, diam, K_eq):
        """ Assign outlet parameters
        N_mult - multipler for number of outlets of identical configuration
        diam - pipe diameter [ft]
        L - length of outlet [ft]
        K_eq - equivalent coefficient for losses
        """
        self.N_mult = N_mult
        self.diam = diam
        self.K_eq = K_eq
        self.area = (np.pi/4)*diam**2
        self.radius_h = self.area/(np.pi*diam) # hydraulic radius = area/perimeter
        print(f"Assigned outlet parameters...: N_mult: {N_mult}, diam: {diam:.2f}, K_eq: {K_eq:.2f}")
        print(f"Derived outlet parameters...: area: {self.area:.2f}, radius_h: {self.radius_h:.2f}")
        return
    
    def assignResevoirParams(self, elev_o, H_o):
        """ Assign resevoir parameters
        elev_o - initial elevation (max certified pool) [ft]
        H_o - initial head (max head from max certified pool to outlet CL) [ft]
        """
        self.elev_o = elev_o
        self.H_o = H_o
        print(f"Assigned resevoir parameters...: elev_o: {elev_o}, H_o: {H_o}")
        return
    
    def assignAreaCapacityCurves(self, area, cap):
        """
        area - either path to area-elev curve csv file or a pandas dataframe: area,elev [acres,ft]
        cap - either path to capacity-elev curve csv file or a pandas dataframe: capacity,elev [acre-ft,ft]
        """
        # If paths are passed
        if (isinstance(cap, str) and isinstance(area, str)): 
            print("Paths passed for area capacity curves...")
            try: 
                self.df_area = pd.read_csv(area)
                self.df_capacity = pd.read_csv(cap)
                print("Sucessful assignment of area capacity curves!")
            except:
                print("Unsuccessful assignment of area capacity curves.")
        # Else if data frames are passed into
        elif (isinstance(cap, pd.DataFrame) and isinstance(area, pd.DataFrame)):
            print("Dataframes passed for area capacity curves...")
            area_names = ['area-acres', 'elev-ft']
            cap_names = ['storage-acre-ft', 'elev-ft']
            if (cap.columns == cap_names).all() and (area.columns == area_names).all():
                self.df_area = area
                self.df_capacity = cap
                print("Area capacity curves assigned sucessfully!")
            else:
                print("Invalid columns names.")
                print(f"Capacity column names must follow: {cap_names}.")
                print(f"Area column names must follow: {area_names}.")
        else:
            print("Invalid type.")
        return
    
    def assignDrawDownTargetElev(self, elev, note=""):
        """
        elev - target drawdown elevation (ft)
        note - note describing the drawdown criteria, e.g. "10% resevoir head in 7 days"
        """
        self.elev_drawdown = elev
        print(f"Assigned target drawdown elevation...: {elev}")
        return
    
    def runDrawdownAnalysis(self):
        """ Drawdown analysis routine
        """
        def discharge(H_T, A, K_eq):
            """ Chapter 10, Section 10.14, Eq. 8
            H_T - Total head to overcome losses to produce discharge [ft]
            A - area of pipe [ft^2]
            K_eq - equivalent losses
            """
            Q = A*np.sqrt((2 * self.GRAVITY * H_T)/K_eq)
            return Q
        
        # initialize arrays
        time = np.arange(1, self.n_steps + 1) * self.dt
        elev = np.zeros(self.n_steps)
        head = np.zeros(self.n_steps)
        storage_initial = np.zeros(self.n_steps)
        storage_final = np.zeros(self.n_steps)
        Q = np.zeros(self.n_steps)
        V = np.zeros(self.n_steps)
        dVol = np.zeros(self.n_steps)

        # apply initial conditions
        elev[0] = self.elev_o
        head[0] = self.H_o
        # Get initial storage from capacity-curve based on initial elev
        self.df_capacity['elev-ft']
        storage_initial[0] = np.interp(self.elev_o,                           
                                       self.df_capacity['elev-ft'], 
                                       self.df_capacity['storage-acre-ft'])

        # Perform the n steps of discharge calculations
        for i in range(self.n_steps):

            # Skip for first time step
            if i > 0:
                # The new storage is the final storage of the last time step
                storage_initial[i] = storage_final[i-1]

                # Read the new elevation from the capacity-elev. curve
                elev[i] = np.interp(storage_final[i-1], 
                                    self.df_capacity['storage-acre-ft'], 
                                    self.df_capacity['elev-ft'])

                # Update the head based on the change in elevation
                head[i] = head[i-1] + (elev[i] - elev[i-1])  

            # Discharge (cfs)
            if head[i] > 0: # discharge is positive so long as head is positive
                Q[i] = self.N_mult * discharge(head[i], self.area, self.K_eq)
                Q[i] = max(0, Q[i]) # flow must be non-negative

            # Velocity (ft/s)
            V[i] = Q[i]/self.area

            # Change in volume (in acre-ft)
            dVol[i] = (Q[i] * self.CFS_TO_ACREFT_PERHOUR)/self.dt

            # Compute the final storage (in acre-ft)
            storage_final[i] = storage_initial[i] - dVol[i]
    
        # Create a dataframe for output
        df = pd.DataFrame(data={'time(days)':time/24,
                                'elev(ft)':elev, 
                                'head(ft)':head,
                                'storage_initial(acre-ft)':storage_initial,
                                'Q(cfs)':Q, 
                                'V(ft/s)':V,
                                'dVol(acre-ft)':dVol,
                                'storage_final(acre-ft)':storage_final
                               })
        self.df_results = df
        return
    
    def plotDrawdown(self, key_x=None, key_y=None):
        """ Plot drawdown analysis
        key_x = optional key for independent variable
        key_y = optional key for dependent variable
        """
        if not self.df_results.empty:
            if not key_x and not key_y:  
                key_x = self.df_results.columns[0]
                key_y = self.df_results.columns[3]
            try:
                fig, ax = plt.subplots()
                ax.plot(self.df_results[key_x]/24, self.df_results[key_y])
                ax.set_xlabel('Time (days)')
                ax.set_ylabel('Storage (acre-ft)')
                ax.grid(which='both', alpha=0.2)
                ax.set_xlim(left=0, right = max(self.df_results[key_x]/24))
                ax.set_ylim(bottom=0)
                plt.show()
            except:
                print("invalid keys specified for plotting. valid fields are:", ', '.join(self.df_results.columns)) 
        return
    
    def plotAreaCapacity(self):
        """ Plot the capacity-area vs elevation curves
        """
        if not self.df_capacity.empty and not self.df_area.empty:
            fig, ax = plt.subplots(1, 2, figsize=(12, 4))
            ax[0].plot(self.df_area['area-acres'], self.df_area['elev-ft'])
            ax[1].plot(self.df_capacity['storage-acre-ft'], self.df_capacity['elev-ft'])
            ax[0].set_xlabel('Area (acres)')
            ax[1].set_xlabel('Storage (acre-ft)')
            [a.set_ylabel('Elevation (ft)') for a in ax]
            [a.grid(which='both', alpha=0.2) for a in ax]
            [a.set_xlim(left=0) for a in ax]
            for x, a in zip(['Resevoir Area Curve', 'Resevoir Capacity Curve'],ax): a.set_title(x)
        return
    
    def getStorageAtElev(self, elev):
        """ Interpolates the elevation from capacity-elev curve
        """
        if not self.df_capacity.empty:
            storage = np.interp(elev, self.df_capacity['elev-ft'], self.df_capacity['storage-acre-ft'])
            return storage
    
    def saveResultsToCSV(self, tag="drawdown-analysis"):
        """ Save the results to a .csv file
        """
        if not self.df_results.empty:
            fname = f"{str(datetime.now().date())}" + f"-{tag}.csv"
            self.df_results.to_csv(fname)
            print(f"Results saved to {fname}")
        return
    
    def summarize(self, verbose=True):
        """ Report time to 10% reduction in max certified to heel of dam, and time to drained resevoir
        verbose - if true, prints statements
        """
        if not self.df_results.empty:
            mask_10percH = self.df_results['elev(ft)'] < self.elev_drawdown
            drained_index = self.df_results['dVol(acre-ft)'][self.df_results['dVol(acre-ft)'] == 0].index[0]
            t_10percH = self.df_results[mask_10percH]['time(days)'].iloc[0]
            t_drained = self.df_results['time(days)'].loc[drained_index]
            if verbose:
                print(f"Time at which 10% head is reduced: {t_10percH:.2f} days" )
                print(f"Time at which resevoir is drained: {t_drained:.2f} days" )
        return t_10percH, t_drained
    
    def displayTable(self, elev=None):
        """ Display table results
        elev - target elevation to center table [ft]; if None, returns table to drawdown
        """
        if elev:
            mask = Analysis.df_results['elev(ft)'] < elev
            print(f"Elevation reached at index: {Analysis.df_results[mask].index[0]}")
            return Analysis.df_results[Analysis.df_results[mask].index[0]-5:].head(10)
        else:
            drained_index = Analysis.df_results['dVol(acre-ft)'][Analysis.df_results['dVol(acre-ft)'] == 0].index[0]
            print(f"Zero discharge reached at index: {drained_index}")
            return Analysis.df_results.head(drained_index + 1)
    
    def sensitivityAnalysis(self, ratios = np.array([1.0, 1.25, 1.5, 2.0, 5.0, 10.0]), display=True):
        """
        Performs sensitivity analysis for different loss ratios
        ratios - loss ratio sensitivity value = K(sensitivity analysis)/K_eq(base analysis)
                 defaults to ratios of [1.0, 1.25, 1.5, 2.0, 5.0, 10.0]
        display - boolean flag for displaying summary results
        """
        analyses = [] 
        time_drawdowns = [] 
        time_drained = []
        K_values = ratios * self.K_eq
        for i, k in enumerate(K_values):
            # instantiate a new object using exisitng params but for different k values
            a = DrawDownAnalysis(dt=self.dt, n_steps=self.n_steps)
            a.assignOutletParams(self.N_mult, self.diam, k)
            a.assignResevoirParams(self.elev_o, self.H_o)
            a.assignAreaCapacityCurves(self.df_area, self.df_capacity)
            a.assignDrawDownTargetElev(self.elev_drawdown, note="")

            # run the analysis and save results for plotting
            a.runDrawdownAnalysis()
            t10, tdrain = a.summarize(verbose=False)
            time_drawdowns.append(t10)
            time_drained.append(tdrain)
            analyses.append(a)
            
        # Plot the results
        symbols = cycle(['o','s','^'])
        x, y = 'time(days)', 'storage_initial(acre-ft)'
        t_max = analyses[0].df_results['time(days)'].max()

        fig = plt.figure(figsize=(8,6))
        for ai in analyses:
            plt.plot(ai.df_results[x], 
                    ai.df_results[y],
                    marker=next(symbols),
                    markevery=100, 
                    markeredgecolor='teal',
                    label=f'K_eq={ai.K_eq:.2f}')
        plt.plot([0, t_max],
                np.ones(2)*ai.getStorageAtElev(self.elev_drawdown),
                'k--', lw=1.0,
                label='10% Drawdown')

        plt.grid(which='both',alpha=0.2)
        plt.xlabel(x), plt.ylabel(y)
        plt.xlim(left=0, right=t_max), plt.ylim(bottom=0)
        plt.legend(loc='upper right')
        plt.show()

        # print results
        if display:
            df = pd.DataFrame(data={'Sensitivity (K/K_eq)': ratios, 
                                    'K':K_values, 
                                    't_10% (days)':time_drawdowns,
                                    't_drain (days)':time_drained
                                    })
            print(df)


if __name__ == '__main__':
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
    Analysis = DrawDownAnalysis(dt=1, n_steps=1100)
    Analysis.assignOutletParams(N_mult, diam, K_eq)
    Analysis.assignResevoirParams(elev_o, H_o)
    Analysis.assignAreaCapacityCurves(path_area, path_cap)
    Analysis.assignDrawDownTargetElev(elev_drawdown, note="10% resevoir head in 7 days")
    Analysis.runDrawdownAnalysis()
    Analysis.summarize()
    Analysis.saveResultsToCSV()
    # Analysis.sensitivityAnalysis()
    print("Analysis successful.")
