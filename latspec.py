#!/usr/bin/env python

""" 

       Fermi LAT Xspec Analysis  (version 0.1.1)

The Latspec is a graphical interactive analysis tool designed for
reduction and analysis of the Fermi/LAT (http://fermi.gsfc.nasa.gov/ssc) 
data using Xspec astrophysical spectral fitting package 
(http://heasarc.gsfc.nasa.gov/docs/xanadu/xspec). The tool
is integrated with Fermi Science Tools, FTOOLS, Xspec and 
DS9 imaging tool (hea-www.harvard.edu/RD/ds9) to provide
fast and convenient analysis steps from LAT server data to 
spectral modeling.


> latspec

To get help on parameters:

> latspec -h

"""

__author__ = 'Nikolai Shaposhnikov'
__version__ = '1.1.0'

import sys
import os
#from GtApp import *
from fgltools import *


# define FERMI tools 
#filter = GtApp('gtselect')
#maketime = GtApp('gtmktime')
#gtCube = GtApp('gtltcube')
#gtPsf = GtApp('gtpsf')
#evtbin = GtApp('gtbin')
#gtRsp = GtApp('gtrspgen')

class LatSpec:


    """This is the base class for Latspec application. It is 
    created and passed into LatSpecApp class, which runs GUI.

    will create an object called latSpec with the <basename> of
    'latspec' and will read in all of the options from the resource
    file. Reads the data in the current directory and initialises
    oll variables decribing the data. Then it is passed to 
    LatspecApp.
    """

    def __init__(self,basename='latspec',
                 rad = 3.0,
                 offset = 15.0,
                 tmin = "INDEF",
                 tmax = "INDEF",
                 zmax = 100.0,
                 nchan = 30,
#                 irfs = "P7REP_SOURCE_V15",
                 irfs = "P7SOURCE_V6",
                 flux_tres = 5.0e-9,
                 verbosity = 4,
                 catalog = '',
                 datapath=''):
        
        
        self.havedata = False
        self.rad = rad
        self.bkg_rad = rad
        self.offset = offset
        self.basename = basename
        self.tmin = tmin
        self.tmax = tmax
        self.emin = 100.0
        self.emax = 300000.0
        self.nchan = int(nchan)
        self.zmax = zmax
        self.binsz = 1
        self.fluxTres = flux_tres
        self.dist_tres = 0.5
        self.irfs = irfs
        self.catalog = catalog
        self.haveCatalog = False
        self.thetacut = 60.0
        self.eventclass = int(2)
        self.dcostheta = 0.05
        self.chatter = verbosity
        self.ltcube = "None"
        self.datapath = datapath
        self.ds9 = False
#    Check if we have a 2FGL catalog
        conffile = os.environ['HOME']+'/.latspecrc'
        if os.path.exists(conffile):
            cf = open(conffile,'r')
#            print cf
            lll = cf.readlines()
#            print lll
            for line in lll:
#                print line.find('LAT_DATA_PATH=')
                if line.find('LAT_DATA_PATH=') == 0:
                    
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
#                    print pt
                    if os.path.isdir(pt):
#                        print pt
                        os.chdir(pt)
                        self.datapath = pt

                if line.find('2FGL_CATALOG_FILE=')==0 and not os.path.exists(self.catalog):
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                    if os.path.exists(pt):
                        self.catalog = pt

                if line.find('IRFS=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    self.irfs = pt
#                    print self.irfs

                if line.find('FLUX_THRESHOLD=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        self.fluxTres = float(pt)
                    except:
                        pass

                if line.find('BINSZ=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 1.0
                        self.binsz = xxx
                    except:
                        self.binsz = 1.0


                if line.find('BASENAME=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        if pt == "": pt = "latspec"
                        self.basename = pt
                    except:
                        self.binsz = "latspec"


                if line.find('ZMAX=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 100.0
                        self.zmax = xxx
                    except:
                        self.zmax = zmax

                if line.find('DCOSTHETA=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 0.05
                        self.dcostheta = xxx
                    except:
                        self.zmax = zmax

                if line.find('THETACUT=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 60.0
                        self.thetacut = xxx
                    except:
                        self.thetacut = 60.0

            cf.close()

        if self.datapath == '':
            self.datapath = os.getcwd()

        self.verify_cat()

#   Prepare directory and set some variables
        self.prepData()

        self.set_names()

    def writerc(self):

        """ Writes the resource file ~./latspecrc. """

        conffile = os.environ['HOME']+'/.latspecrc'
        cf = open(conffile,"w")
        cf.write("BASENAME="+str(self.basename)+"\n")
        cf.write("LAT_DATA_PATH="+self.datapath+"\n")
        cf.write("2FGL_CATALOG_FILE="+self.catalog+"\n")
        cf.write("FLUX_THRESHOLD="+str(self.fluxTres)+"\n")
        cf.write("IRFS="+self.irfs+"\n")
        cf.write("ZMAX="+str(self.zmax)+"\n")
        cf.write("BINSZ="+str(self.binsz)+"\n")
        cf.write("DCOSTHETA="+str(self.dcostheta)+"\n")
        cf.write("THETACUT="+str(self.thetacut)+"\n")

        cf.close()
            

    def set_names(self):

        """
        Performs some data and variable check and sets some flags. 
        """

        from string import split,join        

        if self.havedata:
            self.name ="%s_ra%.2f_dec%.2f_r%.2f"%(self.basename,self.ra,self.dec,self.rad)
        else:
            self.name = ""

        self.fgl_source = 'None'
        self.assoc_source = 'None'
        self.spectrum_type = "PowerLaw"
        self.fgl_powerlaw_index = 2.0
        self.fgl_pivot_e = 1000.0
        self.fgl_cutoff_e = 100000.0
        self.fgl_beta = 0.5

        if self.haveCatalog and self.havedata:
            name,distance,sind,res = get_closest_fgl_source(self.ra,self.dec,self.catalog)
            self.fgl_dist = distance

            if distance < self.dist_tres:
                cfile = pyfits.open(self.catalog)
                self.spectrum_type = cfile[1].data.field('SpectrumType')[sind]
                self.fgl_powerlaw_index = cfile[1].data.field('Spectral_Index')[sind]
                self.fgl_pivot_e = cfile[1].data.field('Pivot_Energy')[sind]
                self.fgl_cutoff_e = cfile[1].data.field('Cutoff')[sind]
                self.fgl_beta = cfile[1].data.field('beta')[sind]
                self.assoc_source = cfile[1].data.field('ASSOC1')[sind]
                cfile.close()

                sn = join(split(name," "),"")
                self.name = self.basename+'_'+sn
                self.fgl_source = name


        self.specfile = self.name+'_src.pha'
        self.bkgfile = self.name+'_bkg.pha'
#        self.ltcube = "None"
        if not os.path.exists(self.ltcube): self.ltcube = "None"
        self.rspfile = self.name+'.rsp'
        self.arffile = self.name+'.arf'
        self.evfile = "None"
        self.image = "None"


        if os.path.exists(self.basename+'_ltcube.fits'): 
            self.ltcube = self.basename+'_ltcube.fits'
        if os.path.exists(self.basename+'_filtered_gti.fits'): 
            self.evfile = self.basename+'_filtered_gti.fits'
        if os.path.exists(self.basename+'_image.fits'): 
            self.image = self.basename+'_image.fits'

            
    def prepData(self):

        """ Prepares LAT data in the current directory for analysis.
        In the datadir writes efiles.list file containing the list of
        event files, i.e. files ending on _PH.fits and 
        identifies the SC file. 
        """


        from coorconv import loffset,eq2gal,gal2eq,dist
        import re
        
        ret = ""
        wd = os.getcwd()
        files = os.listdir(wd)
        scfile = [ f for f in files if re.search("_SC",f) ]
        if len(scfile) == 0: 
            ret += "No SC files found in the directory.Exit.\n"
            self.havedata = False
            self.scfile = ""
            return 
        if len(scfile) > 1:
            ret += "Warning: More that one SC file is found in the\n"
            ret += "specified directory.\n"
            for f in scfile: print f
            ret += "Using"+scfile[0]+"\n"
        phfiles = [ f for f in files if re.search("_PH",f) ]
        if len(phfiles) == 0: 
            ret += "No event files found.Exit.\n"
            self.havedata = False
            self.scfile = ""
            return
        os.system('echo '+phfiles[0]+' > efiles.list')
        for f in phfiles[1:]:os.system('echo '+f+' >> efiles.list')
        self.havedata = True
#        print "prepdata:"+self.havedata
        self.scfile = scfile[0]

        gotinfo,self.obs_pars = self.getObsInfo('efiles.list')

#        self.tmin = self.obs_pars['tmin']
#        self.tmax = self.obs_pars['tmax']
        self.emin = self.obs_pars['emin']
        self.emax = self.obs_pars['emax']
        self.ra = self.obs_pars['RA']
        self.dec = self.obs_pars['DEC']


#        ll,bb = eq2gal(self.ra,self.dec)
#        self.bkg_ra,self.bkg_dec = gal2eq(ll-self.offset,bb)

        ll,bb = eq2gal(self.ra,self.dec)
        r1,d1 = gal2eq(ll-self.offset,bb)
        r2,d2 = gal2eq(ll+self.offset,bb)
        dist1 = dist((self.obs_pars["RA"],self.obs_pars["DEC"]),(r1,d1))
        dist2 = dist((self.obs_pars["RA"],self.obs_pars["DEC"]),(r2,d2))
        if dist1<dist2:
            self.bkg_ra,self.bkg_dec = gal2eq(ll-self.offset,bb)
        else:
            self.bkg_ra,self.bkg_dec = gal2eq(ll+self.offset,bb)
 

#        loff = loffset(ll,bb,self.offset)


        return ret

    def getObsInfo(self,efile):
        
        
        """ Reads the name of the first file in the efiles.list and
        reads the observation information and returns it in the form
        of the disctionary (ra,dec,rad,tmin,tmax,emin,emax,etc) """

        import pyfits
        import string

        try:
            fil = open(efile,'r')
        except:
#            raise FileNotFound
            return 0,{}
        fname = fil.readline()
        fh = pyfits.open(fname)
        dsval3 = fh[1].header['DSVAL3']
        ds_split = string.split(string.split(dsval3,'(')[1],',')
        ra = float(ds_split[0])
        dec = float(ds_split[1])
        roi = float(ds_split[2][:-1])
        dsval5 = fh[1].header['DSVAL5']
        emn,emx =string.split(dsval5,':')
        emin = float(emn)
        emax = float(emx)
        dsval4 = fh[1].header['DSVAL4']
        tmn,tmx = string.split(dsval4,':')
        tmin = float(tmn)
        tmax = float(tmx)
        dict = {"RA":ra,"DEC":dec,"roi":roi,"emin":emin,"emax":emax,"tmin":tmin,"tmax":tmax}
        return 1,dict

    def verify_cat(self):

        """ Verifies if the 2FGL catalog file exists and perform 
        simple check for the file format and content""" 

        import pyfits
        xxx = self.catalog
        self.haveCatalog = False
        self.catalog = "None"
        if os.path.exists(xxx):
            fname = os.path.abspath(xxx)
            try:
                fh = pyfits.open(fname)
                cols = fh[1].columns.names
                if 'Source_Name' in cols and \
                        'RAJ2000' in cols and \
                        'DEJ2000' in cols:
                    self.haveCatalog = True
                    self.catalog = fname

            except:
                self.haveCatalog = False
                self.catalog = "None"
            else:
                fh.close()
        else:
            self.haveCatalog = False
            self.catalog = "None"
                    


    def write_regions(self,regfile = ''):

        """
        Writes current regions into a region .reg file readable by DS9.
        Uses fgltool.py module to select brightest sources in the field
        and writes them into the file, so they can be loaded to DS9.
        """

        from fgltools import get_brightest_sources
        
        if regfile == '': 
            rf = self.basename+'.reg'
        else:
            rf = regfile

        regf = open(rf,'w')
        regf.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n')
        regf.write("fk5\n")
        regf.write("circle({0},{1},{2}\") # source\n".format(self.ra,self.dec,self.rad*3600.0))
        regf.write("circle({0},{1},{2}\") # color=red background\n".format(self.bkg_ra,\
                                         self.bkg_dec,self.bkg_rad*3600.0))


        if self.haveCatalog == True:
            fgl_sources,fgl_ras,fgl_decs = get_brightest_sources( \
                    self.obs_pars['RA'],self.obs_pars['DEC'],\
                    float(self.obs_pars['roi']),\
                    self.fluxTres,self.catalog)
            for i in range(len(fgl_sources)):
                regf.write("point({0},{1}) # select=0 point=cross text=\"{2}\" color=white\n".format(fgl_ras[i],fgl_decs[i],fgl_sources[i]))

        regf.close()
        
        
    def runds9(self):
        
        """Invokes ds9. Loads regions to ds9.
        If 2FLG catalog is available, shows catalog sources, which are brighter
        than FLUX_THRESHOLD  parameter on the ds9 image."""

        from string import atof        
        import subprocess

        rf = self.basename+'.reg'
        self.write_regions()
# This is needed to avoid comunication with another ds9 running from ds9
        pid = os.getpid()
        self.ds9id = 'latspec'+str(pid)
        ds9pr = subprocess.Popen(['ds9','-title',self.ds9id,self.image,'-regions',\
                                      rf,'-cmap','b','-sqrt','-zoom','to','fit',\
                                      '-wcs','skyformat','degrees'])
        self.ds9 = ds9pr
        return ds9pr



    def getregions(self):

        """ Reads region information from ds9"""

        from string import atof
        import subprocess

        try:
            lget = subprocess.Popen(["xpaget",self.ds9id,"regions"],stdout=subprocess.PIPE).communicate()[0]
        except:

            print "Failed to get regions from ds9."
            print lget
            return -1
            
        
        lines = lget.split("\n")

        for line in lines:
            if not line: break
            if line[0:6] == "circle":
                spl = line.split()
                spl1 = line[7:].split(")")[0].split(",")
#                print spl1
                if spl[-1] == "background":
#                    print spl1
                    self.bkg_ra = atof(spl1[0])
                    self.bkg_dec = atof(spl1[1])
                    self.bkg_rad = atof(spl1[2][:-1])/3600.0
#                    print self.bkg_ra,self.bkg_dec,self.bkg_rad
#                elif spl[-1] == "source":      
                else:
#                    print spl1
                    self.ra = atof(spl1[0])
                    self.dec = atof(spl1[1])
                    self.rad = atof(spl1[2][:-1])/3600.0
#                    print self.ra,self.dec,self.rad

 


#    def spc(self):
#    Calculates the source proximity coefficient according
#    to 2FGL fluxes.
#        import pyfits
#        from coorconv import sdist

#        if self.haveCatalog == True:
#            try:
#                fglf = pyfits.open(self.catalog)
#            except():
#                return 0.0, -1, "Failed to open catalog file"
            
#            name,distance,sind,res = \
#                get_closest_fgl_source(self.ra,self.dec,self.catalog)
#            ass_name = fglf[1].data.field('ASSOC1')[sind]
#            print "Assuming that ",name,"(",ass_name,") is the central source."
#            print "The distance to center of the region is ", distance," degrees."
       
#            source = fglf[1].data.field('Source_name')
#            ra = fglf[1].data.field('RAJ2000')
#            dec = fglf[1].data.field('DEJ2000')
#            flux = fglf[1].data.field('Flux1000')
#            flux_err = fglf[1].data.field('Unc_Flux1000')
#            eflux = fglf[1].data.field('Energy_Flux100')
#            eflux_err = fglf[1].data.field('Unc_Energy_Flux100')
#            print "2FGL Flux1000 is ", flux[sind],"+/-",flux_err[sind]," photons/cm**2/s."
            
                
#            spcx = 0.0
#            for i in range(len(source)):
#                dist = sdist(ra[i],dec[i],self.ra,self.dec)
#                if dist < self.obs_pars['roi'] and  i != sind:
#                    spcx += flux[i]/(2.0+dist*dist)
                        
                        
#            spcx = spcx/flux[sind]
#            print "Source proximity coefficient for ",name,":",spcx
#            return spcx, eflux[sind], eflux_err[sind], 1
#            self.spc = spcx
#        else:
#            print "DO NOT HAVE FGL catalog file."
#            print "Specify catalog file with -c option."
#            return -1.0,0.0,0.0,0




    def run_gui(self):
        import Tkinter as tk
        from pylatspec_gui import LatSpecApp


        root = tk.Tk()
        app = LatSpecApp(master=root,analysis=self)
        app.master.title('LAT Xspec Analysis')
        app.mainloop()


def printHelp():
    """This function prints out the help."""

    cmd = "latspec"

    print """
                        - LAT Xspec Analysis - 

The Latspec is a graphical interactive analysis tool designed for
reduction and analysis of the Fermi/LAT (http://fermi.gsfc.nasa.gov/ssc) 
data using Xspec astrophysical spectral fitting package 
(http://heasarc.gsfc.nasa.gov/docs/xanadu/xspec). The tool
is integrated with Fermi Science Tools, FTOOLS, Xspec and 
DS9 imaging tool (hea-www.harvard.edu/RD/ds9) to provide
fast and convenient way from LAT server data to spectral modeling
and lightcurve analysis. There are three comand line options:


%s (-h|--help) ... This help text.

%s (-b |--basename=)<basename>  <basename> is the file rootname 
    which will be used for all product files. For example, the 
    spectrum will have the name <basename>_src.pha, background 
    - <basename>_bkg.pha, response -<basename>.rsp and so on.
    Default basename is "latspec".  
   

%s (-c|--catalog) The 2FLG catalog file.


To get more detailed help information on how to use the  program 
and peform LAT data analysis, start the program and press "Help"
button at the bottom of the main window.

""" %(cmd,cmd,cmd)

# Command-line interface             
def run_latspec():
    """Reads the command-line options and starts the program. """
    import getopt
    
#    try:
    opts, args = getopt.getopt(sys.argv[1:], 'hb:c:', ['help',
                                                             'basename=',
                                                             'catalog=',
                                                             ])
        #Loop through first and check for the basename
    basename = 'latspec'
    tstart = "INDEF"
    tstop = "INDEF"
    offset = 15.0
    radius = 3.0
    nchan = int(30)
    cat = 'gll_psc_v08.fit'
    fltres = 5.0e-9
    gui = True
#    irfs = 'P7SOURCE_V6'
        
    for opt,val in opts:
        if opt in ('-b','--basename'):
            basename = val
#        elif opt in ('-t','--tint'):
#            ttt = string.split(val,',')
#            if len(ttt) != 2:
#                print "Invalid option -t (--tint). The format is <t1,t2>. Exit"
#                return
 #           tstart = ttt[0]
 #           tstop = ttt[1]
#        elif opt in ('-e','--eint'):
#           ttt = string.split(val,',')
#            if len(ttt) != 2:
#                print "Invalid option -e (--eint). The format is <emin,emax>. Exit"
#                return
#            emin = ttt[0]
#            emax = ttt[1]
#        elif opt in ('-o','--offset'):
#            offset = val
#        elif opt in ('-i','--irfs'):
#            irfs = val
        elif opt in ('-c','--catalog'):
            cat = val
#        elif opt in ('-r','--radius'):
#            radius = float(val)
#        elif opt in ('-f','--flux_tres'):
#            fltres = float(val)
#        elif opt in ('-n','--nchan'):
#            nchan = int(val)
#        elif opt in ('--nogui'):
#            gui = False
        elif opt in ('-h','--help'):
            printHelp()
            return
            
#    par_dict = {"rad":radius,"offset:}
    ls = LatSpec(basename=basename,
                 rad=radius,
                 offset=offset,
                 tmin=tstart,
                 tmax=tstop,
                 nchan=nchan,
                 flux_tres = fltres,
                 catalog=cat)
#**** NS: if no gui, run no gui version. Otherwise run gui interface
    if not gui: 
        ls.run()
    else:
        ls.run_gui()

#


if __name__ == '__main__': run_latspec()


