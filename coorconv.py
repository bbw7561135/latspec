#from math import *
import numpy as np
#import celgal
try:
    from numarray import *
except ImportError:
    import math
    from math import *
    arcsin = asin
    arccos = acos
    arctan2 = atan2


def loffset(l, b, off):
    sld = sin(radians(b))
    cld = cos(radians(b))
    coffd = cos(radians(off))
    return degrees(acos((coffd - sld * sld) / cld / cld))



def sdist(l1, d1, l2, d2):
#    conv = celgal()
    return dist([l1,d1],[l2,d2])
#degrees(acos(sin(radians(d1)) * sin(radians(d2)) + cos(radians(d1)) * cos(radians(d2)) * cos(radians(l1 - l2))))



def eq2gal(ra, dec):
#    r = radians(ra)
#    d = radians(dec)
#    pole_ra = radians(192.859508)
#    pole_dec = radians(27.128336)
#    posangle = radians(32.932)
#    bb = asin(cos(d) * cos(pole_dec) * cos(r - pole_ra) + sin(d) * sin(pole_dec))
#    ll = atan2(sin(d) - sin(bb) * sin(pole_dec), cos(d) * sin(r - pole_ra) * cos(pole_dec)) + posangle
#    return (degrees(ll), degrees(bb))
    conv = celgal()
    return conv.gal([ra,dec])



def gal2eq(ll, bb):
#    ga = [ll, bb]
#    l = radians(ga[0])
#    b = radians(ga[1])
#    pole_ra = radians(192.859508)
#    pole_dec = radians(27.128336)
#    posangle = radians(32.932)
#    ra = atan2(cos(b) * cos(l - posangle), sin(b) * cos(pole_dec) - cos(b) * sin(pole_dec) * sin(l - posangle)) + pole_ra
#    dec = asin(cos(b) * cos(pole_dec) * sin(l - posangle) + sin(b) * sin(pole_dec))
#    return (degrees(ra), degrees(dec))
    conv = celgal()
    return conv.cel([ll,bb])

class celgal:
    def __init__(self, J2000=1):
        #
        # Rotation angles for the two most common epochs
        #
        if J2000:
            self.zrot1 = 282.8592
            self.xrot = 62.8717
            self.zrot2 = 32.93224
        else: # use B1950 values
            self.zrot1 = 282.25
            self.xrot = 62.6
            self.zrot2 = 33.

        self.cos_xrot = cos(self.xrot*pi/180.)
        self.sin_xrot = sin(self.xrot*pi/180.)

    def gal(self, radec):
        (ra, dec) = radec
        return (self.glon(ra, dec), self.glat(ra, dec))

    def cel(self, lb):
        (glon, glat) = lb
        return (self.RA(glon, glat), self.DEC(glon, glat))

    def glon(self, ra, dec) :
        """Galactic longitude as a function of Equatorial coordinates"""
        sdec = sin(dec*pi/180.)
        cdec = cos(dec*pi/180.)
        sdra = sin((ra-self.zrot1)*pi/180.)
        cdra = cos((ra-self.zrot1)*pi/180.)
        glon = self.zrot2 + arctan2(cdec*sdra*self.cos_xrot+sdec*self.sin_xrot,
                                    cdec*cdra)*180./pi
        try:
            if glon < 0. : glon += 360.
            if glon > 360. : glon -= 360.
        except RuntimeError:
            for i in xrange(len(glon)):
                if glon[i] < 0.: glon[i] += 360.
                if glon[i] > 360.: glon[i] -= 360.
        return glon

    def glat(self, ra, dec) :
        """Galactic latitude as a function of Equatorial coordinates"""
        sdec = sin(dec*pi/180.)
        cdec = cos(dec*pi/180.)
        sdra = sin((ra-self.zrot1)*pi/180.)
        return arcsin(sdec*self.cos_xrot-cdec*sdra*self.sin_xrot)*180./pi
            
    def RA(self, longitude, latitude) :
        """Right ascension as a function of Galactic coordinates"""
        clat = cos(latitude*pi/180.)
        slat = sin(latitude*pi/180.)
        cdlon = cos((longitude-self.zrot2)*pi/180.)
        sdlon = sin((longitude-self.zrot2)*pi/180.)
        ra = self.zrot1 + arctan2(clat*sdlon*self.cos_xrot-slat*self.sin_xrot,
                                  clat*cdlon)*180./pi
        try:
            if ra < 0. : ra = ra + 360.
            if ra > 360. : ra = ra - 360.
        except RuntimeError:
            for i in xrange(len(ra)):
                if ra[i] < 0.: ra[i] += 360.
                if ra[i] > 360.: ra[i] -= 360.
        return ra

    def DEC(self, longitude, latitude) :
        """Declination as a function of Galactic coordinates"""
        clat = cos(latitude*pi/180.)
        slat = sin(latitude*pi/180.)
        sdlon = sin((longitude-self.zrot2)*pi/180.)
        return arcsin(clat*sdlon*self.sin_xrot+slat*self.cos_xrot)*180./pi
    
def dist(a, b):
    """Angular separation in degrees between two sky coordinates"""
    ra1, dec1 = a
    ra2, dec2 = b
    ra1 = ra1*pi/180.
    dec1 = dec1*pi/180.
    ra2 = ra2*pi/180.
    dec2 = dec2*pi/180.
    mu = (cos(dec1)*cos(ra1)*cos(dec2)*cos(ra2)
          + cos(dec1)*sin(ra1)*cos(dec2)*sin(ra2) + sin(dec1)*sin(dec2))
    return Angdist(mu)*180./pi

def Angdist(x):
    """Angular distance in radians corresponding to a cosinus""" 
    if abs(x) < 1:
        angdist = arccos(x)
    elif abs(x) < 1.00001:
        angdist = math.pi/2.*(1 - int(x))
    else:
        raise ValueError, "x must be smaller than 1"
    return angdist 

