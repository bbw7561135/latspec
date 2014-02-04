import pyfits
import subprocess as sp
import threading
import time
import string
from psfcor import arfcreate
from GtApp import *

evbin = GtApp('gtbin')
gtrsp = GtApp('gtrspgen')
gtpsf = GtApp('gtpsf')
gtcube = GtApp('gtltcube')
gtexp =  GtApp('gtexposure')
gtselect = GtApp('gtselect')
mktime = GtApp('gtmktime')


class ls_thread():

    def __init__(self,evfile,scfile,sra,sdec,rad,bra,bdec,brad,
            cube,tbin = 86400,irfs = "P7REP_SOURCE_V15",
            tstart="INDEF",tstop="INDEF",emin=100.0,
            emax=300000.0,enbin=20,outfile='lc.fits',
            dcostheta=0.05,thetamax=60.0,binsz=1.0,zmax=100.0,
            pl_index=2.5,index_free = False,logfile="latspeclc.log",
            logqueue = None):
        self.srad = rad
        self.brad = brad

        self.logqueue = logqueue


        self.thread = threading.Thread(target=self.run,args=(
                evfile,scfile,sra,sdec,rad,bra,bdec,brad,
                cube,tbin,irfs,tstart,tstop,emin,
                emax,enbin,outfile,
                dcostheta,thetamax,binsz,zmax,
                pl_index,index_free,logfile))

        self.state = "not_run_yet"


    
    def start(self):
        """Starts the lightcurve calculation"""
        
        self.thread.start()
        self.state = "running"


    def putlog(self,s):


        if not self.logqueue == None:
#            print s
            self.logqueue.put("Lightcurve ("+time.ctime()+"):\n"+s)
            


    def stop(self):
        """Stops lightcurve calculation"""
        self.state = "stop"


    def run(self,evfile,scfile,sra,sdec,rad,bra,bdec,brad,
            cube,tbin,irfs,tstart,tstop,emin,
            emax,enbin,outfile,
            dcostheta,thetamax,binsz,zmax,
            pl_index,index_free,logfile):
        
        
        ''' Given the LAT dat event file (evfile), source and background regions,
        Generates a full flux curve using xspec fits for every interval. 
        

        Parameters:
        
        evfile  - observation event file, create with gtmktime
        scfile  - observation house keeping file
        sra     - source RA
        sdec    - source DEC
        rad     - source RAD (degrees)
        bra     - background RA
        bdec    - background DEC
        brad    - background region radius
        outfile [lc.fits] - output lightcurve FITS file
        tbin [86400]    - final flux curve time binnig (sec).
        tstart [INDEF]  - start time (MET sec). If INDEF the value is taken from the evfile.
        tstop  [INDEF] - start time (MET sec). If INDEF the value is taken from the evfile.
        emin [100.0]   - lower energy limit of the energy interval (MeV). 
        emin [300000.0]   - upper energy of the energy interval (MeV). 
        enbin [20]   - number of the energy bins to use in xspec fits.
        cube    - the galactic cube file. If not given or does not exist - it will be 
        calculated (takes a long time!!!). 
        binsz [1.0], zmax [100.0]   - corresponding gtltcube parameters if a cube is to be calculated. 
        thetamax [60.0],dcostheta [0.05] - corresponding parameters for psf and response calculations.
        See gtpsf,gtrspgen help for details.
        pl_index [2.5] - starting value for the photon index of the power law fits
        to data. 
        index_free [False] - if False the index is fixed at pl_index value
        
        ''' 
   
        logf  = open(logfile,"w")
        res_str = ""
        
        scf = pyfits.open(scfile)
        tstart_sc  = float(scf[0].header['TSTART'])
        tstop_sc = float(scf[0].header['TSTOP'])

        if tstart == "INDEF": 
            tstart = tstart_sc
        else:
            try:
                tstart = float(tstart)
            except:
                res_str += "Warning:  Error converting tstart to float.\n"
                res_str += "Using start time from SC file."
                self.putlog("Warning:  Error converting tstart to float.")
                self.putlog("Using start time from SC file.")



        if tstop == "INDEF": 
            tstop = tstop_sc
        else:
            try:
                tstop = float(tstop)
            except:
                res_str += "Warning:  Error converting tstop to float.\n"
                res_str += "Using stop time from SC file.\n"
                self.putlog("Warning:  Error converting tstart to float.")
                logf.write("Using stop time from SC file.\n")

        try:
            tbin = float(tbin)
        except:
            res_str += "Warning:  Error converting tbin to float.\n"
            self.putlog("Warning:  Error converting tbin to float.")
            logf.close()
            return -1,res_str


        if tbin < 0.0:
            res_str += "Negative tbin. Exit!.\n"
            logf.write("Negative tbin. Exit!.\n")
            logf.close()
            self.putlog("Negative tbin. Exit!.")

            return -1,res_str

        if tstart > tstart_sc: tstart = tstart_sc
        if tstop > tstop_sc: tstop = tstop_sc


        expr = "ARCCOS(SIN(DEC*#deg)*SIN("+str(sdec)+\
           "*#deg)+COS(DEC*#deg)*COS("+str(sdec)+"*#deg)*COS((RA-"+\
           str(sra)+")*#deg))/#deg<"+str(rad)

        pid = str(os.getpid())
        src_ef = 'ev'+pid+'_src.fits'
        bkg_ef = 'ev'+pid+'_bkg.fits'

        if self.state == "running":

            try:
                subprocess.call(["fselect",evfile,'!'+src_ef,expr])
            except:
                res_str += "Error occured when running FSELECT for src.\n"
                self.putlog("Error occured when running FSELECT for src.")
            else:
                res_str += "Src events extraction OK.\n"
#                putlog("Src events extraction OK.")

            fh = pyfits.open(src_ef,mode='update')
            hdu = fh[1].header
            hdu['DSVAL2  '] = "CIRCLE("+str(sra)+","+str(sdec)+",25.0)"

            fh.close()
            expr = "ARCCOS(SIN(DEC*#deg)*SIN("+str(bdec)+\
                "*#deg)+COS(DEC*#deg)*COS("+str(bdec)+"*#deg)*COS((RA-"+\
                str(bra)+")*#deg))/#deg<"+str(brad)

        if self.state == "running":
            try:
                subprocess.call(["fselect",evfile,'!'+bkg_ef,expr])
            except:
                res_str += "Error occured when running FSELECT for backgrnd.\n"
                self.putlog("Error occured when running FSELECT for backgrnd.")
            else:
                res_str += "Bkg extraction OK.\n"
#                putlog("Bkg extraction OK.")

# ltcube

        if self.state == "running":
            cubecalc = False

            if not os.path.exists(cube): cubecalc = True
            
            if cubecalc:

                gtcube['evfile'] = src_ef
                gtcube['scfile'] = scfile
                gtcube['outfile'] = cube
                gtcube['dcostheta'] = dcostheta
                gtcube['binsz'] = binsz
                gtcube['zmax'] = zmax
        
                res_str += gtcube.command()
                out = gtcube.runWithOutput(print_command=False)[1]
                xxx = out.read()
                res_str += out.read()
                logf.write(xxx)


        t1 = tstart
        t2 = t1+tbin
        nsp = 0

# psf

        if self.state == "running":

            psff = 'psf'+pid+'.fits'
            gtpsf['expcube'] = cube
            gtpsf['dec'] = sdec
            gtpsf['ra'] = sra
            gtpsf['outfile'] = psff
            gtpsf['irfs'] = irfs
            gtpsf['emin'] = 100.0
            gtpsf['emax'] = 300000.0
            gtpsf['nenergies'] = 101
            gtpsf['thetamax'] = thetamax
            gtpsf['ntheta'] = int(thetamax/dcostheta)
            gtpsf['chatter'] = 0

            res_str += gtpsf.command()
            out = gtpsf.runWithOutput(print_command=False)[1]
            xxx = out.read()
            res_str += xxx
            logf.write(xxx)



# openning xspec session


        try:
            os.system('rm -f xspec'+pid+'_lc.txt')
            os.system('touch xspec'+pid+'_lc.txt')
        except:
            pass
    
        arff = 'arf'+pid+'.arf'

#  response


        hdu0 = fh[0].header
        cflux = -9.0

#    flexp = pyfits.open('gtbin.lc')
#    lcdata = flexp[1].data


        ind10 = int(0)
        ind25 = int(0)
        ind50 = int(0)
        ind75 = int(0)

#        self.putlog('Lightcurve thread: Sarting the main loop')
#       Main loop
        nbin = (tstop - tstart)/tbin
        while t1<tstop and self.state == "running":
            
            if (t1 - tstart)/tbin > 0.1*nbin and ind10 == 0:
                self.putlog("Progress: 10%")
                ind10 = 1

            if (t1 - tstart)/tbin > 0.25*nbin and ind25 == 0:
                self.putlog("Progress: 25%")
                ind25 = 1

            if (t1 - tstart)/tbin > 0.5*nbin and ind50 == 0:
                self.putlog("Progress: 50%")
                ind50 = 1

            if (t1 - tstart)/tbin > 0.75*nbin and ind75 == 0:
                self.putlog("Progress: 75%")
                ind75 = 1
 

#            self.putlog('Sarting loop '+str(nsp))

            logf.write("Interval: "+str(nsp)+" Tstart = "+str(t1)+" Tstop = "+str(t2)+"\n")

            expr = "TIME>"+str(t1)+".AND.TIME<"+str(t2)

            sef1 = 'ev'+pid+'_src'+str(nsp)+'_1.fits'
            bef1 = 'ev'+pid+'_bkg'+str(nsp)+'_1.fits'


            try:
                subprocess.call(["fselect",src_ef,'!'+sef1,expr])
            except:
                xxx = "Error occured when running FSELECT for src.\n"
                res_str += xxx
#            logf.write(xxx)
            else:
                xxx = "Src events extraction OK.\n"
                res_str += xxx
#            logf.write(xxx)


            try:
                subprocess.call(["fselect",bkg_ef,'!'+bef1,expr])
            except:
                xxx = "Error occured when running FSELECT for src.\n"
                res_str += xxx
#            logf.write(xxx)
            else:
                xxx = "Src events extraction OK.\n"
                res_str += xxx
#            logf.write(xxx)


            expr = "START>"+str(t1)+".AND.STOP<"+str(t2)

            sef = 'ev'+pid+'_src'+str(nsp)+'.fits'
            bef = 'ev'+pid+'_bkg'+str(nsp)+'.fits'


            try:
                subprocess.call(["fselect",sef1+'+2','!'+sef,expr])
            except:
                xxx = "Error occured when running FSELECT for src.\n"
                res_str += xxx
#            logf.write(xxx)
            else:
                xxx = "Src events extraction OK.\n"
                res_str += xxx
#            logf.write(xxx)


            try:
                subprocess.call(["fselect",bef1+'+2','!'+bef,expr])
            except:
                xxx = "Error occured when running FSELECT for src.\n"
                self.putlog("Error occured when running FSELECT for src.")
                res_str += xxx
#            logf.write(xxx)
            else:
                xxx = "Src events extraction OK.\n"
                res_str += xxx
#            logf.write(xxx)


            srcf = 'src'+pid+str(nsp)+'.pha'

            evbin['algorithm'] = 'PHA1'
            evbin['ebinalg'] = 'LOG'
            evbin['evfile'] = sef
            evbin['scfile'] = scfile
            evbin['outfile'] = srcf
            evbin['tstart'] = t1
            evbin['tstop'] = t2
            evbin['emin'] = emin
            evbin['emax'] = emax
            evbin['enumbins'] = enbin
            evbin['chatter'] = '10'
            
            res = evbin.runWithOutput(print_command=False)[1]
            xxx = res.read()
            res_str += xxx
#        logf.write(xxx+"\n")

            bkgf = 'bkg'+pid+str(nsp)+'.pha'
            evbin['evfile'] = bef
            evbin['outfile'] = bkgf

            res = evbin.runWithOutput(print_command=False)[1]
            xxx = res.read()
            res_str += xxx
#        logf.write(xxx+"\n")

#  response

            if 1:
#            if nsp == 0:
                rspf = 'rsp'+pid+str(nsp)+'.rsp'
                gtrsp['respalg'] = "PS"
                gtrsp['specfile'] = srcf
                gtrsp['scfile'] = scfile
                gtrsp['thetacut'] = thetamax
                gtrsp['outfile'] = rspf
                gtrsp['irfs'] = irfs
                gtrsp['dcostheta'] = dcostheta
                gtrsp['emin'] = 100.0
                gtrsp['emax'] = 300000.0
                gtrsp['enumbins'] = 100
                gtrsp['chatter'] = 0
                xxx = gtrsp.command()        
                res_str += xxx
            #        logf.write(xxx+"\n")
                out = gtrsp.runWithOutput(print_command=False)[1]
                xxx = out.read()
                res_str += xxx
#        logf.write(xxx+"\n")

            if nsp == 0:
                arfcreate(arff,rad,rspf,psff)

# Write keywords to source spectrum file

            sp.call(['fparkey',bkgf,srcf,'BACKFILE'])
            sp.call(['fparkey',rspf,srcf,'RESPFILE'])
            sp.call(['fparkey',arff,srcf,'ANCRFILE'])
            sp.call(['fparkey','1.0',srcf,'BACKSCAL'])
            sp.call(['fparkey',str((self.brad/self.srad)**2),bkgf,'BACKSCAL'])

            time.sleep(0.05)


            if not os.path.exists(srcf) or not os.path.exists(bkgf) or \
            not os.path.exists(arff) or not os.path.exists(rspf):
                self.state = "stop"
                self.putlog("Lightcurve extractor: something wrong, files are missing. Stoping.")
                

            if self.state != "running": break

            xspecf = open('xspec'+pid+str(nsp)+'.xcm','w')
            xspecf.write('log xspec'+pid+str(nsp)+'.log\n')
            xspecf.write('query yes\n')                
            xspecf.write('data 1 '+srcf+' \n')
            xspecf.write('notice 1:'+str(emin*1000.0)+'-'+str(emax*1000.0)+' \n')
            xspecf.write('ignore 1: **-'+str(emin*1000.0)+' '+str(emax*1000.0)+'-** \n')
            if index_free:
                xspecf.write("model cpflux*pow & "+str(emin*1000.0)+" -1 0 0 1e10 1e10 & "+\
                     str(emax*1000.0)+" -1  0 0 1e16 1e16 & {0} 0.01 &  {1} 0.01 & 1.0 -1 & \n".\
                       format(cflux,pl_index))
            else:
                xspecf.write("model cpflux*pow & "+str(emin*1000.0)+" -1 0 0 1e10 1e10 & "+\
                     str(emax*1000.0)+" -1  0 0 1e10 1e10 & {0} 0.01 &  {1} -1 & 1.0 -1 & \n".\
                       format(cflux,pl_index))
            

            xspecf.write('renorm\n')
            xspecf.write('fit 500\n')
            xspecf.write('tclout param 3\n')
            xspecf.write('set cf [lindex $xspec_tclout 0]\n')
            xspecf.write('tclout param 4\n')
            xspecf.write('set pl [lindex $xspec_tclout 0]\n')
            xspecf.write('error max 1000000.0 3\n')
            xspecf.write('tclout error 3\n')
            xspecf.write('set cferr [lrange $xspec_tclout 0 1]\n')

            if index_free:
                xspecf.write('error 4\n')
                xspecf.write('tclout error 4\n')
                xspecf.write('set plerr [lrange $xspec_tclout 0 1]\n')
            else:
                xspecf.write('set plerr "0.0 0.0"\n')            
#        xspr.stdin.write('tclout statistic\n')
#        xspr.stdin.write('set chi $xspec_tclout\n')
            xspecf.write('catch {exec echo '+str(0.5*(t1+t2))+" "+str(0.5*(t2-t1))+' $cf $cferr $pl $plerr > xspec_lc'+pid+str(nsp)+'.txt } \n')   
            xspecf.write('quit\n')
            xspecf.write('yes\n')
            xspecf.close()

            xspr = sp.Popen(['xspec','xspec'+pid+str(nsp)+'.xcm'],stdout=sp.PIPE,stdin=sp.PIPE,stderr=sp.STDOUT)
#        xspr = sp.call(['xspec','xspec'+str(nsp)+'.xcm'])
            out = xspr.communicate()
            os.system('cat xspec_lc'+pid+str(nsp)+'.txt >> xspec'+pid+'_lc.txt')
            nsp += 1
            t1 += tbin
            t2 = min(tstop,t1+tbin)
            
# End of the main  loop

#    fh.close()
    

        if self.state == "running":

            flis = open('cols.lis','w')
            flis.write('TIME E\n')
            flis.write('TIMEDEL E\n')
            flis.write('FLUX E\n')
            flis.write('LOGFMIN E\n')
            flis.write('LOGFMAX E\n')
            flis.write('INDEX E\n')
            flis.write('INDMIN E\n')
            flis.write('INDMAX E\n')
            flis.close()


            fhead = open('head.lis','w')
            fhead.write('TELESCOP GLAST  / name of telescope generating data\n')
            fhead.write('INSTRUME LAT  / name of instrument generating data\n')
            fhead.write('CREATOR LATSPEC  / Software creating file\n')
            fhead.write('EMIN '+str(emin)+'  / Lower energy limit,  Mev\n')
            fhead.write('EMAX '+str(emax)+'  / Upper energy limit,  Mev\n')
            fhead.close()
            sp.call(["rm",'-f','lc1.fits','lc2.fits'])
            pr1 = sp.Popen(["fcreate",'cols.lis','xspec'+pid+'_lc.txt','lc'+pid+'1.fits',"headfile=head.lis"])
            pr1.wait()
#    time.sleep(0.01)

#    pr2.wait()
#    time.sleep(0.01)

            pr3 = sp.Popen(["fcalc",'lc'+pid+'1.fits','lc'+pid+'2.fits','ERROR','0.5*(LOGFMAX-LOGFMIN)'])
    #    out = pr3.communicate()
            pr3.wait()
            os.system('rm -f '+outfile)
            pr2 = sp.Popen(["fcalc",'lc'+pid+'2.fits',outfile,'INDEXERR','0.5*(INDMAX-INDMIN)'])    
            pr2.wait()

   

# Clean up        
        sp.call(["rm",'-f','lc'+pid+'1.fits','lc'+pid+'2.fits'])
        os.system('rm -f '+arff)
        os.system('rm -f '+psff)
        os.system('rm -f src'+pid+'*')
        os.system('rm -f bkg'+pid+'*')
        os.system('rm -f ev'+pid+'*')   
        os.system('rm -f xspec_lc'+pid+'*')
        os.system('rm -f xspec'+pid+'*')
        os.system('rm -f rsp'+pid+'*')
        #    os.system('rm -f lc1.fits')
        #    os.system('rm -f lc2.fits')

        logf.close()
        
        if self.state == "running": self.state = "done"
        if self.state == "stop": self.state = "stopped"

#    End of run()
#    End of ls_thread


# start of the spectrum thread

#class latsp_thread():




# start of filter thread

class filter_thread():

    def __init__(self,flist,scfile,outfile,obj_ra,obj_dec,roi_deg,tmin,tmax,emin,emax,zmax,
            logqueue = None):

        self.logqueue = logqueue

        self.thread = threading.Thread(target=self.run,args=(flist,scfile,outfile,
                                             obj_ra,obj_dec,roi_deg,tmin,tmax,emin,emax,zmax))

        self.state = "not_run_yet"
        self.out = ""

    
    def start(self):
        """Starts filtering """
        
        self.thread.start()
        self.state = "running"


    def putlog(self,s):


        if not self.logqueue == None:
#            print s
            self.logqueue.put("Filtering: ("+time.ctime()+"):\n"+s)


    def stop(self):
        """Stops filtering """
        import time
        self.state = "stop"
        self.out += "Filter thread: stop requested!\n"

        try:
            self.proc.terminate()
            time.sleep(0.5)
            proc_poll = self.proc.poll()
            while proc_poll == None:
#                time.sleep(0.5)
                os.kill(self.proc.pid(),0)
                proc_poll = self.proc.poll()
        
#                self.putlog("killing filter"+proc_poll)
        except:
            pass
        else:
            self.state = "stopped"


    def run(self,flist,scfile,outfile,obj_ra,obj_dec,roi_deg,tmin,tmax,emin,emax,zmax):
        import time

        pid = str(os.getpid())
        try:
            os.system('rm -f '+outfile)
            os.system('rm -f '+pid+'_filtered.fits')
        except:
            pass
        
        if self.state != "stop":

#            self.putlog("****Runnig GTSELECT****:")
            self.putlog(string.join(["gtselect",'infile=@'+flist,
                                          "outfile="+pid+"_filtered.fits",
                                          "ra="+str(obj_ra),"dec="+str(obj_dec),
                                          "rad="+str(roi_deg),
                                          "tmax="+str(tmax),"tmin="+str(tmin),
                                          "emax="+str(emax),"emin="+str(emin),
                                          "zmax="+str(zmax)," chatter=4"]," "))
            catchError = "at the top level:"
            gterr = False
            self.proc = subprocess.Popen(["gtselect",'infile=@'+flist,
                                          "outfile="+pid+"_filtered.fits",
                                          "ra="+str(obj_ra),"dec="+str(obj_dec),
                                          "rad="+str(roi_deg),
                                          "tmax="+str(tmax),"tmin="+str(tmin),
                                          "emax="+str(emax),"emin="+str(emin),
                                          "zmax="+str(zmax),"chatter=4"],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
            for line in self.proc.stdout:
                self.putlog("GTSELECT: "+line)
                if line.find(catchError) != -1:
                    gterr = True

            for line in self.proc.stderr:
                self.putlog("GTSELECT: "+line)
                if line.find(catchError) != -1:
                    gterr = True

        if gterr:

            self.putlog("Filter: GTSELECT error! Exiting...")
            self.out += "Filter: GTSELECT error!"
            self.state = "stop"

        if self.state != "stop":

            filter_string = "DATA_QUAL==1&&LAT_CONFIG==1&&ABS(ROCK_ANGLE)<52"                                    

            mktime["scfile"]=scfile
            mktime["filter"] = filter_string
            mktime["evfile"] = pid+'_filtered.fits'
            mktime["outfile"] = outfile
            mktime["chatter"] = 4

            self.putlog(string.join(["gtmktime","scfile="+scfile,
                                          "filter="+filter_string,
                                          "evfile="+pid+'_filtered.fits',
                                          "outfile="+outfile,"chatter=4"]," "))
            mktimeerr = False
            self.proc = subprocess.Popen(["gtmktime","scfile="+scfile,
                                          "filter="+filter_string,
                                          "roicut=yes",
                                          "evfile="+pid+'_filtered.fits',
                                          "outfile="+outfile,"chatter=4"],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            for line in self.proc.stdout:
                self.putlog("GTMKTIME: "+line)
                if line.find(catchError) != -1:
                    mktimeerr = True            

            for line in self.proc.stderr:
                self.putlog("GTMKTIME: "+line)
                if line.find(catchError) != -1:
                    mktimeerr = True            


            if mktimeerr:
                
                self.putlog("Filter: GTMKTIME error! Exiting...")
                self.out += "Filter: GTMKTIME error!"
                self.state = "stop"



        if self.state == "stop":

            self.state = "stopped"
            self.putlog("Stopped.")
            return
        
        if self.state == "running":

            self.state = "done"
            self.putlog("Done")
#            self.out += "Filter thread: Done." 
            return


class spectrum_thread():


    def __init__(self,evfile,scfile,sra,sdec,rad,bra,bdec,brad,
            tmin,tmax,emin,emax,enbin,irfs,cube,outroot,
            dcostheta,thetamax,binsz,zmax,
            logqueue):

        self.logqueue = logqueue

        self.thread = threading.Thread(target=self.run,args=(
            evfile,scfile,sra,sdec,rad,bra,bdec,brad,
            tmin,tmax,emin,emax,enbin,irfs,cube,outroot,
            dcostheta,thetamax,binsz,zmax))


        self.state = "not_run_yet"
        self.out = ""

    
    def start(self):
        """Starts filtering """
        
        self.state = "running"
        self.thread.start()



    def putlog(self,s):

        """ Puts a string in the log text."""
        if not self.logqueue == None:
#            print s
            self.logqueue.put("Spectrum: ("+time.ctime()+"):\n"+s)


    def stop(self):

        """Stops spectrum calculation. """
        self.state = "stop"
        self.putlog("Stop.")
        self.out += "Spectrum thread: stop requested!\n"
        self.state = "stopped"
        print("Specthread stopped")
        try:
            self.proc.terminate()
        except:
            pass

    def run(self,evfile,scfile,sra,sdec,rad,bra,bdec,brad,
            tmin,tmax,emin,emax,enbin,irfs,cube,outroot,
            dcostheta,thetamax,binsz,zmax):

        import time
        from psfcor import arfcreate
        import pyfits
        
        tstart = tmin
        tstop = tmax

        scf = pyfits.open(scfile)
        tstart_sc  = float(scf[0].header['TSTART'])
        tstop_sc = float(scf[0].header['TSTOP'])

        scf.close()
        self.putlog(os.environ['PFILES'])

        if tstart == "INDEF": 
            tstart = tstart_sc
        else:
            try:
                tstart = float(tstart)
            except:
                self.putlog("Warning:  Error converting tstart to float.")
                self.putlog("Using start time from SC file.")



        if tstop == "INDEF": 
            tstop = tstop_sc
        else:
            try:
                tstop = float(tstop)
            except:

                self.putlog("Warning:  Error converting tstart to float.")


        if tstart > tstart_sc: tstart = tstart_sc
        if tstop > tstop_sc: tstop = tstop_sc


        expr = "ARCCOS(SIN(DEC*#deg)*SIN("+str(sdec)+\
           "*#deg)+COS(DEC*#deg)*COS("+str(sdec)+"*#deg)*COS((RA-"+\
           str(sra)+")*#deg))/#deg<"+str(rad)+".AND.TIME>"+str(tstart)+".AND.TIME<"+str(tstop)




        pid = str(os.getpid())
        src_ef = 'ev'+pid+'_src.fits'
        bkg_ef = 'ev'+pid+'_bkg.fits'
        srcf = outroot+'_src.pha'
        bkgf = outroot+'_bkg.pha'

        if self.state == "running":

            try:
                self.putlog("***Running FSELECT to produce event file for the source region***")
                subprocess.call(["fselect",evfile,'!'+src_ef,expr])
            except:
                self.putlog("Error occured when running FSELECT for src.")
                self.stop()
            else:
                pass

            fh = pyfits.open(src_ef,mode='update')
            hdu = fh[1].header
            hdu['DSVAL2  '] = "CIRCLE("+str(sra)+","+str(sdec)+","+str(rad)+")"

            fh.close()

            expr = "ARCCOS(SIN(DEC*#deg)*SIN("+str(bdec)+\
                "*#deg)+COS(DEC*#deg)*COS("+str(bdec)+"*#deg)*COS((RA-"+\
                str(bra)+")*#deg))/#deg<"+str(brad)+".AND.TIME>"+str(tstart)+".AND.TIME<"+str(tstop)


        if self.state == "running":

            try:
                self.putlog("***Running FSELECT to produce event file for the background region***")
                subprocess.call(["fselect",evfile,'!'+bkg_ef,expr])
            except:
                self.putlog("Error occured when running FSELECT for backgrnd.")
                self.stop()

 
        if self.state == "running":

            self.putlog("***Running GTBIN to produce spectrum for the source region***")

            time.sleep(0.05)
            evbin['algorithm'] = 'PHA1'
            evbin['ebinalg'] = 'LOG'
            evbin['evfile'] = src_ef
            evbin['scfile'] = scfile
            evbin['outfile'] = srcf
            evbin['tstart'] = tstart
            evbin['tstop'] = tstop
            evbin['emin'] = emin
            evbin['emax'] = emax
            evbin['enumbins'] = enbin
            evbin['chatter'] = '10'
            
            self.putlog(evbin.command())

            catchError = "at the top level:"
            gterr = False
            inf,outf = evbin.runWithOutput(print_command=False)
            for line in outf:
                self.putlog(line)
                if line.find(catchError) != -1:
                    gterr = True

            inf.close()
            outf.close()


            if gterr:
 
               self.putlog("GTBIN error during source region extraction! Exiting...")
               self.state = "stop"

        
        if self.state == "running": 

            evbin['evfile'] = bkg_ef
            evbin['outfile'] = bkgf


            self.putlog("***Running GTBIN to produce spectrum for the background region***")

            time.sleep(0.05)
            
            self.putlog(evbin.command())

            catchError = "at the top level:"
            gterr = False
            inf,outf = evbin.runWithOutput(print_command=False)
            for line in outf:
                self.putlog(line)
                if line.find(catchError) != -1:
                    gterr = True


            inf.close()
            outf.close()


            if gterr:
               
               self.putlog("GTBIN error during background region extraction! Exiting...")
               self.state = "stop"




# response


            fh = pyfits.open(srcf,mode='update')
            hdu = fh[1].header
#            hdu['DSVAL2  '] = "CIRCLE("+str(sra)+ ","+str(self.analysis.dec)+","+ \
#                                      str(self.analysis.obs_pars["roi"])+")"
            

        if self.state == "running": 

            self.putlog( "***Running gtrspgen (response generator)***")

            rspf = outroot+'.rsp'
            gtrsp['respalg'] = "PS"
            gtrsp['specfile'] = srcf
            gtrsp['scfile'] = scfile
            gtrsp['thetacut'] = thetamax
            gtrsp['outfile'] = rspf
            gtrsp['irfs'] = irfs
            gtrsp['dcostheta'] = dcostheta
            gtrsp['emin'] = 100.0
            gtrsp['emax'] = 300000.0
            gtrsp['enumbins'] = 100
            gtrsp['chatter'] = 0


            self.putlog(gtrsp.command())

            catchError = "at the top level:"
            gterr = False
            inf,outf = gtrsp.runWithOutput(print_command=False)
            for line in outf:
                self.putlog(line)
                if line.find(catchError) != -1:
                    gterr = True


#            self.putlog(str(gterr))
            inf.close()
            outf.close()


            if gterr:

               self.putlog("GTRSPGEN error! Exiting...")
               self.stop()

            time.sleep(0.05)

# PSF

        if self.state == "running":            

            self.putlog("***Running gtpsf (PSF generator)***")
            psff = outroot+'_psf.fits'
            gtpsf['expcube'] = cube
            gtpsf['dec'] = sdec
            gtpsf['ra'] = sra
            gtpsf['outfile'] = psff
            gtpsf['irfs'] = irfs
            gtpsf['emin'] = 100.0
            gtpsf['emax'] = 300000.0
            gtpsf['nenergies'] = 101
            gtpsf['thetamax'] = thetamax
            gtpsf['ntheta'] = int(thetamax/dcostheta)
            gtpsf['chatter'] = 0

            self.putlog(gtpsf.command())

            catchError = "at the top level:"
            gterr = False
            inf,outf = gtpsf.runWithOutput(print_command=False)
            for line in outf:
                self.putlog(line)
                if line.find(catchError) != -1:
                    gterr = True


            inf.close()
            outf.close()


            if gterr:

               self.putlog("GTPSF error! Exiting...")
               self.stop()
               


# ARF

        if self.state == "running":            

            arff = outroot+".arf"
            try:

                out = arfcreate(arff,rad,rspf,psff)
                self.putlog(out)
            except:
                self.putlog("ARFCREATE error! Exiting..." )
                self.stop()


            hdu['RESPFILE'] = rspf
            hdu['BACKFILE'] = bkgf
            hdu['ANCRFILE'] =  arff
            hdu['BACKSCAL'] = 1.0
            fh.flush()
            fh.close()

            fh = pyfits.open(bkgf,mode='update')
            hdu = fh[1].header
            hdu['BACKSCAL'] = (brad/rad)**2
            fh.flush()
            fh.close()
#            self.logit(out)


# Clean up        

        try:
            os.system('rm -f '+psff)
            os.system('rm -f src'+pid+'*')
            os.system('rm -f bkg'+pid+'*')
            os.system('rm -f ev'+pid+'*')   
            os.system('rm -f rsp'+pid+'*')
        except:
            pass

        if self.state == "running": self.state = "done"
        if self.state == "stop": self.state = "stopped"
