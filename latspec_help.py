import Tkinter as tk
import tkFont
import threading

class help_thread():

    def __init__(self):

        self.thread = threading.Thread(target=self.run,args=()) 
        self.state = "off"

    def start(self):
        """Starts the lightcurve calculation"""
        
        self.thread.start()
        self.state = "on"
    
    def stop(self):

        self.help_top.destroy()
        self.state = "off"

    def run(self):

#        help_window()


#def help_window():
        from ScrolledText import ScrolledText

        def  gotosettings(*args):
            text.see(tk.END)
            text.see(setting_index)

        def  gotoinfo(*args):
            text.see(tk.END)
            text.see(info_index)

        def  gotoprereq(*args):
            text.see(tk.END)
            text.see(prereq_index)

        def  gotolc(*args):
            text.see(tk.END)
            text.see(lc_index)

        def  gototop(*args):
            text.see(tk.END)
            text.see(top_index)

        def  gotospec(*args):
            text.see(tk.END)
            text.see(spec_index)

        def show_tcross_cursor(*args):
            text.config(cursor="tcross")

        def show_arrow_cursor(*args):
            text.config(cursor="arrow")




        self.help_top = tk.Toplevel()
        self.help_top.title("Help")
        text = ScrolledText(self.help_top,bg='white')
        text.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.Y)
        bold_font = tkFont.Font(text,text.cget("font"))
        bold_font.configure(weight='bold')

        txt0 = """

           Contents

    General Information
    Settings Panel
    Prerequisites Panel
    Lightcurve Panel
    Spectrum Panel










\n"""

        text.insert(tk.END,txt0)
# Define tags
        text.tag_add('settings',"%s-15l+4c"%tk.INSERT,"%s-15l+18c"%tk.INSERT)
        text.tag_bind('settings','<Enter>', show_arrow_cursor)
        text.tag_bind('settings','<Leave>', show_tcross_cursor)
        text.tag_config('settings',foreground='blue',underline=1)
        text.tag_bind('settings','<Button-1>',gotosettings)

        text.tag_add('info',"%s-16l+4c"%tk.INSERT,"%s-16l+24c"%tk.INSERT)
        text.tag_bind('info','<Enter>', show_arrow_cursor)
        text.tag_bind('info','<Leave>', show_tcross_cursor)
        text.tag_config('info',foreground='blue',underline=1)
        text.tag_bind('info','<Button-1>',gotoinfo)

        text.tag_add('prereq',"%s-14l+4c"%tk.INSERT,"%s-14l+24c"%tk.INSERT)
        text.tag_bind('prereq','<Enter>', show_arrow_cursor)
        text.tag_bind('prereq','<Leave>', show_tcross_cursor)
        text.tag_config('prereq',foreground='blue',underline=1)
        text.tag_bind('prereq','<Button-1>',gotoprereq)

        text.tag_add('lc',"%s-13l+4c"%tk.INSERT,"%s-13l+20c"%tk.INSERT)
        text.tag_bind('lc','<Enter>', show_arrow_cursor)
        text.tag_bind('lc','<Leave>', show_tcross_cursor)
        text.tag_config('lc',foreground='blue',underline=1)
        text.tag_bind('lc','<Button-1>',gotolc)

        text.tag_add('spec',"%s-12l+4c"%tk.INSERT,"%s-12l+18c"%tk.INSERT)
        text.tag_bind('spec','<Enter>', show_arrow_cursor)
        text.tag_bind('spec','<Leave>', show_tcross_cursor)
        text.tag_config('spec',foreground='blue',underline=1)
        text.tag_bind('spec','<Button-1>',gotospec)
        
        setting_index = '70.0'
        info_index = '20.0'
        prereq_index = '100.0'
        lc_index = '140.0'
        spec_index = '167.0'
        top_index = '0.0'



        text.insert(tk.END,"General information\n")
        text.tag_add('tag',"%s-1l"%tk.INSERT,tk.INSERT)
        text.tag_config('tag',font=bold_font,underline=1,justify=tk.CENTER)
        text.insert(tk.END,"\n") 


        txt1 = """

Latspec is designed to analyze FERMI/LAT data. The tool allows to perform  all
stages  of  analysis including event filtering, imaging analysis, spectrum and 
lightcurve generation and spectral modeling using single graphical interface.

The core idea behind the  Latspec data analysis  is  to use ancillary response 
to  account  for  the PSF spillover, allowing to use small extraction radii to
minimize  contamination  from nearby sources. The tool gives  reliable results 
for  well isolated and  relatively bright source. However, standard likelihood 
is recommended in the case of a  faint source in a crouded field. Even in this 
case, Latspec can be helpful to  examine your data and to do "quick-and-dirty"
analysis.

The  program allows  user to process the LAT data, starting from the data set, 
extracted from the LAT data  server,  apply  all  necessary  filters,  specify
regions  and  produce intermediary data  products  necessary  for spectral and
lightcurve analysis. For source and background  region selection  the  program
utilizes DS9 image viewer. The LAT data to be analysed along with some  common
analysis parameters can be set using the  "Settings" panel. Preparation  tasks
(filtered event list, galactic cube and image generation) are performed at the
"Prerequisites" panel.
"""
        text.insert(tk.END,txt1)
        text.tag_add('prereq',"%s-1l+0c"%tk.INSERT,"%s-1l+15c"%tk.INSERT)
        text.tag_add('settings',"%s-3l+42c"%tk.INSERT,"%s-3l+52c"%tk.INSERT)

        txt11 = """
For  spectral  analysis  the  program  extracts count  spectra for   specified
source and background regions, creates necessary response files and optionally
fits spectral model to the data. The  application  also  provides interface to
Xspec spectral fitting package for spectral modeling. Lightcurve is calculated
using Xspec spectral fitting, i.e. spectrum is extracted  and  spectral fit is
performed  for  each  time  interval.  Details  on how to generate and analyze 
spectra and lightcurves tasks are given below  in  "Spectrum" and "Lightcurve"
sections respectively.
    """
        text.insert(tk.END,txt11)
        text.tag_add('lc',"%s-2l+62c"%tk.INSERT,"%s-2l+75c"%tk.INSERT)
        text.tag_add('spec',"%s-2l+47c"%tk.INSERT,"%s-2l+56c"%tk.INSERT)
        txt2 = """

The main  window  of the  program has three frames: top, middle (Log) and  the
bottom  frame.  The  top  frame  is  where analysis is performed by using four
panels: "Settings", "Prerequisites", "Lightcurve" and  "Spectrum". Buttons  at 
the bottom of the top frame are used to  switch between  analysis panels.  The
log  window  displays  various  information about analysis steps taken, errors 
occured, warning, etc. Text lines are color coded for convenience. Namely, the
output of different tasks performed  is  shown  in black, errors in red, hints 
for the next step to take is in blue. The  bottom  row  has four  buttons. The
"Save log" writes the contents of the log window in a  file <basename>.log and
the "Clear Log"  button  clears  the log window. "Help" button shows user this
help and the "Quit" button  quits  Latspec.  Quitting  Latspec  may  take some 
noticable time (few seconds) as the program has to perform some clean up steps: shut  down  all active analysis threads, close any open windows, etc.
    """

        text.insert(tk.END,txt2)

        text.insert(tk.END,"                                                            Back to top")
        text.tag_add('back',"%s-0l-11c"%tk.INSERT,"%s-0l-0c"%tk.INSERT)
        text.tag_bind('back','<Enter>', show_arrow_cursor)
        text.tag_bind('back','<Leave>', show_tcross_cursor)
        text.tag_config('back',foreground='red',underline=1)
        text.tag_bind('back','<Button-1>',gototop)

        text.insert(tk.END,"\n") 
        text.insert(tk.END,"Settings Panel\n")

        text.tag_add('tag',"%s-1l"%tk.INSERT,tk.INSERT)
        text.insert(tk.END,"\n")
        txt3 = """

There  are   four   sections  in  this panel:"Data", "Catalog", "Basename" and
"Parameters". The "Data"  section  has the "..." button which allows to change
the data directory. The "Data info" button prints a short synopsis of the data 
in the Log window. The "Catalog" section allows to specify a 2FGL catalog file
using the "..." button. You  need  to  specify catalog only the first time you
start  the  program. Latspec  stores information  about  the  latest data  and 
catalog in the resource file (~/.latspecrc) and will load  them  automatically
next time you start the program.

The "Flux threshold" entry shows the lower flux limit (given in  the  FLUX1000
column of 2FGL catalog) which used to display the catalog sources in  the  DS9
imaging tool (see "Prerequisites"  panel  section  below).  Namely,  when  you 
increase/decrease the  flux  threshold, less/more  sources appear on the image 
and in the 2FGL source  dropdown  menu list in  the  "Image"  section  of  the
"Prerequisites"  panel.
"""
        text.insert(tk.END,txt3)
        text.tag_add('prereq',"%s-1l+0c"%tk.INSERT,"%s-1l+15c"%tk.INSERT)
        txt31 = """
The "Basename" entry specifes the analysis  "basename". It is used as a prefix
to all intermediary files created during analysis (i.e. <basename>_ltcube.fits
for galactic cube,<basename>_roi.fits for  image,etc). The default basename is
"latspec". For each analysed   source  Latspec  creates  individual  directory 
named <basename>_<sourceid> under the current data directory, where <sourceid>
is  either  source  2FGL  catalog  name, if  2FGL catalog is specified, or sky 
location ID ra<RA>_dec<DEC>_rad<radius>. For example, for 3C 273 the directory 
name will be  set to latspec_2FGLJ1229.1+0202 or latspec_r187.35_dec2.00_r3.00
respectiviely.  All  data  products file names, created in the current session 
will have the same <basename>_<sourceID> structure prefix.

The  "Parameters" subpanel allows to set or modify parameters binsz, dcostheta,
thetamax, zmax and set  the IRFS  used  by FERMI Science Tools (gtltcube,gtpsf,
gtrspgen,gtbin,etc.). 
    """

        text.insert(tk.END,txt31)

        text.insert(tk.END,"                                                            Back to top")
        text.tag_add('back',"%s-0l-11c"%tk.INSERT,"%s-0l-0c"%tk.INSERT)
        text.tag_bind('back','<Enter>', show_arrow_cursor)
        text.tag_bind('back','<Leave>', show_tcross_cursor)
        text.tag_config('back',foreground='red',underline=1)
        text.tag_bind('back','<Button-1>',gototop)


        text.insert(tk.END,"\n") 
        text.insert(tk.END,"\n")
        text.insert(tk.END,"\n") 
        text.insert(tk.END,"Prerequisites Panel\n")
        text.tag_add('tag',"%s-1l"%tk.INSERT,tk.INSERT)
#    text.tag_config('tag',foreground='blue',underline=1,justify=tk.CENTER)
        text.insert(tk.END,"\n")
        text.insert(tk.END,"\n")
        txt4 = """    

This panels has three subpanels:"Events","Ltcube" and "Image" used to  create 
or specify filtered event file, galactic cube and image file. These tasks are
achieved by clicking on the "Filter Events","Run GTLTcube" and "Extract Image"
buttons correspondingly. The Latspec then executes a pipeline of Science Tools
to create a specific data product. When the product is created, its name shows
up  on  the  left side of a subpanel. Clicking on a button before the pipeline 
will terminate it and the product will NOT be created. The output event list,
cube or image files will have names with the <basename>_ prefix.

The  "Ltcube"  subpanel has an additional button "Load Cube" to specify a pre-
existing galactic cube file.

The "Image" and "Regions" subpanels present a set of components to extract the
image of the region and  to  specify  the  source  and background regions. The 
entire region image is extracted by clicking  the "Extract image" button. When
image  is  available  (i.e. the  name  of  the image file is shown next to the 
"Extract image"  button),  the source and background extraction regions can be 
set using any of the following three ways. First, region coordinates and radii
can directly set in the corresponding entries of the  "Regions"  panel. Second,
if catalog is specified, the source region can placed over a catalog source by 
choosing its name in the "2FGL Source" menu. Third,  you  can  launch  DS9 and 
modify regions in DS9. Namely, clicking on "Run DS9" will launch DS9, load the 
image, preset the source and background region selection and  show the catalog
sources in the DS9 window. Modifying the regions in the DS9 image  will update
the numbers in the "Regions" panel. In parallel, catalog source identification
is preformed and, if the center of the current source region is idetified with
a catalog source, its name appears in the  catalog  source  menu. (It is worth
noting that source names that are used here are taken from  ASSOC1  column  of
the catalog or from the SOURCE column if  ASSOC1  is  empty.  Also, the source
identification  is  done  with  ANY  2FGL source, while the dropdown menu list 
shows  only  sources  with  2FGL  flux above  the  flux  threshold, set in the 
"Settings" panel).
    """
        text.insert(tk.END,txt4)
        text.tag_add('settings',"%s-1l-4c"%tk.INSERT,"%s-1l+6c"%tk.INSERT)
        txt41 = """

After you are done with producing event/cube/image files and  selecting your 
extraction regions, you can proceed with spectral analysis in the "Spectrum" 
panel or timing analysis in the "Lightcurve" panel. 
                                """
        text.insert(tk.END,txt41)
        text.tag_add('lc',"%s-1l+0c"%tk.INSERT,"%s-1l+12c"%tk.INSERT)
        text.tag_add('spec',"%s-2l+34c"%tk.INSERT,"%s-2l+44c"%tk.INSERT)

        text.insert(tk.END,"\n                                                               Back to top")
        text.tag_add('back',"%s-0l-11c"%tk.INSERT,"%s-0l-0c"%tk.INSERT)
        text.tag_bind('back','<Enter>', show_arrow_cursor)
        text.tag_bind('back','<Leave>', show_tcross_cursor)
        text.tag_config('back',foreground='red',underline=1)
        text.tag_bind('back','<Button-1>',gototop)

        text.insert(tk.END,"\n") 
        text.insert(tk.END,"\n") 
        text.insert(tk.END,"Lightcurve Panel\n")
        text.tag_add('tag',"%s-1l"%tk.INSERT,tk.INSERT)

        txt5 = """

The lightcurve calculation is implemented as follows. Photon flux in each time
bin is calcilated via spectrum  fitting,  accounting  for  PSF  spillover. The
spectrum  is  fit  with  pure  power  law. The photon flux with its errors  is 
calculated  using cflux model (see XSPEC documentaion).

 The "Lightcurve" binning dropdown menue sets the bin size of the lightcurve to
month, week or day (Only these three options for  time interval are available).
The energy  range sets the limits for the photon flux calculation in the XSPEC 
fits. In the "Powerlaw index" entry the user can  specify  the starting  value 
of the index and wheather it should be kept fixed  during spectral fits. These
last two sttings should be modified only in rare cases of a very high 
statistics  (or if you really know what you are doing). 

The "Show lightcurve" button opens up  the QPP plot of the lightcurve. In case
the powerlaw  index  was  free  during  the  lightcurve  extraction, the index
evolution is also plotted. "Save lightcurve" button opens a dialog window 
which allows you to save the lightcurve file in a location different from the
default one (i.e. source directory).

 
    """
        text.insert(tk.END,txt5) 
        text.insert(tk.END,"\n") 
        text.insert(tk.END,"\n") 


        text.insert(tk.END,"                                                            Back to top\n")
        text.tag_add('back',"%s-0l-12c"%tk.INSERT,"%s-0l-0c"%tk.INSERT)
        text.tag_bind('back','<Enter>', show_arrow_cursor)
        text.tag_bind('back','<Leave>', show_tcross_cursor)
        text.tag_config('back',foreground='red',underline=1)
        text.tag_bind('back','<Button-1>',gototop)


        text.insert(tk.END,"Spectrum Panel\n")
        text.tag_add('tag',"%s-1l"%tk.INSERT,tk.INSERT)
        text.insert(tk.END,"\n") 



        txt5  = """
    This panel presents a set of tools to extract and analyse Fermi/LAT energy
spectrum. First,  you need  to extract spectrum and all corresponding response 
files  by  clicking on the "Extract Spectrum" button. You can specify the time
ranges  in  the  "Time Ranges"  window.  The  spectral  files are saved in the 
product directory, shown in the top  line  of the  panel.  After extraction is 
finished  you  have  an option  to  examine the spectrum and background versus 
channels   by   pressing  the   "Plot  spectrum/background" button. When first 
calculated,  spectral  files  are  stored  in a source directory with the file 
names, which can not be changed or modified within  Latspec. To  save spectral
and  response  files in location different from the source directory use "Save 
spectrum" button. "Save spectrum" opens a  save  file  dialog window where you
can  specify  the  location and name of the files for spectral  products to be
saved to. Specifically, when using "Save spectrum" dialog you need to select a
directory where you want your files to be stored and in  the "Save as"  window
you  need  to specify <spectrum_name> string WITHOUT ANY EXTENSIONS. The files
will  then  be  saved   as  <spectrum_name>_src.pha,  <spectrum_name>_bkg.pha,
<spectrum_name>.rsp,etc.

On the  "Xspec"  subpanel the user can perform the full Xspec fit using one of 
three  models:  PowerLaw, LogParabola  and  Power Law with Exponential Cutoff.
The fitting  model can be changed  using  the  dropdown menu. If the source is
identified as a 2FGL catalog source, the model is  preselected  by the catalog
model.  The fit  is performed in the energy range specified by the "Fit Energy 
Range".  Moreover,  one  can  apply any  Xspec  model  or  execute  any  Xspec
command  in  the Xspec prompt, designated by "xspec>".Any Xspec output appears
in the Log window.
    """

        text.insert(tk.END,txt5)

        text.insert(tk.END,"                                                            Back to top\n")
        text.tag_add('back',"%s-0l-12c"%tk.INSERT,"%s-0l-0c"%tk.INSERT)
        text.tag_bind('back','<Enter>', show_arrow_cursor)
        text.tag_bind('back','<Leave>', show_tcross_cursor)
        text.tag_config('back',foreground='red',underline=1)
        text.tag_bind('back','<Button-1>',gototop)



        text.tag_config('tag',font=bold_font)
        text.tag_config('tag',underline=1)
        text.tag_config('tag',justify=tk.CENTER)

        
        txt_bot = """
Nikolai Shaposhnikov (UMD/CRESST/GSFC/FSSC)
nikolai.v.shaposhnikov@nasa.gov
"""
        text.insert(tk.END,txt_bot)
        text.tag_add('bot',"%s-2l-0c"%tk.INSERT,"%s-0l-0c"%tk.INSERT)
#        text.tag_config('bot',foreground='green',underline=0)


        button = tk.Button(self.help_top, text="Dismiss", command=self.stop)
        button.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.Y,padx=20)
        text["state"] = tk.DISABLED

      
        
