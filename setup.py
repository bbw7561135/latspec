#!/usr/bin/evn python

import sys
import os
import subprocess
from distutils.core import setup


if os.environ.get("FERMI_DIR"):
    print "The Fermi Science tools seem to be set up."
else:
    print "The Fermi Science tools are not set up."
    sys.exit()

if os.environ.get("FTOOLS"):
    print "The FTOOLS seem to be set up."
else:
    print "The FTOOLS are not set up."
    sys.exit()



ds9path = subprocess.check_output(['which','ds9'])
if os.path.exists(ds9path):
    print "ds9 is found."
else:
    print "Warning: ds9 is not found."
    print "Your can still use Latspec, however interactive source/background\n selection will not be available."


setup(name='latspec',
      version='0.1.1',
      description='Fermi LAT Xspec Analysis',
      author='Nikolai Shaposhnikov (GSFC/FSSC/CRESST/UMD)',
      author_email='nikolai.v.shaposhnikov@nasa.gov',
      py_modules=['latspec',
                  'pylatspec_gui',
                  'latspec_help',
                  'psfcor',
                  'lsthreads',
                  'coorconv',
                  'fgltools'],
      scripts=['scripts/latspec'],
      )



fermidir = os.environ.get("FERMI_DIR")
if not sys.prefix == fermidir: os.system("ln -s %s/bin/latspec %s/bin/latspec"%(sys.prefix,fermidir))
