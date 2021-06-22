"""
    Collection of functions for retrieving files from the BIPM
    ftp server.
    File types include:
    - Circular-T
    - UTC-rapid
    - RINEX
    - LZ (offset from RINEX receiver clock to UTC(k))
    
    This file is part of ppp-tools, https://github.com/aewallin/ppp-tools
    GPLv2 license.
"""
# import ftplib
import datetime
import pytz
import os 
import sys
import math
import numpy

import jdutil  # mjd-functions
import ftp_tools # downloads files using ftp



def bipm_utcr_download():
    """
    Download UTC-rapid datafile from BIPM
    place result in the UTCr/ subdirectory
    """
    print("bipm_utcR_download start ", datetime.datetime.utcnow())
    
    current_dir = os.getcwd() # the current directory
    localdir = current_dir + "/UTCr/"
    server = "ftp2.bipm.org"   #  IP number '5.144.141.242'
    username = ''
    password = ''

    sys.stdout.flush()
    # list of directories and files we want
    utcr_files = [ ["pub/tai/publication/utcrlab/","utcr-op"],
                   ["pub/tai/publication/utcrlab/","utcr-ptb"],
                   ["pub/tai/publication/utcrlab/","utcr-nict"],
                   ["pub/tai/publication/utcrlab/","utcr-nist"],
                   ["pub/tai/publication/utcrlab/","utcr-sp"],
                   ["pub/tai/publication/utcrlab/","utcr-usno"],
                   ["pub/tai/publication/utcrlab/","utcr-mike"] ]
    
    for (remotedir, remotefile) in utcr_files:
        ftp_tools.ftp_download( server, username, password, remotedir, remotefile, localdir, overwrite=True)

    print("bipm_utcR_download Done ", datetime.datetime.utcnow())
          
def bipm_utc_download(prefixdir=""):
    """
    Download Circular-T data from BIPM website.
    
    placed in UTC/ subdirectory
    """
    print("bipm_utc_download start ", datetime.datetime.utcnow())
    current_dir = os.getcwd()
    localdir = current_dir + "/UTC/"
    # Connection information
    server = "ftp2.bipm.org" #'5.144.141.242'
    username = '' # don't need a password for circular-T
    password = ''

    # directories and files to download
    utc_files= [ ["pub/tai/publication/utclab/","utc-mike"],
                 ["pub/tai/publication/utclab/","utc-usno"],
                 ["pub/tai/publication/utclab/","utc-ptb"],
                 ["pub/tai/publication/utclab/","utc-nict"],
                 ["pub/tai/publication/utclab/","utc-nist"],
                 ["pub/tai/publication/utclab/","utc-sp"],
                 ["pub/tai/publication/utclab/","utc-op"],
                 ["pub/tai/publication/utclab/","utc-npl"] ]

    for (remotedir, remotefile) in utc_files:
        ftp_tools.ftp_download( server, username, password, remotedir, remotefile, localdir, overwrite=True)

    
    print("bipm_utc_download Done ", datetime.datetime.utcnow())

def read_UTC(prefixdir, station, rapid=False):
    """
    Read Circular-T or UTC-Rapid data
    Format:
    # comments start with "#"
    MJD1 UTC-UTC(k)/ns
    MJD2 UTC-UTC(k)/ns
    ...
    """
    
    if rapid:
        utcfile = prefixdir + "/UTCr/utcr-%s" % station.utctag
    else:
        utcfile = prefixdir + "/UTC/utc-%s" % station.utctag
    print("read_UTC reading: ", utcfile)
    t = [] # mjd
    x = [] # UTC-UTC(k) in nanoseconds
    with open(utcfile) as f: # parse the circular-T or UTC-rapid format
        for line in f:
            line2 = line.split()
            if len(line2) >= 2:
                try:
                    mjd =  int(line2[0]) 
                    ns =  float(line2[1]) 
                    t.append( mjd )
                    x.append( ns )
                except:
                    pass
    assert( len(t) == len(x) )
    return (t,x)



if __name__ == "__main__":
    
    # an example of how to download UTC/UTCr data
    bipm_utcr_download() # download UTCr files
    bipm_utc_download()  # download Circular-T files
    
    pass
