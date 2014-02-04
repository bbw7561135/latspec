from coorconv import sdist
import pyfits
import os


def get_brightest_sources(sra,sdec,rad,fl_tres,fglfile):

    
    names = []
    ras = []
    decs = []

    if not os.path.exists(fglfile):
#        print "Specified FGL file ",fglfile
#        print "does not exitst. Exit."
        return [],[],[]

    fglf = pyfits.open(fglfile)
    source = fglf[1].data.field('Source_name')
    assoc1 = fglf[1].data.field('ASSOC1')
    ra = fglf[1].data.field('RAJ2000')
    dec = fglf[1].data.field('DEJ2000')
    sdis = [sdist(ra[i],dec[i],sra,sdec) for i in range(len(source))]
    inds = [ i for i in range(len(source)) if sdist(ra[i],dec[i],sra,sdec)<rad]
    flux = fglf[1].data.field('Flux1000')
#    print len(sdis),len(inds)



    dists = [sdis[i] for i in inds if flux[i] > fl_tres ]
    snames = [source[i] for i in inds if flux[i] > fl_tres  ]
    names = [assoc1[i] for i in inds if flux[i] > fl_tres  ]
    for i in range(len(names)): 
        if names[i] == '': names[i] = snames[i]
    ras = [ra[i] for i in inds if flux[i] > fl_tres and sdis[i]<rad ]
    decs = [dec[i] for i in inds if flux[i] > fl_tres and sdis[i]<rad ]
#    print sdis,ras,decs
    fglf.close()
    return names,ras,decs

def get_closest_fgl_source(sra,sdec,fglfile):
    if not os.path.exists(fglfile):
#        print "Specified FGL file ",fglfile
#        print "does not exitst. Exit."
        return -1.0,-1.0,-1,0
    fglf = pyfits.open(fglfile)
    source = fglf[1].data.field('Source_name')
#    source = fglf[1].data.field('ASSOC1')
    ra = fglf[1].data.field('RAJ2000')
    dec = fglf[1].data.field('DEJ2000')
    sdis = [sdist(ra[i],dec[i],sra,sdec) for i in range(len(source))]
    ind = sdis.index(min(sdis))
    fglf.close()

#    snm = source[ind]
#    if snm == "": snm = source1[ind]
    return source[ind],sdis[ind],ind,0

def get_closest_fgl_asssource(sra,sdec,fglfile):
    if not os.path.exists(fglfile):
#        print "Specified FGL file ",fglfile
#        print "does not exitst. Exit."
        return -1.0,-1.0,-1,0
    fglf = pyfits.open(fglfile)
    source1 = fglf[1].data.field('Source_name')
    source = fglf[1].data.field('ASSOC1')
    ra = fglf[1].data.field('RAJ2000')
    dec = fglf[1].data.field('DEJ2000')
    sdis = [sdist(ra[i],dec[i],sra,sdec) for i in range(len(source))]
    ind = sdis.index(min(sdis))
    fglf.close()

    snm = source[ind]
    if snm == "": snm = source1[ind]
    return source1[ind],sdis[ind],snm,0



def get_fgl_source_coords(sname,fglfile):
    if not os.path.exists(fglfile):
#        print "Specified FGL file ",fglfile
#        print "does not exitst. Exit."
        return -1,-1
    fglf = pyfits.open(fglfile)
    source = fglf[1].data.field('Source_name')
    assoc1 = fglf[1].data.field('ASSOC1')
    ra = fglf[1].data.field('RAJ2000')
    dec = fglf[1].data.field('DEJ2000')
#    print sname
    sssind = [ ind for ind in range(len(source)) if sname[-10:] == source[ind][-10:]]
    if len(sssind):
        sind = sssind[0]
        return ra[sind],dec[sind]
    else:
        sssind = [ ind for ind in range(len(source)) if sname[-10:] == assoc1[ind][-10:]]
        if len(sssind):
            sind = sssind[0]
            return ra[sind],dec[sind]
       
    return -1,-1

#    print sind
#    for i in range(len(source)):
#        if source[i] == sname: sind = i
        
    fglf.close()
    if sind == -1: return 0.0,0.0,-1
    if sind != -1: return ra[sind],dec[sind],sind



def spc(sname,radius,fglfile):
#    Calculates the source proximity coefficient according
#    to 2FGL fluxes.
    sigma = 1.0*1.0

    try:
        fglf = pyfits.open(fglfile)
    except():
        return 0.0, -1, "Failed to open catalog file"
    
    source = fglf[1].data.field('Source_name')
    ra = fglf[1].data.field('RAJ2000')
    dec = fglf[1].data.field('DEJ2000')
    flux = fglf[1].data.field('Flux1000')
    sra,sdec,sind = get_fgl_source_coords(sname,fglfile)
    if sind == -1:
        print "Failed to querry 2FGL file ",fglfile," for the coordinates of ",sname
        return 0.0,-1

#    indexes = [ i for i in range(len(source)) if sdist(ra[i],dec[i],sra,sdec) < radius and source[i] != sname ]

    spcx = 0.0
    for i in range(len(source)):
        dist = sdist(ra[i],dec[i],sra,sdec)
        if dist < radius and  i != sind:
            spcx += flux[i]/(2.0+dist*dist)


    spcx = spcx/flux[sind]
    print "Source proximity coefficient for ",sname,":",spcx
    return spcx, 1

    
    
