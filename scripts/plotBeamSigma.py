import pybdsim

import matplotlib.pyplot as plt

def LoadFocusRegion(filename):
    d = pybdsim.Data.Load(filename)

    result = {}
    result['s'] = d.optics.GetColumn("S")

    # want data after dipole - choose S > 8.1m
    mask = result['s'] > 8.1

    result['s'] = result['s'][mask] # update s array
    for name in ['Sigma_x', 'Sigma_Sigma_x', 'Sigma_y', 'Sigma_Sigma_y']:
        result[name] = d.optics.GetColumn(name)[mask]

    return result

def PlotBeamSigma(dataDictionary):
    d = dataDictionary # shortcut
    plt.figure()
    sf = 1e3 # scaling factor
    plt.errorbar(d['s'], d['Sigma_x']*sf, yerr=d['Sigma_Sigma_x']*sf, fmt=".", label="x")
    plt.errorbar(d['s'], d['Sigma_y']*sf, yerr=d['Sigma_Sigma_y']*sf, fmt=".", label="y")

    plt.axvline(11.097,color='r',label='collimator')
    plt.axvline(11.787,color='b',label='detector')
    
    plt.xlabel('S (m)')
    plt.ylabel('$\sigma$ (mm)')
    plt.legend()

def DoIt():
    d = LoadFocusRegion("../models/run1-optics.root")
    PlotBeamSigma(d)    

if __name__ == "__main__":
    DoIt()
    
