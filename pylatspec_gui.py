#
#
#   History -----
#   
#  23.09.2013 ---- 
#  Fixed some issues
#  Moving on to use menu insted of buttons
#  
#  20.11.2013
#
#  Improving logging by using queues
#
#
#

import Tkinter as tk
#import ttk
import tkFileDialog
import os
import tkFont
import time
from fgltools import get_brightest_sources
import subprocess
import threading
import Queue



class LatSpecApp(tk.Frame):

    """ Latspec GUI class. Handles graphics for Latspec tool for 
    LAT data Xspec style analysis."""
        
    def __init__(self, master=None,analysis=None):
        
        self.analysis = analysis
        self.master = master
        master.protocol("WM_DELETE_WINDOW",self.quit_handler)
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.logQueue = Queue.Queue()
        self.logerrQueue = Queue.Queue()
        self.logblueQueue = Queue.Queue()
        self.logThread = threading.Thread(target = self.logger,args=())
        self.logLock = threading.Lock()
        self.logThread.deamon = True
        self.stop = False
        self.createWidgets()

#  logging stuff


        self.logThread.start()

    def quit_handler(self):

        self.quit_gui()
        

    def logger(self):
        
        import time
        while not self.stop:
            self.logLock.acquire()

            if not self.logQueue.empty():
                logtext = self.logQueue.get()
                self.logit_to_text(logtext)
                self.hline()

            if not self.logerrQueue.empty():

                logtext = self.logerrQueue.get()
                self.logerr_to_text(logtext)
                self.hline()

            if not self.logblueQueue.empty():
                logtext = self.logblueQueue.get()                
                self.logblue_to_text(logtext)
                self.hline()                

            self.logLock.release()
            time.sleep(0.1)


            

    def logit(self,s):


        self.logQueue.put(s)


    def logerr(self,s):


        self.logerrQueue.put(s)


    def logblue(self,s):


        self.logblueQueue.put(s)

         

    def createWidgets(self):
    
        from ScrolledText import ScrolledText

        top=self.winfo_toplevel()                
        top.rowconfigure(0, weight=1)            
        top.columnconfigure(0, weight=1)         
        self.rowconfigure(0, weight=1)           
        self.columnconfigure(0, weight=1)        


# ****** Define threads

#        self.filter_events_thread = threading.Thread(target=self.filterevents,args=())
#        self.get_cube_thread = threading.Thread(target=self.getCube,args=())
#        self.get_image_thread = threading.Thread(target=self.createimage,args=())
#        self.get_lc_thread = threading.Thread(target=self.get_full_lc,args=())
#        self.get_spectra_thread = threading.Thread(target=self.get_spectra,args=())
#        self.ds9_thread = ds9thread()


# ***** Definition of vars ****

        self.skipch = False
        self.basename_entry = tk.StringVar()
        self.date_extracted = tk.StringVar()
        self.tmin_entry = tk.StringVar()
        self.tmax_entry = tk.StringVar()
        self.ltcube_file= tk.StringVar()
        self.emin_entry = tk.StringVar()
        self.emax_entry = tk.StringVar()
#        self.emax = self.analysis.obs_pars["emax"]
#        self.emin = self.analysis.obs_pars["emin"]
        self.lc_emin_entry = tk.StringVar()
        self.lc_emax_entry = tk.StringVar()
        self.lc_pl_index = tk.StringVar()
        self.lc_index_fixed = tk.IntVar()
        self.lc_emax = self.analysis.emax
        self.lc_emin = self.analysis.emin
        self.zmax_entry = tk.StringVar()
        self.binsz_entry = tk.StringVar()
        self.dcostheta_entry = tk.StringVar()
        self.thetacut_entry = tk.StringVar()
        self.src_spc = tk.StringVar()
        self.cat_source = tk.StringVar()
        self.flux_entry = tk.StringVar()
        self.nchan_entry = tk.StringVar()
        self.rootname_entry = tk.StringVar()
        self.modelvar = tk.StringVar()
        self.filtered_events = tk.StringVar()
        self.image_file = tk.StringVar()
        self.lc_file = tk.StringVar()        
        self.lc_bin = tk.StringVar()
        self.irfs = tk.StringVar()
        self.lc_bin.set("month")
        self.lc_tres = 30*86400
        self.lc_file.set("lc.fits")
        self.lc_pl_index.set("2.5")
        self.lc_index_fixed.set(1)

        self.src_ra_entry = tk.StringVar()
        self.bkg_ra_entry = tk.StringVar()
        self.src_dec_entry = tk.StringVar()
        self.bkg_dec_entry = tk.StringVar()
        self.src_rad_entry = tk.StringVar()
        self.bkg_rad_entry = tk.StringVar()

        
# ***** Analysis Frame *********

        self.AnalysisFrame = tk.Frame(self,padx=0,pady=0)
        self.AnalysisFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.AnalysisFrame.grid_columnconfigure(0,weight=1)
        self.AnalysisFrame.grid_rowconfigure(0,weight=1)

# ***** Navigation Frame *********

        self.NavFrame = tk.Frame(self,padx=0,pady=0)
        self.NavFrame.grid(column=0,row=1,sticky=tk.N+tk.S+tk.E+tk.W)
        self.NavFrame.grid_columnconfigure(0,weight=1)
        self.NavFrame.grid_columnconfigure(1,weight=1)
        self.NavFrame.grid_columnconfigure(2,weight=1)
        self.NavFrame.grid_columnconfigure(3,weight=1)

# ******* Log Frame *******
        self.logfont = tkFont.Font(family="Courier New", size=11)
        self.LogFrame = tk.LabelFrame(self,text="Log",padx=5,pady=5,labelanchor=tk.N)
        self.LogFrame.grid(column=0,row=2,sticky=tk.N+tk.S+tk.E+tk.W)
        self.LogText = ScrolledText(self.LogFrame,bg='white',font=self.logfont)
        self.LogText.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.Y)

        self.logit("Welcome to LATSPEC, Xspec style analysis of FERMI LAT data.")
        if self.analysis.haveCatalog:
            self.logit("Using 2FGL catalog: "+self.analysis.catalog)
        else:
            self.logit("2FGL catalog (and related functionality) is not available.")

        if self.analysis.havedata:
            self.log_data_info()

# *** Bottom Panel

        self.BottomFrame = tk.LabelFrame(self,padx=5,pady=5)
        self.BottomFrame.grid(column=0,row=3,sticky=tk.N+tk.S+tk.E+tk.W)
        self.BottomFrame.grid_columnconfigure(0,weight=1)
        self.BottomFrame.grid_columnconfigure(1,weight=1)
        self.BottomFrame.grid_columnconfigure(2,weight=1)
        self.BottomFrame.grid_columnconfigure(3,weight=1)


        self.SaveLogButton = tk.Button(self.BottomFrame,text="Save Log",
                                   command=self.save_log)
        self.SaveLogButton.grid(column=0,row=0,sticky='EWNS')
        self.ClearLogButton = tk.Button(self.BottomFrame,text="Clear Log",
                                    command=self.clear_log)
        self.ClearLogButton.grid(column=1,row=0,sticky='EWNS')
        self.QuitButton = tk.Button(self.BottomFrame,text="Quit",
                                command=self.quit_gui)
        self.QuitButton["text"] = "Quit"
        self.QuitButton["command"] =  self.quit_gui
        self.QuitButton.grid(column=3,row=0,sticky='EWNS')
        
        self.HelpButton = tk.Button(self.BottomFrame,text="Help",command=self.open_help)
        self.HelpButton.grid(column=2,row=0,sticky='EWNS')

        self.populate_cat_source_menu()
        self.set_spectrum_panel()
        self.set_filter_panel()
        self.set_lc_panel()


# **** Analysis Panels pack into Analysis (top) frame ***


# ****** Settings Panel

        self.SettingsFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                       relief=tk.GROOVE,labelanchor=tk.N,
                                       text="Settings",pady=5)

        
        self.DataFr = tk.LabelFrame(self.SettingsFrame,bd=1,relief=tk.GROOVE,
                                text="Data")

    
        self.DataDirButton = tk.Button(self.DataFr,text="...",
                                   command=self.askdirectory,
                                   relief=tk.GROOVE)
        self.DataDirButton.grid(column=0,row=0,sticky='EW',pady=2,padx=2)
        self.DataShowButton = tk.Button(self.DataFr,text="Data Info",
                                    command=self.log_data_info,
                                    relief=tk.GROOVE)
        self.DataShowButton.grid(column=1,row=0,sticky='EW',pady=2,padx=2)
        self.DataDirLabel = tk.Label(self.SettingsFrame)
#        self.DataDirLabel.grid(column=0,row=0,sticky='EW')

        self.DataFr.grid(column=0,row=0,sticky='EWNS',pady=3,padx=3)
        self.DataFr.grid_columnconfigure(0,weight=1)
        self.DataFr.grid_columnconfigure(1,weight=1)


        self.CatalogFr = tk.LabelFrame(self.SettingsFrame,bd=1,
                                   relief=tk.GROOVE,
                                   text="Catalog")
        self.CatButton = tk.Button(self.CatalogFr,text="...",
                               command=self.askfile,relief=tk.GROOVE)
#        self.CatLabel = tk.Label(self.SettingsFrame,text=self.analysis.catalog)
#        self.CatLabel.grid(column=1,row=1,columnspan=4,sticky='W')
        self.CatButton.grid(column=0,row=0,sticky='EW',pady=2,padx=2)
        self.CatFluxLabel = tk.Label(self.CatalogFr,text="Flux Threshold")
        self.CatFluxEntry = tk.Entry(self.CatalogFr,
                                 textvariable=self.flux_entry)
        
        self.CatFluxLabel.grid(column=1,row=0,sticky='EW',pady=2,padx=2)
        self.CatFluxEntry.grid(column=2,row=0,sticky='EW',pady=2,padx=2)
        self.CatFluxEntry.bind("<Return>",self.flux_tres_rtrn)
        self.flux_entry.set(self.analysis.fluxTres)

        self.CatalogFr.grid(column=0,row=1,sticky='EWNS',pady=3,padx=3)
        self.CatalogFr.grid_columnconfigure(0,weight=1)
        self.CatalogFr.grid_columnconfigure(1,weight=2)
        self.CatalogFr.grid_columnconfigure(2,weight=2)


        self.ParsFr = tk.LabelFrame(self.SettingsFrame,bd=1,
                                relief=tk.GROOVE,
                                text="Parameters")
    

        self.BinszLabel = tk.Label(self.ParsFr,text='binsz:')
        binsz_isok_command = self.register(self.binsz_isok)
        self.BinszEntry = tk.Entry(self.ParsFr,
                               textvariable=self.binsz_entry,validate='all',
                               validatecommand=(binsz_isok_command,'%i','%s','%P'))
    
        self.BinszLabel.grid(column=0,row=0,sticky='E',pady=2,padx=2)
        self.BinszEntry.grid(column=1,row=0,sticky='EW',pady=2,padx=2)

        self.ZmaxLabel = tk.Label(self.ParsFr,text='zmax:')
        zmax_isok_command = self.register(self.zmax_isok)
        self.FilterZmaxEntry = tk.Entry(self.ParsFr,
                                    textvariable=self.zmax_entry,validate='all',
                                    validatecommand=(zmax_isok_command,'%i','%s','%P'))
        self.ZmaxLabel.grid(column=0,row=1,sticky='E',pady=2,padx=2)
        self.FilterZmaxEntry.grid(column=1,row=1,sticky='EW',pady=2,padx=2)


        self.DcosthetaLabel = tk.Label(self.ParsFr,text='dcostheta:')
        dcostheta_isok_command = self.register(self.dcostheta_isok)
        self.DcosthetaEntry = tk.Entry(self.ParsFr,
                          textvariable=self.dcostheta_entry,
                          validate='all',
                          validatecommand=(dcostheta_isok_command,'%i','%s','%P'))
        self.DcosthetaLabel.grid(column=0,row=2,sticky='E',pady=2,padx=2)
        self.DcosthetaEntry.grid(column=1,row=2,sticky='EW',pady=2,padx=2)

        self.ThetacutLabel = tk.Label(self.ParsFr,text='thetacut:')
        thetacut_isok_command = self.register(self.thetacut_isok)
        self.ThetacutEntry = tk.Entry(self.ParsFr,
                         textvariable=self.thetacut_entry,validate='all',
                         validatecommand=(thetacut_isok_command,'%i','%s','%P'))
        self.ThetacutLabel.grid(column=0,row=3,sticky='E',pady=2,padx=2)
        self.ThetacutEntry.grid(column=1,row=3,sticky='EW',pady=2,padx=2)

#        self.irfs.trace("w",self.cat_source_change)
        self.IrfsLabel = tk.Label(self.ParsFr,text='IRFS:')
        self.IrfsLabel.grid(column=0,row=4,sticky='E',pady=2,padx=2)
        self.irfs.trace("w",self.irfs_change)
        self.IrfsMenu = tk.OptionMenu(self.ParsFr,self.irfs,"")
        self.IrfsMenu.config(width=15)
        self.IrfsMenu.grid(column=1,row=4,sticky='EWNS')


        self.ParsFr.grid(column=1,row=0,rowspan=3,sticky='EWNS',pady=3,padx=3)
        self.ParsFr.grid_columnconfigure(0,weight=1)
        self.ParsFr.grid_columnconfigure(1,weight=1)
        self.ParsFr.grid_rowconfigure(0,weight=1)
        self.ParsFr.grid_rowconfigure(1,weight=1)
        self.ParsFr.grid_rowconfigure(2,weight=1)
        self.ParsFr.grid_rowconfigure(3,weight=1)
        self.ParsFr.grid_rowconfigure(4,weight=1)

        self.BasenameFr = tk.LabelFrame(self.SettingsFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Basename")
        self.DataBasenameEntry = tk.Entry(self.BasenameFr,
                                      textvariable=self.basename_entry)
        self.DataBasenameEntry.bind("<Return>",self.basename_return)
        self.DataBasenameEntry.grid(column=0,row=0,sticky='EW',pady=2,padx=2)
        self.basename_entry.set(self.analysis.basename)

        self.BasenameFr.grid(column=0,row=2,sticky='EWNS',pady=3,padx=3)
        self.BasenameFr.grid_columnconfigure(0,weight=1)


        self.SettingsFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.SettingsFrame.grid_columnconfigure(0,weight=1)
        self.SettingsFrame.grid_columnconfigure(1,weight=1)
        self.SettingsFrame.grid_rowconfigure(0,weight=1)
        self.SettingsFrame.grid_rowconfigure(1,weight=1)
        self.SettingsFrame.grid_rowconfigure(2,weight=2)


        self.set_settings_panel()

# ***** Prerequisites (Filter) Panel *************

        self.FilterFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                         relief=tk.GROOVE,labelanchor='n',
                                         padx=5,pady=5,text="Prerequisites")
        self.FilterFrame.grid_columnconfigure(0,weight=3)
        self.FilterFrame.grid_columnconfigure(1,weight=1)
        self.FilterFrame.grid_rowconfigure(0,weight=1)
        self.FilterFrame.grid_rowconfigure(1,weight=1)
        self.FilterFrame.grid_rowconfigure(2,weight=2)
#        self.FilterFrame.grid_rowconfigure(3,weight=1)

        self.DataFr = tk.LabelFrame(self.FilterFrame,bd=1,text="Events")
        self.DataFr.grid_columnconfigure(0,weight=1)
        self.DataFr.grid_columnconfigure(1,weight=1)
        self.DataFr.grid(column=0,row=0,sticky='EW')

        self.DataFilterButton = tk.Button(self.DataFr,
                                      text="Filter Events",relief=tk.GROOVE,
                                      command=self.filterevents)

        self.DataFilterFileLabel = tk.Label(self.DataFr,
                                        textvariable=self.filtered_events)
        self.DataFilterButton.grid(column=1,row=0,sticky='EW')
#        self.DataFilterButton.grid(column=0,row=4,sticky='E')
        self.DataFilterFileLabel.grid(column=0,row=0,sticky='EW')


        self.CubeFr = tk.LabelFrame(self.FilterFrame,bd=1,
                                relief=tk.GROOVE,
                                text="Ltcube")
        self.CubeFr.grid_columnconfigure(0,weight=1)
        self.CubeFr.grid_columnconfigure(1,weight=1)
        self.CubeFr.grid_columnconfigure(2,weight=1)

        self.SourceLtcubeButton = tk.Button(self.CubeFr,text="Run GTLTcube",
                                        command=self.getCube,relief=tk.GROOVE)
        self.SourceLtcubeFileLabel = tk.Label(self.CubeFr,
                                          textvariable=self.ltcube_file)
        self.SourceLtcubeButton.grid(column=2,row=0,sticky='EW',pady=2,padx=2)
        self.ltcube_file.set(self.analysis.ltcube)
        self.LtcubeChooseBtn = tk.Button(self.CubeFr,text="Load Cube",
                                         relief=tk.GROOVE,
                                         command=self.ask_cube)
        self.LtcubeChooseBtn.grid(column=1,row=0,sticky='EW')
        self.SourceLtcubeFileLabel.grid(column=0,row=0,sticky='EW')
        self.rootname_entry.trace("w",self.set_spectrum_panel)        
        
        self.CubeFr.grid(column=0,row=1,sticky='EWNS')

        self.set_filter_panel()

# ****** Image Frame (now a part of the Prerequisites Panel) *******

        self.ImageFrame = tk.LabelFrame(self.FilterFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Image")

        self.ImageFrame.grid_columnconfigure(0,weight=1)
        self.ImageFrame.grid_columnconfigure(1,weight=1)
        self.ImageFrame.grid_columnconfigure(2,weight=1)
#        self.ImageFrame.grid_rowconfigure(0,weight=1)
#        self.ImageFrame.grid_rowconfigure(1,weight=1)

        self.ImageCreateButton = tk.Button(self.ImageFrame,
                                       text="Extract Image",relief=tk.GROOVE,
                                       command=self.image_thread)
        self.ImageCreateButton.grid(column=1,row=0,columnspan=2,sticky='EWNS')

        self.ImageLabel = tk.Label(self.ImageFrame,textvariable=self.image_file)
        self.ImageLabel.grid(column=0,row=0,sticky='EWNS')

        self.ImageFrame.grid(column=0,row=2,sticky=tk.N+tk.S+tk.E+tk.W)


        self.RegionsFrame = tk.LabelFrame(self.FilterFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Regions")

        self.RegionsFrame.grid_rowconfigure(0,weight=1)
        self.RegionsFrame.grid_rowconfigure(1,weight=1)
        self.RegionsFrame.grid_rowconfigure(2,weight=1)
        self.RegionsFrame.grid_rowconfigure(3,weight=1)
        self.RegionsFrame.grid_columnconfigure(0,weight=1)
        self.RegionsFrame.grid_columnconfigure(1,weight=1)
        self.RegionsFrame.grid_columnconfigure(2,weight=1)



        self.ImageDS9Button = tk.Button(self.ImageFrame,
                                        text="Run ds9",
                                        command=self.run_ds9,
                                            relief=tk.GROOVE)
        self.ImageDS9Button.grid(column=0,row=1,sticky='EW')

#        self.ImageRegionsButton = tk.Button(self.ImageFrame,
#                                        text="Get regions",
#                                        command=self.get_regions,
#                                            relief=tk.GROOVE)
#        self.ImageRegionsButton.grid(column=0,row=2,sticky='EW')


#        self.src_spc.set("")
#        self.ImageSrcSpcLabel = tk.Label(self.ImageFrame,textvariable=self.src_spc)
#        self.ImageSrcSpcLabel.grid(column=2,row=1)
        self.CatSourceLabel = tk.Label(self.ImageFrame,text="2FGL Source:")
        self.CatSourceLabel.grid(column=1,row=1,sticky='EW')
        self.cat_source.trace("w",self.cat_source_change)
        self.CatSourceMenu = tk.OptionMenu(self.ImageFrame,self.cat_source,"")
        self.CatSourceMenu.config(width=20)
        self.CatSourceMenu.grid(column=2,row=1,sticky='EWNS')


        self.SrcLbl = tk.Label(self.RegionsFrame,text="Source")
        self.SrcRALbl =  tk.Label(self.RegionsFrame,text="RA:")
        self.SrcDECLbl =  tk.Label(self.RegionsFrame,text="DEC:")
        self.SrcRADLbl =  tk.Label(self.RegionsFrame,text="RAD:")

        src_ra_isok_command = self.register(self.src_ra_isok)
        src_dec_isok_command =  self.register(self.src_dec_isok)
        src_rad_isok_command =  self.register(self.src_rad_isok)


        entryw = 6

        self.SrcRAEntry = tk.Entry(self.RegionsFrame,width=entryw,
                                   textvariable=self.src_ra_entry,validate='key',
                         validatecommand=(src_ra_isok_command,'%d','%s','%P'))
        self.SrcDECEntry = tk.Entry(self.RegionsFrame,width=entryw,
                                   textvariable=self.src_dec_entry,validate='key',
                         validatecommand=(src_dec_isok_command,'%d','%s','%P'))
        self.SrcRADEntry = tk.Entry(self.RegionsFrame,width=entryw,
                           textvariable=self.src_rad_entry,validate='key',
                         validatecommand=(src_rad_isok_command,'%d','%s','%P'))
        self.SrcLbl.grid(column=1,row=0,sticky="EWNS")

        self.SrcRALbl.grid(column=0,row=1,sticky="EWNS")
        self.SrcRAEntry.grid(column=1,row=1,sticky="EWNS",pady=8)

        self.SrcDECLbl.grid(column=0,row=2,sticky="EWNS")
        self.SrcDECEntry.grid(column=1,row=2,sticky="EWNS",pady=8)

        self.SrcRADLbl.grid(column=0,row=3,sticky="EWNS")
        self.SrcRADEntry.grid(column=1,row=3,sticky="EWNS",pady=8)


        self.BkgLbl = tk.Label(self.RegionsFrame,text="Bkgrnd")
        self.BkgRALbl =  tk.Label(self.RegionsFrame,text="RA:")
        self.BkgDECLbl =  tk.Label(self.RegionsFrame,text="DEC:")
        self.BkgRADLbl =  tk.Label(self.RegionsFrame,text="RAD:")

        bkg_ra_isok_command  =  self.register(self.bkg_ra_isok)
        bkg_dec_isok_command =  self.register(self.bkg_dec_isok)
        bkg_rad_isok_command =  self.register(self.bkg_rad_isok)

        self.BkgRAEntry = tk.Entry(self.RegionsFrame,width=entryw,
                          textvariable=self.bkg_ra_entry,validate='key',
                          validatecommand=(bkg_ra_isok_command,'%d','%s','%P'))
        self.BkgDECEntry = tk.Entry(self.RegionsFrame,width=entryw,
                           textvariable=self.bkg_dec_entry,validate='key',
                           validatecommand=(bkg_dec_isok_command,'%d','%s','%P'))
        self.BkgRADEntry = tk.Entry(self.RegionsFrame,width=entryw,
                           textvariable=self.bkg_rad_entry,validate='key',
                           validatecommand=(bkg_rad_isok_command,'%d','%s','%P'))
        self.BkgLbl.grid(column=2,row=0,sticky="EWNS")

#        self.BkgRALbl.grid(column=8,row=1,sticky="EWNS")
        self.BkgRAEntry.grid(column=2,row=1,sticky="EWNS",pady=8)

#        self.BkgDECLbl.grid(column=10,row=1,sticky="EWNS")
        self.BkgDECEntry.grid(column=2,row=2,sticky="EWNS",pady=8)

#        self.BkgRADLbl.grid(column=12,row=1,sticky="EWNS")
        self.BkgRADEntry.grid(column=2,row=3,sticky="EWNS",pady=8)



        self.RegionsFrame.grid(column=1,row=0,rowspan=3,sticky=tk.N+tk.S+tk.E+tk.W,padx=8,pady=8)

    
        self.populate_cat_source_menu()

# ****** Lightcurve Frame *******

        self.LcFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                 relief=tk.GROOVE,padx=5,pady=5,
                                 text="Lightcurve",labelanchor='n')

        self.LcFrame.grid_columnconfigure(0,weight=1)
        self.LcFrame.grid_columnconfigure(1,weight=1)
        self.LcFrame.grid_columnconfigure(2,weight=1)
        self.LcFrame.grid_rowconfigure(0,weight=1)
        self.LcFrame.grid_rowconfigure(1,weight=1)

        self.LcFrame1 = tk.LabelFrame(self.LcFrame,bd=1,
                                    relief=tk.GROOVE)
        self.LcFrame1.grid_columnconfigure(0,weight=1)
        self.LcFrame1.grid_columnconfigure(1,weight=1)
        self.LcFrame1.grid_columnconfigure(2,weight=1)
        self.LcFrame1.grid_columnconfigure(3,weight=1)
        self.LcFrame1.grid_columnconfigure(4,weight=1)
        self.LcFrame1.grid_rowconfigure(0,weight=1)
        self.LcFrame1.grid_rowconfigure(1,weight=1)
        self.LcFrame1.grid_rowconfigure(2,weight=1)

        self.LcFrame1.grid(column=0,row=0,columnspan=3,sticky="EWNS")
        self.LcRootnameLabel = tk.Label(self.LcFrame1,bd=1,
                                                 text="Product directory:")

        self.LcRootnameLabel.grid(column=0,row=0,sticky='EWNS')



        self.LcRootnameEntry = tk.Entry(self.LcFrame1,relief=tk.FLAT,
                                        textvariable=self.rootname_entry,
                                        disabledforeground="black",state=tk.DISABLED)
        self.LcRootnameEntry.grid(column=1,row=0,columnspan=3,sticky='EWNS',pady=2)
        self.LcBinLabel = tk.Label(self.LcFrame1,text="Lightcurve binning")
        self.LcBinLabel.grid(column=0,row=2,sticky='EWNS',pady=2)
#        self.LcFileLabel = tk.Label(self.LcFrame1,text="Output File:")
#        self.LcFileLabel.grid(column=0,row=1,sticky='EWNS',pady=2)

#        self.LcFileEntry = tk.Entry(self.LcFrame1,textvariable=self.lc_file)
#        self.LcFileEntry.grid(column=1,row=1,columnspan=3,sticky='EWNS',pady=2)
        self.lc_bin.trace("w",self.lc_bin_change)
        self.LcBinMenu = tk.OptionMenu(self.LcFrame1,self.lc_bin,"")
        self.LcBinMenu.config(width=15)
        self.LcBinMenu.grid(column=1,row=2,columnspan=3,sticky='EWNS',pady=2)
        self.LcBinMenu["menu"].delete(0, tk.END)
        self.lc_bin.set("month")
        for s in ["month","week","day"]: 
            self.LcBinMenu["menu"].add_command(label=s, 
                                           command=lambda temp = s: 
                                           self.LcBinMenu.setvar(self.LcBinMenu.cget("textvariable"),
                                             value = temp))
        self.LcShowBtn = tk.Button(self.LcFrame,text="Show Lightcurve",
                                   relief=tk.GROOVE,command=self.plot_lc)
        self.LcShowBtn.grid(column=1,row=1,sticky='EWNS')
        self.LcExtBtn = tk.Button(self.LcFrame,
                                  text="Extract Lightcurve",
                                  relief=tk.GROOVE,
                                  command=self.get_full_lc)
        self.SaveLcBtn = tk.Button(self.LcFrame,
                                   text="Save lightcurve",
                                   command=self.save_lightcurve,height=1,
                                   relief=tk.GROOVE)


        self.LcExtBtn.grid(column=0,row=1,sticky='EWNS')
        self.SaveLcBtn.grid(column=2,row=1,sticky='EWNS')


        emin_isok_command = self.register(self.emin_isok)
        emax_isok_command = self.register(self.emax_isok)
        

        self.LcEnergyRangeLabel = tk.Label(self.LcFrame1,text='Energy Range:')
        self.LcELabel = tk.Label(self.LcFrame1,text='-')
        self.LcEunitLabel = tk.Label(self.LcFrame1,text='MeV')
        self.LcEminEntry = tk.Entry(self.LcFrame1,textvariable=self.lc_emin_entry,
                                validate='all',
                                validatecommand=(emin_isok_command,'%P'))
        self.LcEmaxEntry = tk.Entry(self.LcFrame1,
                                textvariable=self.lc_emax_entry,validate='all',
                                validatecommand=(emax_isok_command,'%P'))


        self.LcEnergyRangeLabel.grid(column=0,row=3,sticky='EWNS',pady=2)
        self.LcEminEntry.grid(column=1,row=3,sticky='EWNS',pady=2)
        self.LcELabel.grid(column=2,row=3,sticky='EWNS',pady=2)
        self.LcEmaxEntry.grid(column=3,row=3,sticky='EWNS',pady=2)
        self.LcEunitLabel.grid(column=4,row=3,sticky='EWNS',pady=2)
    
        self.lc_emin_entry.set(str(self.analysis.emin))
        self.lc_emax_entry.set(str(self.analysis.emax))
    
        self.LcEmaxEntry.bind("<Return>",self.lc_emax_enter)
        self.LcEminEntry.bind("<Return>",self.lc_emin_enter)
        self.LcPLindLabel = tk.Label(self.LcFrame1,text="Powerlaw Index:")
        self.LcPLindEntry = tk.Entry(self.LcFrame1,textvariable=self.lc_pl_index,width=5)
        self.LcPLindLabel.grid(column=0,row=4,sticky='EWNS',pady=8)
        self.LcPLindEntry.grid(column=1,row=4,sticky='EWNS',pady=8)
        self.LcIndFixCB = tk.Checkbutton(self.LcFrame1,text="fixed",variable=self.lc_index_fixed)
        self.LcIndFixCB.grid(column=2,row=4,columnspan=2,sticky='EWN',pady=12)
        

        
# ****** Spectrum Frame *******
        
        self.SpectrumFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                       relief=tk.GROOVE,padx=5,pady=5,
                                       text="Spectrum",labelanchor='n')

        self.SpectrumFrame.grid_columnconfigure(0,weight=1)
        self.SpectrumFrame.grid_columnconfigure(1,weight=1)
        self.SpectrumFrame.grid_columnconfigure(2,weight=1)
#        self.SpectrumFrame.grid_columnconfigure(3,weight=1)
#        self.SpectrumFrame.grid_columnconfigure(4,weight=1)
        self.SpectrumFrame.grid_rowconfigure(0,weight=2)
        self.SpectrumFrame.grid_rowconfigure(1,weight=1)
        self.SpectrumFrame.grid_rowconfigure(2,weight=2)
        

        self.SpFrame = tk.LabelFrame(self.SpectrumFrame,bd=1,
                                    relief=tk.GROOVE)


        self.SpFrame.grid(column=0,row=0,columnspan=3,sticky="EWNS")

        self.SpFrame.grid_columnconfigure(0,weight=3)
        self.SpFrame.grid_columnconfigure(1,weight=10)
        self.SpFrame.grid_columnconfigure(2,weight=1)
        self.SpFrame.grid_columnconfigure(3,weight=10)
        self.SpFrame.grid_columnconfigure(4,weight=2)

        self.SourceRootnameLabel = tk.Label(self.SpFrame,bd=1,
                                                 text="Product directory:")

        self.SourceRootnameLabel.grid(column=0,row=0,sticky='EWNS')



        self.SourceRootnameEntry = tk.Entry(self.SpFrame,relief=tk.FLAT,
                                        textvariable=self.rootname_entry,
                                            disabledforeground="black")
        self.rootname_entry.set(self.analysis.name)
        self.rootname_entry.trace("w",self.rootname_change)
        self.SourceRootnameEntry.grid(column=1,row=0,columnspan=4,sticky='EW')
        self.SourceRootnameEntry["state"] = tk.DISABLED
    
        self.SourceCountsButton = tk.Button(self.SpectrumFrame,
                                            text="Plot spectrum/background",
                                        command=self.show_spectra,height=1,
                                            relief=tk.GROOVE)
        self.SourceGetspcButton = tk.Button(self.SpectrumFrame,
                                        text="Extract spectrum",
                                        command=self.get_spectra_thr,height=1,
                                            relief=tk.GROOVE)
        self.SaveSpecBtn = tk.Button(self.SpectrumFrame,
                                        text="Save spectrum",
                                        command=self.save_spectrum,height=1,
                                            relief=tk.GROOVE)
        
        self.SourceCountsButton.grid(column=1,row=1,sticky='EWNS')
        self.SourceGetspcButton.grid(column=0,row=1,sticky='EWNS')
        self.SaveSpecBtn.grid(column=2,row=1,sticky='EWNS')
        self.SourceChannelsLabel = tk.Label(self.SpFrame,text="Channels:")
        self.SourceChannelsEntry = tk.Entry(self.SpFrame,textvariable=self.nchan_entry,width=3)
        self.SourceChannelsLabel.grid(column=0,row=2,sticky='E')
        self.SourceChannelsEntry.grid(column=1,row=2,sticky='W')
        self.nchan_entry.set(self.analysis.nchan)


        self.TimeRangeLabel = tk.Label(self.SpFrame,text='Time Range:')
        tmin_isok_command = self.register(self.tmin_isok)
        tmax_isok_command = self.register(self.tmax_isok)
        self.FilterTminEntry = tk.Entry(self.SpFrame,
                                    textvariable=self.tmin_entry,validate='all',
                                    validatecommand=(tmin_isok_command,'%i','%s','%P'))

        self.FilterTmaxEntry = tk.Entry(self.SpFrame,
                                    textvariable=self.tmax_entry,validate='all',
                                    validatecommand=(tmax_isok_command,'%i','%s','%P'))

        self.TimeRangeLabel.grid(column=0,row=1,sticky='EWNS')

        self.FilterTLabel = tk.Label(self.SpFrame,text='-')
        self.FilterTunitLabel = tk.Label(self.SpFrame,text='MET,s')
        self.FilterTLabel.grid(column=2,row=1,sticky='EW')
        self.FilterTminEntry.grid(column=1,row=1,sticky='EW')
        self.FilterTmaxEntry.grid(column=3,row=1,sticky='EW')
        self.FilterTunitLabel.grid(column=4,row=1,sticky='EW')


        self.set_spectrum_panel()

# ****** Xspec Frame ( now part of the Spectrum panel)******
        
        self.XspecFrame = tk.LabelFrame(self.SpectrumFrame,bd=1,
                                    relief=tk.GROOVE,text="Xspec")

        self.XspecFrame.grid_columnconfigure(0,weight=1)
        self.XspecFrame.grid_columnconfigure(1,weight=1)
        self.XspecFrame.grid_columnconfigure(2,weight=1)
        self.XspecFrame.grid_columnconfigure(3,weight=1)

        self.XspecModelLabel = tk.Label(self.XspecFrame,text="Model")
        list = ('','PowerLaw','LogParabola','PLExpCutoff')
        self.modelvar.trace("w",self.model_change)
        self.modelvar.set(self.analysis.spectrum_type)
        self.XspecModelMenu = tk.OptionMenu(self.XspecFrame,self.modelvar,*list)
        self.XspecModelLabel.grid(column=2,row=0,sticky='EW')
        self.XspecModelMenu.grid(column=3,row=0,columnspan=2,sticky='EW')
        self.XspecRunButton = tk.Button(self.XspecFrame,
                                        relief=tk.GROOVE,
                                        text = "Start Xspec")
        self.XspecRunButton["command"] = self.analyse
        self.XspecRunButton.grid(column=0,row=0,sticky='EW')
#        self.XspecRunButton["state"] = tk.DISABLED

        self.XspecPromptLabel = tk.Label(self.XspecFrame,text="xspec>")
        self.XspecPromptLabel.grid(column=0,row=2,sticky='E')
        self.xspec_prompt = tk.StringVar()
        self.XspecPromptEntry = tk.Entry(self.XspecFrame,textvariable=self.xspec_prompt)
        self.xspec_prompt.set("")
        self.XspecPromptEntry.grid(column=1,row=2,columnspan=4,sticky='EW')
        self.XspecPromptEntry["bg"] = 'white'
        self.XspecPromptEntry.bind("<Return>",self.xspec_prompt_return)        
        self.XspecPromptEntry["state"]=tk.DISABLED


        self.FilterEnergyRangeLabel = tk.Label(self.XspecFrame,text='Fit Energy Range:')


 
        self.FilterELabel = tk.Label(self.XspecFrame,text='-')

        self.FilterEunitLabel = tk.Label(self.XspecFrame,text='MeV')
        self.FilterEminEntry = tk.Entry(self.XspecFrame,textvariable=self.emin_entry,
                                    validate='all',
                                    validatecommand=(emin_isok_command,'%P'))
        self.FilterEmaxEntry = tk.Entry(self.XspecFrame,
                                    textvariable=self.emax_entry,validate='all',
                                    validatecommand=(emax_isok_command,'%P'))

        self.FilterEnergyRangeLabel.grid(column=0,row=1,sticky='E')
        self.FilterEminEntry.grid(column=1,row=1,sticky='EW')
        self.FilterELabel.grid(column=2,row=1,sticky='EW')
        self.FilterEmaxEntry.grid(column=3,row=1,sticky='EW')

        self.FilterEunitLabel.grid(column=4,row=1,sticky='EW')
        
        self.FilterEmaxEntry.bind("<Return>",self.emax_enter)
        self.FilterEminEntry.bind("<Return>",self.emin_enter)

        self.XspecFrame.grid(column=0,row=4,columnspan=5,sticky='EW')

#   End of Spectrum frame definition


        self.FilterFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.LcFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.SpectrumFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.SettingsFrame.lift()

#  Navigation Buttons

        self.NavSettingsBtn = tk.Button(self.NavFrame,text="Settings",
                                        command=self.nav_settings_btn)
        self.NavPrerequisitesBtn = tk.Button(self.NavFrame,text="Prerequisites",
                                        command=self.nav_prerequisites_btn)
        self.NavLightcurveBtn = tk.Button(self.NavFrame,text="Lightcurve",
                                        command=self.nav_lightcurve_btn)
        self.NavSpectrumBtn = tk.Button(self.NavFrame,text="Spectrum",
                                        command=self.nav_spectrum_btn)

        
        self.NavSettingsBtn.grid(column=0,row=0,sticky='EWNS')
        self.NavPrerequisitesBtn.grid(column=1,row=0,sticky='EWNS')
        self.NavLightcurveBtn.grid(column=2,row=0,sticky='EWNS')
        self.NavSpectrumBtn.grid(column=3,row=0,sticky='EWNS')

        self.nav_settings_btn()
        

    def open_help(self):
        
        from latspec_help import help_thread

        self.HelpButton["state"] = tk.DISABLED

        self.helpthrd = help_thread()
        self.helpthrd.start()
            
        helpwait = threading.Thread(target=self.help_wait,args=())
        helpwait.start()

    def help_wait(self):
            
        import time

        while self.helpthrd.state == "on":
            time.sleep(1.0)
                
        try:

            self.HelpButton["state"] = tk.NORMAL
        
        except:
            pass


#
# Navigation button commands



    def nav_settings_btn(self):
       
        self.NavSettingsBtn["text"] = ">>Settings<<"
        self.SettingsFrame.lift()
        self.NavPrerequisitesBtn["text"] = "Prerequisites"
        self.NavLightcurveBtn["text"] = "Lightcurve"
        self.NavSpectrumBtn["text"] = "Spectrum"


    def nav_prerequisites_btn(self):
       
        self.FilterFrame.lift()
        self.NavPrerequisitesBtn["text"] = ">>Prerequisites<<"
        self.NavLightcurveBtn["text"] = "Lightcurve"
        self.NavSpectrumBtn["text"] = "Spectrum"
        self.NavSettingsBtn["text"] = "Settings"

        
    def nav_lightcurve_btn(self):
       
        self.LcFrame.lift()
        self.NavLightcurveBtn["text"] = ">>Lightcurve<<"
        self.NavPrerequisitesBtn["text"] = "Prerequisites"
        self.NavSpectrumBtn["text"] = "Spectrum"
        self.NavSettingsBtn["text"] = "Settings"


    def nav_spectrum_btn(self):
       
        self.SpectrumFrame.lift()
        self.NavSpectrumBtn["text"] = ">>Spectrum<<"
        self.NavLightcurveBtn["text"] = "Lightcurve"
        self.NavSettingsBtn["text"] = "Settings"
        self.NavPrerequisitesBtn["text"] = "Prerequisites"

        
#  ***** End of the create_widgets *****

        
    def set_settings_panel(self):

        self.zmax_entry.set(str(self.analysis.zmax)) 
        self.binsz_entry.set(str(self.analysis.binsz))
        self.dcostheta_entry.set(str(self.analysis.dcostheta))
        self.thetacut_entry.set(str(self.analysis.thetacut))
        self.populate_irfs_menu()

        pass

    def log_data_info(self):

        import pyfits
        import string
        try:

            if self.analysis.havedata:
                
                logstring = ""

                logstring += "Data info:\n"
                logstring += "Data path: "+self.analysis.datapath+"\n"
                
                scf = pyfits.open(self.analysis.scfile)
                logstring += "Extracted:          "+scf[1].header['DATE']+"\n"
                logstring += "Start:              "+scf[1].header['DATE-OBS']+"\n"
                logstring += "Start:              "+scf[1].header['DATE-END']+"\n"
                scf.close()

                logstring += "Time Range:         "+\
                    str(self.analysis.obs_pars["tmin"])+\
                    " - "+str(self.analysis.obs_pars["tmax"])+" MET, sec\n"
                logstring += "Extraction Region:  Circle(RA="+str(self.analysis.obs_pars["RA"])+\
                    ",DEC="+str(self.analysis.obs_pars["DEC"])+",ROI="+\
                    str(self.analysis.obs_pars["roi"])+" deg)\n"
                logstring += "Energy Range:       "+str(self.analysis.obs_pars["emin"])+\
                    " - "+str(self.analysis.obs_pars["emax"])+" MeV"
            else:

                logstring = "No LAT data found."

            self.logit(logstring)



            logstring = "Photon event file(s):\n"
            ff = open('efiles.list','r')
            for li in ff:
                logstring += "    "+string.join(li.split(),'')+"\n"
       
            
            logstring += "Spacecraft data file:\n"
            logstring += "    "+self.analysis.scfile
             
            self.logit(logstring)
            ff.close()


        except:
            pass


        

    def set_filter_panel(self):

        self.ltcube_file.set(self.analysis.ltcube)
        self.filtered_events.set(self.analysis.evfile)
        self.image_file.set(self.analysis.image)

        if self.analysis.havedata:
            self.set_regions_entry()

    def set_regions_entry(self):
        
        self.src_ra_entry.set("{:.3f}".format(self.analysis.ra))
        self.src_dec_entry.set("{:.3f}".format(self.analysis.dec))
        self.src_rad_entry.set("{:.3f}".format(self.analysis.rad))
        self.bkg_ra_entry.set("{:.3f}".format(self.analysis.bkg_ra))
        self.bkg_dec_entry.set("{:.3f}".format(self.analysis.bkg_dec))
        self.bkg_rad_entry.set("{:.3f}".format(self.analysis.bkg_rad))
    
    def set_lc_panel(self,*arg):
        
        pass


    def set_spectrum_panel(self,*arg):
        try:
            if not self.analysis.havedata:
                self.tmin_entry.set("")
                self.tmax_entry.set("")
                return
            else:
                self.rootname_entry.set(self.analysis.name)
                self.tmin_entry.set(str(self.analysis.obs_pars["tmin"]))
                self.tmax_entry.set(str(self.analysis.obs_pars["tmax"]))
                self.emin_entry.set(str(self.analysis.emin))
                self.emax_entry.set(str(self.analysis.emax))
                
                self.XspecPromptEntry["state"] = tk.DISABLED
        except:
            pass
        

    def logit_to_text(self,s):
        
        self.LogText["state"] = tk.NORMAL

        spl = s.split("\n")
        for l in spl:

            self.LogText.insert(tk.END,l+"\n")
        
            self.LogText.see(tk.END)
        self.LogText["state"] = tk.DISABLED


    def logerr_to_text(self,s):
        
        self.LogText["state"] = tk.NORMAL

        spl = s.split("\n")
        for l in spl:

            self.LogText.insert(tk.END,l+'\n')
            self.LogText.update()
            self.LogText.tag_add('err',"%s-2l"%tk.END,"%s-1l"%tk.END)
        
        self.LogText.tag_config('err',foreground="red")
        self.LogText.see(tk.END)
        self.LogText["state"] = tk.DISABLED


    def logblue_to_text(self,s):
        
        self.LogText["state"] = tk.NORMAL
        spl = s.split("\n")
        for l in spl:

            
            self.LogText.insert(tk.END,l+'\n')
            self.LogText.update()
            self.LogText.tag_add('blue',"%s-2l-0c"%tk.END,"%s-1l-0c"%tk.END)
        
        self.LogText.tag_config('blue',foreground="blue")
        self.LogText.see(tk.END)
        self.LogText["state"] = tk.DISABLED
        self.LogText.update()

    def tmin_isok(self,why,vbefore,vafter):
        
        try:
            xxx= float(vafter)
         
        except:
            self.tmin_entry.set(vbefore)
            return False

        if xxx < self.analysis.obs_pars["tmin"]:

            self.logit("TMIN should not be less than start time of the obseration!")
            self.tmin_entry.set(vbefore)
            return False
        return True

    def zmax_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.zmax_entry.set(vbefore)
            return False

        if xxx > 180.0 or xxx < 0.0:

            self.logit("Zmax should be in the [0:180] range.")
            self.zmax_entry.set(vbefore)
            return False
        return True

    def binsz_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.binsz_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logit("Binsz can take only positive values.")
            self.binsz_entry.set(vbefore)
            return False

        self.analysis.binsz = xxx
        return True


    def src_ra_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.src_ra_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logit("Invalid RA value {0}."%xxx)
            self.src_ra_entry.set(vbefore)
            return False
        self.analysis.ra = float(xxx)
        self.catsourceid()
        if int(why) >= 0:
            self.show_cat_sources()
        return True



    def src_dec_isok(self,why,vbefore,vafter):    

        try:
            xxx = float(vafter)
            
        except:
            self.src_dec_entry.set(vbefore)
            return False

        if xxx < -90.0 or xxx > 90.0:

            self.logerr("Invalid DEC value {0}."%vafter)
            self.src_dec_entry.set(vbefore)
            return False
        self.analysis.dec = float(xxx)
        self.catsourceid()
        if int(why)>=0: 
            self.show_cat_sources()
        return True

    def src_rad_isok(self,why,vbefore,vafter):    

        try:
            xxx = float(vafter)
            
        except:
            self.src_rad_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logerr("Invalid Radius value {0}."%xxx)
            self.src_rad_entry.set(vbefore)
            return False
        self.analysis.rad = float(xxx)
        self.catsourceid()
        if int(why)>=0: 
            self.show_cat_sources()
        return True

    def bkg_ra_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.bkg_ra_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logit("Invalid RA value {0}."%xxx)
            self.bkg_ra_entry.set(vbefore)
            return False
        self.analysis.bkg_ra = float(xxx)
        if int(why)>=0: self.show_cat_sources()
        return True

    def bkg_dec_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.bkg_dec_entry.set(vbefore)
            return False

        if xxx < -90.0 or xxx > 90.0:

            self.logerr("Invalid DEC value {0}."%xxx)
            self.bkg_dec_entry.set(vbefore)
            return False
        self.analysis.bkg_dec = float(xxx)
        if int(why)>=0: self.show_cat_sources()
        return True

    def bkg_rad_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.bkg_rad_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logerr("Invalid Radius value {0}."%xxx)
            self.bkg_rad_entry.set(vbefore)
            return False
        self.analysis.bkg_rad = float(xxx)
        if int(why)>=0: self.show_cat_sources()
        return True




    def dcostheta_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.dcostheta_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logit("Dcostheta can take only positive values.")
            self.dcostheta_entry.set(vbefore)
            return False
        self.analysis.dcostheta = xxx
        return True

    def thetacut_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.thetacut_entry.set(vbefore)
            return False

        if xxx < 0.0 or xxx > 90.0:

            self.logit("Thetacut can take only values betweeen 0 and 90.0.")
            self.thetacut_entry.set(vbefore)
            return False
        self.analysis.thetacut = xxx

        return True


    def tmax_isok(self,why,vbefore,vafter):
        
        try:
            xxx= float(vafter)
         
        except:
            self.tmax_entry.set(vbefore)
            return False

        if xxx > self.analysis.obs_pars["tmax"]:

            self.logit("TMAX should not be greater than start time of the obseration!")
            self.tmax_entry.set(vbefore)
            return False
        return True


    def emin_isok(self,vafter):
        

        try:
            xxx= float(vafter)
         
        except:

            return False
        return True

    def emin_enter(self,*arg):

        txt = self.emin_entry.get()
        xxx= float(txt)

        if xxx < self.analysis.obs_pars["emin"] or xxx < 100.0:

            self.logerr("EMIN should not be less than 100 MeV or the minimum energy ("+
                        str(self.analysis.obs_pars["emin"])+" MeV) of the data.")
            self.emin_entry.set(str(max(100.0,self.analysis.emin)))
        
        return

    def lc_emin_enter(self,*arg):

        txt = self.lc_emin_entry.get()
        xxx= float(txt)

        if xxx < self.analysis.obs_pars["emin"]:

            self.logerr("EMIN should not be less than 100 MeV or the minimum energy ("+
                        str(self.analysis.obs_pars["emin"])+" MeV) of the data!")
            self.lc_emin_entry.set(str(self.analysis.emin))

        return

    def emax_isok(self,vafter):

        try:
            xxx= float(vafter)         
        except:
            return False

        return True

    def emax_enter(self,*arg):

        txt = self.emax_entry.get()
        xxx= float(txt)
         
        if xxx > self.analysis.obs_pars["emax"]:

            self.logerr("EMAX should not be greater than maximum energy ("+
                        str(self.analysis.obs_pars["emax"])+
                        " MeV) of the data!")
            self.emax_entry.set(str(self.analysis.emax))

            return
        self.analysis.emax = xxx
        return

    def lc_emax_enter(self,*arg):

        txt = self.lc_emax_entry.get()
        xxx= float(txt)

        if xxx < self.analysis.obs_pars["emin"]:

            self.logerr("EMAX should not be greater than maximum energy("+
                        str(self.analysis.obs_pars["emax"])+" MeV) of the data!")
            self.lc_emax_entry.set(str(self.analysis.emin))

        return


    def populate_cat_source_menu(self):

        if not self.analysis.havedata: return
        try:
            self.CatSourceMenu["menu"].delete(0, tk.END)
            sources = get_brightest_sources(self.analysis.obs_pars["RA"],
                                        self.analysis.obs_pars["DEC"],
                                        self.analysis.obs_pars["roi"],
                                        float(self.analysis.fluxTres),
                                        self.analysis.catalog)
            for s in sources[0]: 
                self.CatSourceMenu["menu"].add_command(label=s, 
                                        command=lambda temp = s: 
                                        self.CatSourceMenu.setvar(self.CatSourceMenu.cget("textvariable"),
                                                                  value = temp))
            self.cat_source.set(self.analysis.fgl_source)
        except:
            pass


    def lc_bin_change(self,*arg):
    
        if self.lc_bin.get() == "month": self.lc_tres = 30*86400
        if self.lc_bin.get() == "week": self.lc_tres = 7*86400
        if self.lc_bin.get() == "day": self.lc_tres = 86400
        self.logit("Set lightcurve time resolution to "+str(self.lc_tres)+" seconds.")
        

    def populate_irfs_menu(self):

        irf = subprocess.Popen(["gtirfs"],stdout=subprocess.PIPE).communicate()[0]
#        irf = fff.readlines()
#        print irf
        
       
        for s in str(irf).split("\n"):
            self.IrfsMenu["menu"].add_command(label=s, 
                                        command=lambda temp = s: 
                                        self.IrfsMenu.setvar(self.IrfsMenu.cget("textvariable"),
                                                                  value = temp))
#            if s[0:self.analysis.irfs.__len__()] == self.analysis.irfs:
            if s.split(" ")[0] == self.analysis.irfs:
                self.irfs.set(s)
 

    def irfs_change(self,*arg):

        st = self.irfs.get()
        s = st.split(" ")
        self.analysis.irfs = s[0]
#        print self.analysis.irfs

    def cat_source_change(self,*arg):

#        from coorconv import loffset,eq2gal,gal2eq,dist
        from fgltools import get_fgl_source_coords

        if self.skipch: return

        sra,sdec = get_fgl_source_coords(self.cat_source.get(),self.analysis.catalog)
#        self.logit(str(sra)+","+str(sdec))

        if sra == -1: return
        self.analysis.ra = float(sra)
        self.analysis.dec = float(sdec)

        self.analysis.set_names()

#        self.lc_file.set(self.analysis.name+'/lc.fits')
        self.set_lc_panel()
        try:
            self.rootname_entry.set(self.analysis.name)
            self.modelvar.set(self.analysis.spectrum_type)
        except:
            pass
        
        self.show_cat_sources()
        self.set_regions_entry()

        try:
            self.xs_proc.terminate()
            self.xs_proc.kill()
        except:
            pass

        try:
            self.xspec_proc.terminate()
            self.xspec_proc.kill()
            self.XspecRunButton["text"] = "Start Xspec"
            self.SourceCountsButton["text"] = "Show counts spectrum/background"
            self.lcplot_proc.terminate()
            self.LcShowBtn["text"] = "Show Lightcurve"
            
        except:
            pass        

        return

    def show_cat_sources(self):

        try:       
            ds9_poll = self.analysis.ds9.poll()            
        except:
            pass
        else:
            if ds9_poll == None:
                self.analysis.write_regions()
                lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,"regions","delete","all"])
                lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,
                                        "regions","file",self.analysis.basename+'.reg'])



    def dist_isok(self,why,vbefore,vafter):
        
        try:
            xxx= float(vafter)
         
        except:
            self.dist_tres.set(vbefore)
            return False

        if xxx < 0.0 :

            self.logit("Source distance threshold should not be less than zero!")
            self.dist_tres.set(vbefore)
            return False

        self.analysis.dist_tres = xxx
        self.analysis.set_names()
        self.cat_source.set(self.analysis.assoc_source)
        self.rootname_entry.set(self.analysis.name)
        return True


    def xspec_session(self):

        import time

        logfile = self.analysis.name+'/'+self.analysis.name+'_xspec.log'
        os.system('rm -f '+logfile+'\n')
        filo = open(logfile,'w')
        self.xs_proc = subprocess.Popen(['xspec'],bufsize=0,stdin=subprocess.PIPE,stdout=filo,stderr=filo)
        infile =  self.xs_proc.stdin

        infile.write('query yes\n')
        infile.write("cd "+self.analysis.name+'\n')
        infile.write('data '+self.analysis.specfile+'\n')   
        self.xs_fil = open(logfile,'r')
        infile.write('ignore **-100000.0 100000000.0-**\n')

        if self.analysis.haveCatalog and self.analysis.fgl_source != "None": 
            if self.analysis.spectrum_type == "PowerLaw": 
                infile.write("model cflux*pow & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 &  {0} 0.01 & 1.0 -1 & \n".format(self.analysis.fgl_powerlaw_index))
            if self.analysis.spectrum_type == "LogParabola": 
                infile.write("model cflux*logpar & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 & {0} 0.01 & {1} 0.01 & {2} 0.01 & 1.0 -1 &\n".format(self.analysis.fgl_powerlaw_index,self.analysis.fgl_beta,self.analysis.fgl_pivot_e*1000.0))
            if self.analysis.spectrum_type == "PLExpCutoff": 
                infile.write("model cflux*powerlaw*spexpcut & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 & {0} 0.01 & 1.0 -1 & {1} 0.01 0.0 0.0 1.0e10 1.0e10 & -0.3 -0.01 &\n".format(self.analysis.fgl_powerlaw_index,float(self.analysis.fgl_cutoff_e)*1000.0))
 
        else:
            infile.write('model cflux*pow & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 &  2.0 0.01 & 10.0 0.1 & \n')
#            print "Here"
        infile.write("renorm\n")
        infile.write("fit\n")
        infile.write("cpd /xw\n")
        infile.write("setplot energy\n")
        infile.write("plot ldata del\n")
        infile.write("iplot\n")
        infile.write("label T \"{0}\"\n".format(self.analysis.assoc_source))
        infile.write("time off\n")
        infile.write("p\n")
        infile.write("q\n")
        time.sleep(0.5)
        self.logit(self.xs_fil.read())
        

    def save_xcm(self):
        try:
            self.xs_proc.stdin.write("save all "+self.analysis.name+".xcm\n")
        except:
            self.logerr("Error saving Xspec session. Try \"Start Xspec\".")
        else:
           self.logit("Xspec session is saved to "+self.analysis.name+".xcm.") 

    def analyse(self):

        import sys
        import time

        try:
            p = self.xs_proc.poll()

        except:
            
            if not os.path.exists(self.analysis.name+'/'+self.analysis.specfile) \
               and not os.path.exists(self.analysis.name+'/'+self.analysis.bkgfile) \
               and not os.path.exists(self.analysis.name+'/'+self.analysis.rspfile)  \
               and not os.path.exists(self.analysis.name+'/'+self.analysis.arffile) :
            
                self.logerr("There is no spectrum yet. Use \"Extract  Spectrum\" button first!")
                return
            else:

                self.XspecRunButton["text"] = "Quit Xspec"
                self.XspecPromptEntry["state"]=tk.NORMAL      
                self.xspec_session()
                time.sleep(0.2)

        else:

            if p == None:

                self.xs_proc.terminate()
                self.xs_proc.kill()
                self.XspecRunButton["text"] = "Start Xspec"
                self.XspecPromptEntry["state"]=tk.DISABLED

            else:
                self.XspecRunButton["text"] = "Quit Xspec"
                self.xspec_session()
                self.XspecPromptEntry["state"]=tk.NORMAL



    def rootname_change(self,*args):
        
        xxx = self.rootname_entry.get()
        self.analysis.specfile = xxx+'_src.pha'
        self.analysis.bkgfile = xxx+'_bkg.pha'
        self.analysis.rspfile = xxx+'.rsp'
        self.analysis.arffile = xxx+'.arf'
        

    def model_change(self,*args):

        xxx = self.modelvar.get()
        if self.analysis.spectrum_type != xxx:
            
            self.analysis.spectrum_type = xxx
            if self.analysis.spectrum_type == "LogParabola":
                if self.analysis.fgl_beta == "INDEF": self.analysis.fgl_beta = 0.5
                if self.analysis.fgl_beta == "INDEF": self.fgl_pivot_e = 200.0
            if self.analysis.spectrum_type == "PLExpCutoff":
                if self.analysis.fgl_cutoff_e == "INDEF": self.analysis.fgl_cutoff_e = 500000.0

    def getCube(self):

        """Generates a livetime cube"""


        self.ltcube_stop = False

        run = 0
        try:

            ltcube_poll = self.ltcube_proc.poll()

        except:
            
            run = 1

        else:

#            print "Mark1 ",ltcube_poll
            if ltcube_poll == None:
                
                self.logit("Stopping GTLTcube calculation.")
                self.ltcube_proc.kill()
                self.SourceLtcubeButton["text"] = "Run CTLTcube"


            else:

               run = 1
                
        if run:

            if not os.path.exists(self.analysis.evfile):
                self.logerr("CTLTcube extractor:\nEvent file is not available. Can't calculate cube without it.")
                self.logblue("Hint: Click on \"Filter events\" button.")
                return

            logstring  = "*** Running GTLTCUBE with parameters:\n"
            self.SourceLtcubeButton["text"] = "Stop GTLTcube"


            outfile = self.analysis.basename+'_ltcube.fits'
            evfile = self.analysis.evfile
            scfile = self.analysis.scfile
            dcostheta = self.analysis.dcostheta
            binsz = self.analysis.binsz
            zmax = self.analysis.zmax
            res_str = ""

            logstring += "    evfile  = "+evfile+"\n"
            logstring += "    scfile  = "+scfile+"\n"
            logstring += "    outfile = "+outfile+"\n"
            logstring += "    dcostheta  = "+str(dcostheta)+"\n"
            logstring += "    binsz  = "+str(binsz)+"\n"
            logstring += "    zmax  = "+str(zmax)
            
            self.logit(logstring)

            if os.path.exists(outfile):

                oldfile = "old"+str(os.getpid())+"_"+outfile
                self.logit("The file "+outfile+" exists. Move it to "+oldfile+".")
                os.system("mv -f "+outfile+" "+oldfile)

            self.ltcube_proc = subprocess.Popen(["gtltcube",evfile,scfile,outfile,
                                             str(dcostheta),str(binsz),"zmax="+str(zmax)],
                                            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            ltcube_thread = threading.Thread(target=self.ltcube_wait,args=())
            ltcube_thread.start()

            self.ltcube_file.set("calculating...")
            self.SourceLtcubeFileLabel.update()

        return

    def ltcube_wait(self):

        import time
        
        while not self.ltcube_stop:

            time.sleep(1.0)

            try:       

                cube_poll = self.ltcube_proc.poll()


            except:        

                # this should not happen
                break

#
            else:
                if cube_poll == None:  
                    continue
                else:
                    break


        self.logblue("GTLTCUBE finished.\nGalactic cube is saved to "+self.analysis.basename+"_ltcube.fits")
        self.SourceLtcubeButton["text"] = "Run GTLTcube"

        if self.ltcube_proc.returncode:
            self.analysis.ltcube = 'None'

        else:
            self.analysis.ltcube = self.analysis.basename+'_ltcube.fits'

        self.ltcube_file.set(self.analysis.ltcube)            
        return 
            
    def get_spectra_thr(self):
        
        from lsthreads import spectrum_thread

        if not self.analysis.havedata:
            self.nodata()
            return -1

        run = int(0)

        try:
            state = self.specthread.state
        except Exception as e:
#            print "1",e
            run = int(1)
        else:
 #           print "2 ",state
            if state != "running":
                run = int(1)
            else:
                self.specthread.stop()


        eemin = max(float(self.analysis.obs_pars["emin"]),100.0)
        if (float(self.analysis.obs_pars["emin"]) < 100.0):
            self.logit("Warning: Minimum energy for spectrum extraction is set to 100.0 MeV. ")

        if run:

            self.logblue("Starting spectrum calculation.")

            try:
                subprocess.Popen(["mkdir",self.analysis.name],
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            except:
                pass

            self.specthread = spectrum_thread(self.analysis.evfile,self.analysis.scfile,
                                      self.analysis.ra,self.analysis.dec,self.analysis.rad,
                                      self.analysis.bkg_ra,self.analysis.bkg_dec,self.analysis.bkg_rad,
                                      tmin=float(self.tmin_entry.get()),tmax=float(self.tmax_entry.get()),
                                      emin=eemin,
                                      emax=float(self.analysis.obs_pars["emax"]),
                                      enbin=self.nchan_entry.get(),
                                      irfs=self.analysis.irfs,
                                      cube=self.analysis.ltcube,outroot=self.analysis.name,
                                      dcostheta=float(self.dcostheta_entry.get()),
                                      thetamax=float(self.thetacut_entry.get()),
                                      binsz=float(self.binsz_entry.get()),
                                      zmax=float(self.zmax_entry.get()),
                                      logqueue = self.logQueue)

            self.specthread.start()
            specthread_wait = threading.Thread(target = self.spectrum_wait,args=())
            specthread_wait.start() 
            self.SourceGetspcButton["text"] = "Stop extracting spectrum"


    def spectrum_wait(self):
        
        import time
        
        while self.specthread.state != "stopped" and self.specthread.state != "done" :

            time.sleep(0.5)


        if self.specthread.state == "done":

            lcf = self.lc_file.get()
            os.system("mv "+self.analysis.name+"_src.pha "+" "+self.analysis.name+'/'+self.analysis.name+"_src.pha")
            os.system("mv "+self.analysis.name+"_bkg.pha "+" "+self.analysis.name+'/'+self.analysis.name+"_bkg.pha")
            os.system("mv "+self.analysis.name+".rsp "+" "+self.analysis.name+'/'+self.analysis.name+".rsp")
            os.system("mv "+self.analysis.name+".arf "+" "+self.analysis.name+'/'+self.analysis.name+".arf")
            self.logblue("Finished extracting spectrum.\n"+\
            "     Spectrum:  "+self.analysis.name+'/'+self.analysis.name+"_src.pha\n"+\
            "     Background:"+self.analysis.name+'/'+self.analysis.name+"_bkg.pha\n"+\
            "     Response:  "+self.analysis.name+'/'+self.analysis.name+".rsp\n"+\
            "     Arf:       "+self.analysis.name+'/'+self.analysis.name+".arf")
            


        if self.specthread.state == "stopped":

            self.logerr("Spectrum extraction aborted.") 

        self.SourceGetspcButton["text"] = "Extract spectrum"
    

    def save_spectrum(self):
        import string
        from tkMessageBox import askquestion

        spcf = self.analysis.name+'/'+self.analysis.name+"_src.pha"
        bkgf = self.analysis.name+'/'+self.analysis.name+"_bkg.pha"
        rspf = self.analysis.name+'/'+self.analysis.name+".rsp"
        arff = self.analysis.name+'/'+self.analysis.name+".arf"

        if ( not os.path.exists(spcf) or not os.path.exists(bkgf) or \
                 not os.path.exists(rspf) or not os.path.exists(arff)):
            self.logerr("Warning: one or more spectral products are not found.")
        
        fopt = options = {}
        options['defaultextension'] = ''
        options['filetypes'] = [('PHA files','*.pha')]
        if (self.analysis.fgl_source != "None"):
            initname = string.join(string.split(self.analysis.fgl_source," "),"")
        else:
            initname = "ra%.2f_dec%.2f_r%.2f"%(self.analysis.ra,self.analysis.dec,
                                               self.analysis.rad)
#        initname = self.analysis.name+'_src'
        options['initialfile'] = initname
#        options['parent'] = root
        options['title'] = 'Save spectrum'
        fname = tkFileDialog.asksaveasfilename(**fopt)
        if (fname == ""): return
        
#        print fname
        bfname = os.path.basename(fname)
        if (os.path.exists(fname+"_src.pha") or os.path.exists(fname+"_bkg.pha") or \
                os.path.exists(fname+".rsp") or os.path.exists(fname+".arf")):
            ans = askquestion("Files exist","One or more files "+os.path.basename(fname)+"* exist in this location. Replace?")
            if (ans): 
                os.system("rm -f "+fname+"_src.pha "+fname+".rsp "+fname+"_bkg.pha "+fname+".arf ")
            else:
                return


        try:
            os.system("cp "+spcf+" "+fname+"_src.pha")
            os.system("cp "+bkgf+" "+fname+"_bkg.pha")
            os.system("cp "+rspf+" "+fname+".rsp")
            os.system("cp "+arff+" "+fname+".arf")

            os.system("fparkey "+bfname+"_bkg.pha "+fname+"_src.pha BACKFILE")
            os.system("fparkey "+bfname+".rsp "+fname+"_src.pha RESPFILE")
            os.system("fparkey "+bfname+".arf "+fname+"_src.pha BACKFILE")

        except:
            self.logerr("Error occured when saving spectrum. Check you results.")
            return

        else:
            self.logblue("Spectrum sucessfully saved to\n"+\
            "Source spectrum:     "+fname+"_src.pha\n"+\
            "Background spectrum: "+fname+"_bkg.pha\n"+\
            "Response:            "+fname+".rsp\n"+\
            "Ancillary response:  "+fname+".arf")
           

    def show_spectra(self):

        if not os.path.exists(self.analysis.name+'/'+self.analysis.specfile):
            
            self.logerr("There is no spectrum yet. Use \"Extract  Spectrum\" button first!")
            return

        try:
            pr = self.xspec_proc.poll()
        except:
          
            self.xspec_proc = subprocess.Popen(['xspec'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            fil = self.xspec_proc.stdin 
            fil.write("cd "+self.analysis.name+'\n')
            fil.write('data 1 '+self.analysis.specfile+'\n')
            fil.write('backgrnd 1 none\n')
            fil.write('data 2 '+self.analysis.bkgfile+'\n')
            fil.write('backgrnd 1 none\n')
            fil.write("cpd \/xw\n")
            fil.write("setplot ch\n")
            fil.write('plot ldata\n')
            
            fil.write("iplot\n")
            fil.write("LAB T RED - BACKGROUND \n")
            fil.write("LAB OT BLACK - SOURCE - BLACK \n")
            fil.write("plot\n")
    
            

            self.SourceCountsButton["text"] = "Hide spectrum/background" 

        else:
            if pr == None:
                try:
                    self.xspec_proc.terminate()
                    self.xspec_proc.kill()
                except:
                    pass
                self.SourceCountsButton["text"] = "Plot spectrum/background" 
                
            else:

                self.xspec_proc = subprocess.Popen(['xspec'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                fil = self.xspec_proc.stdin 
                fil.write("cd "+self.analysis.name+'\n')
                fil.write('data 1 '+self.analysis.specfile+'\n')
                fil.write('data 2 '+self.analysis.bkgfile+'\n')
                fil.write("cpd \/xw\n")
                fil.write("setplot ch\n")
                fil.write('plot ldata\n')
                self.SourceCountsButton["text"] = "Hide counts spectrum/background" 


    def get_full_lc(self):
        
        from lsthreads import ls_thread

        if not self.analysis.havedata:
            self.nodata()
            return -1

        run = int(0)

        try:
            state = self.lsthread.state
        except Exception as e:
#            print "1",e
            run = int(1)
        else:
 #           print "2 ",state
            if state != "running":
                run = int(1)
            else:
                self.lsthread.state = "stopped"


        if run:
            self.logblue("Starting lightcurve calculation.")

#            lcf = self.lc_file.get()
            lcf = self.analysis.name+'_'+self.lc_bin.get()+'.lc'

            pl_free = True
            if self.lc_index_fixed.get(): pl_free = False

#        res = latspeclc(self.analysis.evfile,self.analysis.scfile,

            try:
                subprocess.Popen(["mkdir",self.analysis.name],
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            except:
                pass

            self.lsthread = ls_thread(self.analysis.evfile,self.analysis.scfile,
                                      self.analysis.ra,self.analysis.dec,
                                      self.analysis.rad,
                                      self.analysis.bkg_ra,self.analysis.bkg_dec,self.analysis.bkg_rad,
                                      emin=float(self.lc_emin_entry.get()),
                                      emax=float(self.lc_emax_entry.get()),
                                      irfs=self.analysis.irfs,
                                      pl_index=float(self.lc_pl_index.get()), index_free = pl_free,
                                      cube=self.analysis.ltcube,outfile=self.analysis.name+'/'+lcf,
                                      tbin=self.lc_tres,dcostheta=float(self.dcostheta_entry.get()),
                                      logqueue = self.logQueue)

            self.lsthread.start()
            lsthread_wait = threading.Thread(target = self.ls_wait,args=())
            lsthread_wait.start() 
            self.LcExtBtn["text"]= "Stop Extracting LC"
            
    def ls_wait(self):
        
        import time
        

        while self.lsthread.state != "stopped" and self.lsthread.state != "done" :

            time.sleep(0.5)


        if self.lsthread.state == "done":

#            lcf = self.lc_file.get()
            lcf = self.analysis.name+'_'+self.lc_bin.get()+'.lc'
            self.lc_file.set(lcf)
            self.logblue("Finished producing lightcurve." + \
            "Lightcurve file is saved to "+self.analysis.name+'/'+lcf+".")


        if self.lsthread.state == "stopped":

            self.logerr("Lightcurve extraction aborted.") 

        self.LcExtBtn["text"]= "Extract Lightcurve"


    def plot_lc(self):
        
        try:
            fplot_poll = ""
            fplot_poll = self.lcplot_proc.poll()
        except:
            pass
              
        if fplot_poll == None:
            self.lcplot_proc.stdin.write("quit\n")
            self.LcShowBtn["text"] = "Show Lightcurve"
        else:

            lcf = self.analysis.name+'/'+self.analysis.name+'_'+self.lc_bin.get()+'.lc'
            if not os.path.exists(lcf):
                self.logerr("Lightcurve file is not available.")
                self.logblue("Create lightcurve by pressing \"Extract lightcurve\" button.")
                return
# If index is free then show flux and index, otherwise just flux
            ystr = "FLUX[ERROR] INDEX[INDEXERR]"
            if self.lc_index_fixed.get(): ystr = "FLUX[ERROR]"
            
            if os.path.exists(lcf):
                self.lcplot_proc = subprocess.Popen(["fplot",lcf,
                                                     "TIME",ystr,"-",
                                                     "/xw","line step;plot;"],
                                                    stdout=subprocess.PIPE,
                                                    stdin=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
                self.LcShowBtn["text"] = "Hide Lightcurve"
        return



    def save_lightcurve(self):
#        from tkMessageBox import askquestion
        
        lcf = self.analysis.name+'/'+self.analysis.name+'_'+self.lc_bin.get()+'.lc'
        if ( not os.path.exists(lcf)):
#            self.logerr("Error saving lightcurve: file not found.")
            self.logerr("Lightcurve file is not available.")
            self.logblue("Create lightcurve by pressing \"Extract lightcurve\" button.")
            return;
        
        fopt = options = {}
        options['defaultextension'] = '.fits'
        options['filetypes'] = [('All files','*.*'),('LC files','*.lc'),('FITS files','*.fits')]
        options['initialfile'] = self.analysis.name+'_'+self.lc_bin.get()+'.lc'
#        options['parent'] = root
        options['title'] = 'Save lightcurve'
        fname = tkFileDialog.asksaveasfilename(**fopt)
        if fname == "": return;
#        print fname
        bfname = os.path.basename(fname)
#        if (os.path.exists(fname)):
#            ans = askquestion("File exists","File:"+os.path.basename(fname)+" exists\nin this location.Replace?")
#            if (ans): 
#                os.system("rm -f "+fname)
#            else:
#                return
        try:
            os.system("cp "+lcf+" "+fname)

        except:
            self.logerr("Error occured when saving lightcurve. Check you results.")

        else:
            self.logblue("Lightcurve sucessfully saved to "+fname)


    def flux_tres_rtrn(self,event):
#        import subprocess
        xxx = self.flux_entry.get()
        try:
            yyy = float(xxx)
        except:
            self.flux_entry.set(self.analysis.fluxTres)
        else:

            self.analysis.fluxTres = float(xxx)
            self.flux_entry.set(self.analysis.fluxTres)
            self.populate_cat_source_menu()
            try:       
                ds9_poll = self.analysis.ds9.poll()
            except:
                pass
            else:
                if ds9_poll == None:
                    self.analysis.write_regions()
                    lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,"regions","delete","all"])
                    lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,
                                            "regions","file",self.analysis.basename+'.reg'])

        return

            

    def basename_return(self,event):

        li = self.basename_entry.get()
        xxx = li.split()
        if len(xxx)>1: 
            self.logit("Basename should not contain spaces!!!")
            self.basename_entry.set(self.analysis.basename)
            return
        
        xxx = li.split("/")
        if len(xxx)>1: 
            self.logit("Basename should not contain slashes!!!")
            self.basename_entry.set(self.analysis.basename)
            return
        if li == "":
            self.logit("Basename can not be empty string.")
            self.basename_entry.set(self.analysis.basename)
            return
        
        self.analysis.basename = li
        self.analysis.ltcube = li+'_ltcube.fits'
        self.analysis.set_names()
        self.set_filter_panel()
#        self.ImageLself.analysis.image
        self.rootname_entry.set(self.analysis.name)
#        self.set_ltcube_ckbtn()
#        self.XspecRunButton["state"] = tk.DISABLED
#        self.clear_model()
        try:
            self.analysis.ds9.terminate()
            self.xs_proc.kill()
            self.xs_fil.close()
            self.XspecPromptEntry["state"] = tk.DISABLED
            self.XspecRunButton["state"] = tk.NORMAL
        except:
            pass


    def run_ds9(self):

        """
        Invokes ds9 and predefines regions.
        If catalog is available, puts 2FGL sources, which are brighter
        than <flux_tres> parameter.

        """

        import time

        if not self.analysis.havedata:
            self.nodata()
            return

        if not os.path.exists(self.analysis.image):
            self.logerr("You need to extact image first! Use \"Extract\" button.")
            return

        try:       
            ds9_poll = self.analysis.ds9.poll()

        except:

            self.analysis.ds9 = self.analysis.runds9()
            self.ds9_thread = threading.Thread(target = self.ds9wait,args=())
            self.ds9_thread.start()
            self.ImageDS9Button["text"] = "Stop ds9"
            self.logblue("Opening ds9 session to edit/verify regions.The source region is shown in green,\nbackground region is red. DO NOT ADD or DELETE regions!")

            if self.analysis.haveCatalog:
                self.logblue("Hint: you can place the source region over a Catalog source by choosing \nthe source name in the \"2FGL source\" menu.")

        else:

            if ds9_poll == None:

                lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,"exit"])

                self.logit("DS9 session finished.")
            else:

                self.analysis.ds9 = self.analysis.runds9()
                self.ds9_thread = threading.Thread(target = self.ds9wait,args=())
                self.ds9_thread.start()
                self.ImageDS9Button["text"] = "Stop ds9"
                self.logblue("Opening ds9 session to edit/verify regions.The source region is shown in green,\nbackground region is red. DO NOT ADD or DELETE regions!")
                if self.analysis.haveCatalog:
                    self.logblue("Hint: you can jump to a Catalog source by using \"2FGL source\" menu.")

        return


    def ds9wait(self):
        
        
        import time
        xpa_response = "no"
        nwait = 0
        while xpa_response.strip() != "yes" and nwait < 30:
            time.sleep(0.2)
            xpa_response = subprocess.Popen(['xpaaccess','-c',self.analysis.ds9id],
                                            stdout=subprocess.PIPE).communicate()[0]
            nwait += 1
#            print xpa_response.strip(),nwait,'here'


            
#        time.sleep(5.0)

        tol = 1.0e-4
        lra = float(self.src_ra_entry.get())
        ldec = float(self.src_dec_entry.get())
        lrad = float(self.src_rad_entry.get())
        lbra = float(self.bkg_ra_entry.get())
        lbdec = float(self.bkg_dec_entry.get())
        lbrad = float(self.bkg_rad_entry.get())

        while 1:

            time.sleep(1.0)

            try:       

                ds9_poll = self.analysis.ds9.poll()

            except:

                try:
                    self.ImageDS9Button["text"] = "Run ds9"
                except:
                    pass
                return

            else:
                
                if ds9_poll != None:

                    try:
                        self.ImageDS9Button["text"] = "Run ds9"
                    except:
                        pass
                
                    return

                self.analysis.getregions()
                sd = 100.0
                sn = ""
                chk = False
                if ( abs(self.analysis.ra - lra)>tol):
                    chk = True
                    self.src_ra_entry.set("{:.3f}".format(self.analysis.ra))
                    lra = self.analysis.ra
#                    sn,sd,sassn,res = get_closest_fgl_asssource(self.analysis.ra,
#                                      self.analysis.dec,self.analysis.catalog)

                if ( abs(self.analysis.dec - ldec)>tol): 
                    chk = True
                    ldec = self.analysis.dec
                    self.src_dec_entry.set("{:.3f}".format(ldec))
#                    sn,sd,sassn,res = get_closest_fgl_asssource(self.analysis.ra,
#                                      self.analysis.dec,self.analysis.catalog)
                if ( abs(self.analysis.rad - lrad)>tol):
                    chk = True
                    lrad = self.analysis.rad
                    self.src_rad_entry.set("{:.3f}".format(lrad))
#                    sn,sd,sassn,res = get_closest_fgl_asssource(self.analysis.ra,
#                                      self.analysis.dec,self.analysis.catalog)

                if  ( abs(self.analysis.bkg_ra - lbra)>tol):
                    self.bkg_ra_entry.set("{:.3f}".format(self.analysis.bkg_ra))
                    lbra = self.analysis.bkg_ra
                if ( abs(self.analysis.bkg_dec - lbdec)>tol): 
                    lbdec = self.analysis.bkg_dec
                    self.bkg_dec_entry.set("{:.3f}".format(lbdec))
                if ( abs(self.analysis.bkg_rad - lbrad)>tol):
                    lbrad = self.analysis.bkg_rad
                    self.bkg_rad_entry.set("{:.3f}".format(lbrad))

#                self.analysis.set_names()
#                self.rootname_entry.set(self.analysis.name)
                if chk: self.catsourceid()
#                    print self.cat_source.get()
        self.analysis.set_names()
        self.set_spectrum_panel()
                

    def catsourceid(self):

        from fgltools import get_closest_fgl_asssource
        from string import split,join
#        print "SOUCE"

        sn,sd,sassn,res = get_closest_fgl_asssource(self.analysis.ra,
                                                    self.analysis.dec,self.analysis.catalog)
        self.analysis.name ="%s_ra%.2f_dec%.2f_r%.2f"%(self.analysis.basename,
                                                       self.analysis.ra,self.analysis.dec,
                                                       self.analysis.rad)
#                    if self.analysis.dist_tres > sd:
        if self.analysis.dist_tres > sd and self.analysis.haveCatalog:
            self.skipch = True
            self.cat_source.set(sassn)
            self.analysis.assoc_source = sassn
            self.analysis.fgl_source = sn
            self.skipch = False
            self.analysis.name = self.analysis.basename+'_'+join(split(sn," "),"")
            
            
#                    if self.analysis.dist_tres <= sd and sd < 100.0:
        if self.analysis.dist_tres <= sd and sd < 100.0 and self.analysis.haveCatalog:
            self.skipch = True
            self.cat_source.set("None")
            self.analysis.fgl_source = "None"
            self.skipch = False
            self.analysis.assoc_source = self.analysis.name
        self.rootname_entry.set(self.analysis.name)
        

    def get_regions(self):
        
        if not self.analysis.havedata:
            self.nodata()
            return


        try:       
            ds9_poll = self.analysis.ds9.poll()
        except:

            self.logerr("You need to start ds9 first! Use \"Run sd9\" button.")
            return


        else:

            if ds9_poll == None:
                self.analysis.getregions()
#                print self.analysis.ra,self.analysis.dec
                self.analysis.write_regions()
                self.analysis.set_names()
                self.rootname_entry.set(self.analysis.name)
                if self.analysis.assoc_source != "":
                    self.cat_source.set(self.analysis.assoc_source)
#                    print self.cat_source.get()
                else:
                    self.cat_source.set(self.analysis.fgl_source)
#                    print self.cat_source.get()                    
#            self.src_spc.set("")
                self.modelvar.set(self.analysis.spectrum_type)
#                self.XspecRunButton["state"] = tk.DISABLED
                self.logit("New regions set:\n"+\
                "Source: Circle(RA= %.2f, DEC= %.2f, Radius=%.2f deg)\n"%(self.analysis.ra,self.analysis.dec,self.analysis.rad)+\
                "Background: Circle(RA= %.2f, DEC= %.2f, Radius=%.2f deg)"%(self.analysis.bkg_ra,self.analysis.bkg_dec,self.analysis.bkg_rad))
#            else:
#                self.analysis.ds9 = self.analysis.runds9()
           
                
    def nodata(self):
        self.logerr("No LAT data in the current directory. " +\
                        "Specify data directory using \"...\" \n button in \"Data\"" +\
                    "section of the \"Settings\" panel.")


    def filterevents(self):

        from lsthreads import filter_thread

        if not self.analysis.havedata:
            self.nodata()
            return
        
        run = int(0)

        try:
            state = self.filt_thread.state
#            print state

        except:            
            run = int(1)

        else:
            if state == "running":
                self.filt_thread.stop()

            if state == "done" or state == "stopped":
                run = int(1)


        if run:
            
#            self.logblue("Start filtering thread.")
            self.filt_thread = filter_thread('efiles.list',
                                             self.analysis.scfile,
                                             self.analysis.basename+"_filtered_gti.fits",
                                             self.analysis.obs_pars["RA"],
                                             self.analysis.obs_pars["DEC"],
                                             self.analysis.obs_pars["roi"],
                                             self.analysis.obs_pars["tmin"],
                                             self.analysis.obs_pars["tmax"],
                                             self.analysis.obs_pars["emin"],
                                             self.analysis.obs_pars["emax"],
                                             self.analysis.zmax,
                                             logqueue = self.logQueue)
            self.filt_thread.start()

            wait_thread = threading.Thread(target=self.filter_wait,args=())
            wait_thread.start()

            self.DataFilterButton["text"] = "Stop Flitering"
#        self.DataFilterButton["command"] = self.filter_events_thread._Thread_stop

            self.filtered_events.set("calculating...")
            self.DataFilterFileLabel.update()


    def filter_wait(self):
        
        import time

        while self.filt_thread.state != "stopped" and self.filt_thread.state != "done":

            time.sleep(0.5)


        if  self.filt_thread.state == "stopped":
            
            self.analysis.evfile = "None"
            self.filtered_events.set(self.analysis.evfile)           
            self.logerr("Event file production aborted!")
 
        if  self.filt_thread.state == "done":
            
            ef = self.analysis.basename+"_filtered_gti.fits"
            if (os.path.exists(ef)):
                self.analysis.evfile = \
                    self.analysis.basename+"_filtered_gti.fits"
                self.filtered_events.set(self.analysis.evfile)           
                self.logblue("Finished filtering events!")
            else:
                self.logerr("Something wrong. Event file was not created!!!")
                self.analysis.evfile = "None"
                self.filtered_events.set(self.analysis.evfile)           

#                pass

#        if self.filt_thread.state == "error":
#            self.logit(self.filt_thread.out)
            

        self.logit(self.filt_thread.out)
        self.DataFilterButton["text"] = "Filter Events"            
                        

    def image_thread(self):
        
        """Defines and starts image extraction thread."""
        
        self.im_thread = threading.Thread(target=self.createimage,args=())
        self.im_thread.start()
        
    def createimage(self):
        
        from string import join
        
        """Performs image extraction. Called from image thread."""

        if not self.analysis.havedata:
            self.nodata()
            return -1 


        if not os.path.exists(self.analysis.evfile):
            self.logerr("Event file is not available. Use \"Filter Events\" to create one.")
            return

        self.ImageCreateButton["state"] = tk.DISABLED
        self.logit("****RUNNING GTBIN TO CREATE REGION IMAGE ******")
        binsz = float(self.binsz_entry.get())
        npics = int(self.analysis.obs_pars['roi']*2/binsz)
        self.logit(join(["    Parameters:","    algorithm=CMAP","    ebinalg=LOG",
                                    "    scfile="+self.analysis.scfile,
                                    "    evfile="+self.analysis.evfile,
                                    "    outfile="+self.analysis.basename+'_image.fits',
                                    "    tstart="+str(self.analysis.tmin),
                                    "    tstop="+str(self.analysis.tmax),
                                    "    emin="+str(self.analysis.emin),
                                    "    emax="+str(self.analysis.emax),
                                    "    nxpix="+str(npics),"    nypix="+str(npics),
                                    "    binsz="+str(binsz),"    xref="+str(self.analysis.ra),
                                    "    yref="+str(self.analysis.dec),"    axisrot=0.0",
                                    "    proj=AIT","    coordsys=CEL",
                                    "    chatter="+str(self.analysis.chatter)],"\n"))
        self.image_file.set("calculating...")
        self.ImageLabel.update()
#        time.sleep(0.05)
#        try:

        self.analysis.ra  = self.analysis.obs_pars["RA"]
        self.analysis.dec = self.analysis.obs_pars["DEC"]

#        out = self.analysis.runevtbin(alg="CMAP",
#                                      outfile=self.analysis.basename+'_roi.fits')
        gtbinerr = False
        process = subprocess.Popen(["gtbin","algorithm=CMAP","ebinalg=LOG",
                                    "scfile="+self.analysis.scfile,
                                    "evfile="+self.analysis.evfile,
                                    "outfile="+self.analysis.basename+'_image.fits',
                                    "tstart="+str(self.analysis.tmin),
                                    "tstop="+str(self.analysis.tmax),
                                    "emin="+str(self.analysis.emin),
                                    "emax="+str(self.analysis.emax),
                                    "nxpix="+str(npics),"nypix="+str(npics),
                                    "binsz="+str(binsz),"xref="+str(self.analysis.ra),
                                    "yref="+str(self.analysis.dec),"axisrot=0.0",
                                    "proj=AIT","coordsys=CEL",
                                    "chatter="+str(self.analysis.chatter)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    

#       except:
        catchError = "at the top level:"
        for line in process.stdout:
            self.logit("IMAGE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        for line in process.stderr:
            self.logit("IMAGE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        
        if (gtbinerr):
            self.logerr("ERROR DURING GTBIN EXECUTION!!!!")
            self.analysis.image = "None"
        
        
        if os.path.exists(self.analysis.basename+'_image.fits'):
            self.logit("Image file: "+self.analysis.basename+"_image.fits created.")
            self.logblue("Finished extracting image.")
            self.analysis.image = self.analysis.basename+'_image.fits'

        self.set_filter_panel()
        
        self.ImageCreateButton["state"] = tk.NORMAL
        return


    def askdirectory(self):

        """ Asks for a new LAT data directory"""

        dirname = tkFileDialog.askdirectory()
        if dirname == "": return
#        self.DataDirLabel["text"] = dirname
        os.chdir(dirname)
        self.analysis.datapath = dirname
        self.analysis.prepData()
        self.analysis.set_names()
        self.set_settings_panel()
        self.set_filter_panel()
        self.set_spectrum_panel()
        self.set_regions_entry()
#        self.clear_log()
        self.populate_cat_source_menu()
        try:
            self.analysis.ds9.terminate()
            self.xs_proc.kill()
            self.xs_fil.close()
            self.XspecPromptEntry["state"] = tk.DISABLED
            self.XspecRunButton["state"] = tk.NORMAL
        except:
            pass
        if self.analysis.havedata:
            self.logit("Working directory: "+dirname)
#            self.logit("Fermi/LAT data is found.")
            self.log_data_info()
        else:
            self.logit("No LAT data is found in directory.")
        return

    def askfile(self):

        fname = tkFileDialog.askopenfilename()
        if fname == "": return

        try:
            res = os.path.exists(fname)
        except:
            return

        self.analysis.catalog = fname
        self.analysis.verify_cat()
        self.analysis.set_names()
        self.set_filter_panel()
        if self.analysis.haveCatalog:
#            self.CatLabel["text"] = self.analysis.catalog
            self.logit("Using 2FGL catalog: "+self.analysis.catalog)
            self.populate_cat_source_menu()
            self.show_cat_sources()

        else:
            self.logit("2FGL catalog (and related functionality) is not available.")
        return

    def ask_cube(self):

        fname = tkFileDialog.askopenfilename()
        if fname == "": return

        try:
            res = os.path.exists(fname)
        except:
            return


        self.ltcube_file.set(os.path.basename(fname))
        self.analysis.ltcube = self.ltcube_file.get()
        self.logit("Using Galactic cube: "+fname)
        return

    def xspec_prompt_return(self,event):
        import time
        try:
            self.xs_proc.stdin.write(self.xspec_prompt.get()+"\n")
            time.sleep(0.5)
            self.logit(self.xs_fil.read())
        except:
            self.logerr("Error send input to xspec.")
            pass
        self.xspec_prompt.set("")
        return

    def save_log(self):
        text = self.LogText.get(1.0,tk.END)
        logfile = self.analysis.datapath+"/"+self.analysis.basename + '.log'
        fil = open(logfile,"w")
        fil.write(text)
        fil.close()
        self.logit("Log saved to "+logfile)

    def clear_log(self):
        self.logLock.acquire()
        self.LogText["state"] = tk.NORMAL
        self.LogText.delete(0.0,tk.END)
        self.LogText["state"] = tk.DISABLED
        self.logLock.release()

    def hline(self):

        self.LogText["state"] = tk.NORMAL
        self.LogText.insert(tk.END,'---------------------------------------------------------------------------\n')
        self.LogText["state"] = tk.DISABLED

    def quit_gui(self):
        
        self.stop = True
        self.ltcube_stop = True

        try:
            self.filt_thread.stop()
        except:
            pass


        try:
            self.lsthread.stop()
        except:
            pass

        try:
            self.helpthrd.stop()
        except:
            pass

        try:
            self.analysis.ds9.kill()
            
        except:
            pass

        try:
            self.xs_proc.terminate() 
        except:
            pass

        self.analysis.writerc()

        self.quit()

