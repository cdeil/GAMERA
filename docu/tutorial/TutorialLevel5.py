#!/usr/local/bin/python

import sys
import os
sys.path.append(os.path.abspath('./lib'))
import gamerapy
import numpy as np
import math
import matplotlib.pyplot as plt
import ConfigParser

def CalculateTimeDependentStuff():
  t = np.logspace(0,math.log10(1.e6*age),80)
  gammap = 1.3333;
  vej = math.sqrt(10.*e0/(3.*mej))
  c = math.pow((6./(15.*(gammap-1.)))+289./240.,-0.2);
  lum=[]
  emax=[]
  r=[]
  v=[]
  b=[]
  for i in t:
    lum.append((1.-etab)*lum0*math.pow(1.+i/tc,-1.*(brind+1.)/(brind-1.)))
    emax.append(3.*eps*gamerapy.el_charge*math.sqrt(etab*lum[len(lum)-1]/((1.-etab)*gamerapy.c_speed)))
    r.append(c*math.pow(lum0*i*gamerapy.yr_to_sec/e0,0.2)*vej*i*gamerapy.yr_to_sec)
    v.append(1.2*r[len(r)-1]/(gamerapy.yr_to_sec*i))
  for i in xrange(len(t)):
    bi=0.
    ri=r[i]
    if(i==0):
      bi=0.
    else:
      for j in xrange(i):
        if(j==0):
          continue
        bi = bi+etab*lum[j]*ri*gamerapy.yr_to_sec*(t[j]-t[j-1])
    bi=math.sqrt(6.*bi/(ri*ri*ri*ri))
    b.append(bi)
  lum = np.array(zip(t,lum))
  b = np.array(zip(t,b))
  emax = np.array(zip(t,emax))
  r = np.array(zip(t,r))
  v = np.array(zip(t,v))
  return lum, b, emax, r, v

if __name__ == "__main__":
  # Read in parameter file
  configFile = os.path.abspath(sys.argv[1])
  configParser = ConfigParser.RawConfigParser()
  configParser.read(configFile)

  f, (ax1, ax2, ax3, ax4, ax5, ax6, ax7) = plt.subplots(7, 1, sharey=False,figsize=(7, 35))  
  global lum0, age, tc, mej, e0, etab, eps
  lum0 = float(configParser.get('Parameters','InitialLuminosity'))
  age = float(configParser.get('Parameters','Age'))
  tc = float(configParser.get('Parameters','CharAge'))
  dist = gamerapy.pc_to_cm*float(configParser.get('Parameters','Distance'))
  dens = float(configParser.get('Parameters','AmbientDensity'))
  tNIR = float(configParser.get('Parameters','tNIR'))
  eNIR = gamerapy.TeV_to_erg*1.e-12*float(configParser.get('Parameters','edensNIR'))
  tFIR = float(configParser.get('Parameters','tFIR'))
  eFIR = gamerapy.TeV_to_erg*1.e-12*float(configParser.get('Parameters','edensFIR'))
  ebins = float(configParser.get('Parameters','Ebins'))
  emin = gamerapy.TeV_to_erg*float(configParser.get('Parameters','Emin'))
  ebreak = gamerapy.TeV_to_erg*float(configParser.get('Parameters','Ebreak'))
  spindlow = float(configParser.get('Parameters','SpectralIndexLow'))
  spindhigh = float(configParser.get('Parameters','SpectralIndexHigh'))
  mej = gamerapy.mSol*float(configParser.get('Parameters','Mej'))
  e0 = float(configParser.get('Parameters','E0'))
  etab = float(configParser.get('Parameters','etaB'))
  eps = float(configParser.get('Parameters','epsilon'))
  brind = float(configParser.get('Parameters','BrakingIndex'))
  outfile = configParser.get('Files','outfile')

  lumt,bt,emaxt,r,v = CalculateTimeDependentStuff()
  fr = gamerapy.Radiation()
  fp = gamerapy.Particles()
  fu = gamerapy.Utils()
  fu.DrawGamera()
  # set particle stuff
  fp.SetLuminosityLookup(lumt)
  fp.SetBFieldLookup(bt)
  fp.SetEmaxLookup(emaxt)
  fp.SetRadiusLookup(r)
  fp.SetVelocityLookup(v)
  fp.SetAmbientDensity(dens)
  fp.SetEmin(emin)
  fp.SetBreakEnergy(ebreak)
  fp.SetLowSpectralIndex(spindlow)
  fp.SetSpectralIndex(spindhigh)
  fp.SetEnergyBinsForNumericalSolver(ebins)
#  fp.SetCriticalMinEnergyForGridSolver(1.e-2)
  fp.SetAge(age)

  # set radiation stuff
  fr.SetDistance(dist)
  fr.AddThermalTargetPhotons(2.7,0.25*1.602*1.e-12)
  fr.AddThermalTargetPhotons(tFIR,eFIR)
  fr.AddThermalTargetPhotons(tNIR,eNIR)
  fr.SetAmbientDensity(fp.GetAmbientDensity())
#  fr.SetSynchrotronEmissionModel(1)
  fr.CreateICLossLookup()
  fp.SetICLossLookup(fr.GetICLossLookup())

  # calculate stuff 
  t = np.logspace(math.log10(500.),math.log10(age),6)
  n = 0
  for i in t:
    print i,n
#    if(i<=500):
#      fp.SetCriticalMinEnergyForGridSolver(1.e-2)
#    elif(i<3000):
#      fp.SetCriticalMinEnergyForGridSolver(2.*1.e-2)
#    else:
#      fp.SetCriticalMinEnergyForGridSolver(2.*1.e-3)
    fp.SetAge(i) 
    fr.SetBField(fp.GetBField())
    fp.CalculateParticleSpectrum("electrons")
    fr.SetElectrons(fp.GetParticleSpectrum())
    if(n!=0):
      fr.RemoveLastICTargetPhotonComponent()
    fr.AddSSCTargetPhotons(fp.GetRadius())
    fr.CalculateDifferentialPhotonSpectrum()
    ElectronSED = np.array(fr.GetElectronSED())
    TotalSED = np.array(fr.GetTotalSED())
    ICSED = np.array(fr.GetICSED())
    BremsSED = np.array(fr.GetBremsstrahlungSED())
    SynchSED = np.array(fr.GetSynchrotronSED())
    ax1.plot(ElectronSED[:,0],ElectronSED[:,1],color='black',alpha=1.-n,label=str(round(i,0)))
    ax2.plot(TotalSED[:,0],TotalSED[:,1],color='black',alpha=1.-n,label=str(round(i,0)))
    n = n+0.1


  ax1.legend(title="age",prop={'size':6},loc="lower left")
  ax2.legend(title="age",prop={'size':6},loc="lower left")

  ## plot stuff ##
  ax1.set_yscale("log")
  ax1.set_xscale("log")
  ax2.set_yscale("log")
  ax2.set_xscale("log")  
  ax3.set_yscale("log")
  ax3.set_xscale("log")
  ax4.set_yscale("log")
  ax4.set_xscale("log")
  ax5.set_xscale("log")
  ax6.set_xscale("log")
  ax7.set_xscale("log")
  ax1.set_ylabel(r'$E^{2} \mathrm{d}N/\mathrm{d}E(\mathrm{erg})$', fontsize=13)
  ax1.set_xlabel(r'$E (\mathrm{TeV})$', fontsize=13)
  ax2.set_ylabel(r'$\nu F_{\nu}(\mathrm{erg} \cdot \mathrm{cm}^{-2} \cdot \mathrm{s}^{-1})$', fontsize=13)
  ax2.set_xlabel(r'$E (\mathrm{TeV})$', fontsize=13)
  ax3.set_ylabel(r'$L (\mathrm{erg} \cdot \mathrm{s}^{-1})$', fontsize=13)
  ax3.set_xlabel(r'$t (\mathrm{yrs})$', fontsize=13)
  ax4.set_ylabel(r'$B (\mu \mathrm{G})$', fontsize=13)
  ax4.set_xlabel(r'$t (\mathrm{yrs})$', fontsize=13)
  ax5.set_ylabel(r'$E_{max} (\mathrm{erg})$', fontsize=13)
  ax5.set_xlabel(r'$t (\mathrm{yrs})$', fontsize=13)
  ax6.set_ylabel(r'$R (\mathrm{pc})$', fontsize=13)
  ax6.set_xlabel(r'$t (\mathrm{yrs})$', fontsize=13)
  ax7.set_ylabel(r'$V (\mathrm{cm/s}$', fontsize=13)
  ax7.set_xlabel(r'$t (\mathrm{yrs})$', fontsize=13)
  ax1.set_xlim([0.7*min(ElectronSED[:,0]),2.e4])
  ax1.set_ylim([1.e42,1.e49])
  ax2.set_xlim([0.7*min(TotalSED[:,0]),2.e3])
  ax2.set_ylim([1.e-16,1.e-6])
  ax3.set_xlim([2.,1.5*age])
  ax3.set_ylim([1.e36,1.1*max(lumt[:,1])])
  ax4.set_xlim([2.,1.5*age])
  ax4.set_ylim([1.e-6,1.1*max(bt[:,1])])
  ax5.set_xlim([2.,1.5*age])
  ax5.set_ylim([0.7*min(emaxt[:,1]),1.1*max(emaxt[:,1])])
  ax6.set_xlim([2.,1.5*age])
  ax6.set_ylim([0.,100])
  ax7.set_xlim([2.,1.5*age])
  ax7.set_ylim([0.,1.e9])
  ax3.plot(lumt[:,0],lumt[:,1],color='black',alpha=1.,label="luminosity")
  ax3.legend(prop={'size':12},loc="lower left")
  ax4.plot(bt[:,0],bt[:,1],color='black',alpha=1.,label="B-field")
  ax4.legend(prop={'size':12},loc="lower left")
  ax5.plot(emaxt[:,0],emaxt[:,1],color='black',alpha=1.,label=r'$E_{max}$')
  ax5.legend(prop={'size':12},loc="lower left")
  ax6.plot(r[:,0],r[:,1]/gamerapy.pc_to_cm,color='black',alpha=1.,label="Radius")
  ax6.legend(prop={'size':12},loc="lower left")
  ax7.plot(v[:,0],v[:,1],color='black',alpha=1.,label="Velocity")
  ax7.legend(prop={'size':12},loc="lower right")
  f.savefig(outfile)

