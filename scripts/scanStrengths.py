import matplotlib.pyplot as _plt
import multiprocessing as _mp
import numpy as _np
import os as _os
import pybdsim as _pybdsim
import shutil as _shutil
import subprocess as _subprocess

def MakePairsOfVoltages(start,stop,npoints):
    voltage1 = _np.linspace(start,stop,npoints)
    voltage2 = _np.linspace(start,stop,npoints)

    result = [(v1,v2) for v1,v2 in zip(voltage1,voltage2)]
    return result

def PrepareSingleModel(workingDirectory, name, replacements, basemodel):
    f = open(basemodel, 'r')
    o = f.read()
    f.close()

    for key,value in replacements.items():
        o = o.replace(key,str(value))
        
    wd = _os.path.abspath(workingDirectory)
    outputabspath = _os.path.join(wd, name+".gmad")
    fo = open(outputabspath, "w")
    fo.write(o)
    fo.close()
    return outputabspath

def PrepareScan(voltages, workingDirectory, baseModel, extraFiles, basename='job_'):
    parameters = [{'__VOLTAGE1__':v1,'__VOLTAGE2__':v2} for v1,v2 in voltages]
    jobsToRun = []
    for i,parameter in enumerate(parameters):
        name = basename+str(i)
        job = PrepareSingleModel(workingDirectory, name, parameter, baseModel)
        jobsToRun.append(job)

    for filename in extraFiles:
        _shutil.copy(_os.path.abspath(filename),workingDirectory+"/.")
        
    return jobsToRun

def RunSingleJob(absFileName, seed, ngenerate, outputname):
    print('Running ',absFileName)
    cwd = _os.path.dirname(absFileName)
    log = open(_os.path.join(cwd,outputname+"log.txt"),"w")
    args =  ['bdsim']
    args.append('--file='+absFileName)
    args.append('--seed='+str(seed))
    args.append('--batch')
    args.append('--ngenerate='+str(ngenerate))
    args.append('--outfile='+outputname)
    _subprocess.call(args, cwd=cwd, stdout=log, stderr=log)

    args2 =  ['rebdsimOptics']
    args2.append(outputname+".root")
    args2.append(outputname+"-optics.root")
    _subprocess.call(args2, cwd=cwd, stdout=log, stderr=log)
    print('Finished ',absFileName)
    return (_os.path.join(cwd,outputname+".root"), _os.path.join(cwd,outputname+"-optics.root"))

def RunJobs(jobsToRun, seed, ngenerate, ncores=8):
    args = [(j,seed,ngenerate,j.strip(".gmad")) for j in jobsToRun]
    pool = _mp.Pool(ncores)
    outputFiles = pool.starmap(RunSingleJob, args)
    return outputFiles

def AnalyseOutput(outputFiles, workingDirectory):
    sx,sy = [],[]
    detectorIndex = 27
    for f in outputFiles:
        raw = f[0]
        opt = f[1]
        d = _pybdsim.Data.Load(opt)
        sx.append(d.optics.GetColumn('Sigma_x')[detectorIndex])
        sy.append(d.optics.GetColumn('Sigma_y')[detectorIndex])
        del d
    return sx,sy

def PlotResult(sx, sy, voltages):
    v1 = [v[0] for v in voltages]
    v2 = [v[1] for v in voltages]
    sx = _np.array(sx)
    sy = _np.array(sy)
    _plt.figure()
    _plt.plot(v1,sx*1e3,label='$\sigma_x$')
    _plt.plot(v1,sy*1e3,label='$\sigma_y$')
    _plt.xlabel('Voltage 1 (V)')
    _plt.ylabel('$\sigma$ (mm)')
    _plt.legend()

    _plt.figure()
    _plt.plot(v2,sx*1e3,label='$\sigma_x$')
    _plt.plot(v2,sy*1e3,label='$\sigma_y$')
    _plt.xlabel('Voltage 2 (V)')
    _plt.ylabel('$\sigma$ (mm)')
    _plt.legend()

    # we could always do a 2D plot here...

def DoIt(seed=123):
    _os.mkdir("scan1") # make a working directory for this scan
    wd = _os.path.abspath("scan1") # absolute path to working directory

    # this is up to us how we generate pairs of voltages to simulate
    # ultimately we want a list of 2 nubmers in a tuple
    # e.g. [(100,200), (200,100), (300,400), (400,300)]
    voltages = MakePairsOfVoltages(1000,2000,10)

    # make copies of the model with the edited values
    jobsToRun = PrepareScan(voltages, wd, "../models/CMAM_V2_2MeV_template.gmad", ["../models/CMAM_V2_model.gmad"])

    # run the jobs and get back a list of output files
    outputFiles = RunJobs(jobsToRun, seed, 100)

    sx,sy = AnalyseOutput(outputFiles, wd)

    PlotResult(sx,sy,voltages)


if __name__ == "__main__":
    DoIt()
