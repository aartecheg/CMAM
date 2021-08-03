import pybdsim

# see http://www.pp.rhul.ac.uk/bdsim/pybdsim/data.html#sampler-data
d = pybdsim.Data.Load("../models/run1.root")
detector = pybdsim.Data.PhaseSpaceData(d, "detector")
pybdsim.Plot.PhaseSpace(detector, outputfilename="detector-phase-space")
