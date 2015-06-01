"""
    Collection of functions for retrieving files from the BIPM
    ftp server.
    File types include:
    - Circular-T
    - UTC-rapid
    - RINEX
    - LZ (offset from RINEX receiver clock to UTC(k))
    
    AW 2013-2015
"""
import ftplib
import datetime
import pytz
import sys
import os 
import math
import numpy

import jdutil  # mjd-functions

def check_dir(target_dir):
    # check that directory exsits, create if not
    if not os.path.isdir(target_dir):
        print "creating target directory ", target_dir
        os.mkdir(target_dir)

def bipm_utcr_download(prefixdir=""):
    """
    Download UTC-rapid datafile from BIPM
    """
    print "bipm_utcR_download start ", datetime.datetime.now()
    
    target_dir = prefixdir + "/UTCr/"
    check_dir(target_dir)

    # Connection information
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
                   ["pub/tai/publication/utcrlab/","utcr-usno"] ]

    ftp = ftplib.FTP(server)
    ftp.login(username, password)
    current_dir=""
    for filedata in utcr_files:
        bipm_directory = filedata[0]
        bipm_file = filedata[1]
        local_file = target_dir + bipm_file
        print "Downloading: ",local_file
        # Change to the proper directory
        if bipm_directory != current_dir:
            ftp.cwd(bipm_directory)
            current_dir = bipm_directory
        # Loop through matching files and download each one individually
        fhandle = open(local_file, 'wb')
        ftp.retrbinary('RETR ' + bipm_file, fhandle.write)
        fhandle.close()
    ftp.close()               
    print "bipm_utcR_download Done ", datetime.datetime.now()
          
def bipm_utc_download(prefixdir=""):
    """
    Download Circular-T data from BIPM website.
    
    placed in prefixdir/UTC/
    """
    print "bipm_utc_download start ", datetime.datetime.now()
    
    target_dir = prefixdir + "/UTC/"
    check_dir(target_dir)
    
    # Connection information
    server = "ftp2.bipm.org" #'5.144.141.242'
    username = '' # don't need a possword for circular-T
    password = ''

    sys.stdout.flush()
    # directories and files to download
    utc_files= [ ["pub/tai/publication/utclab/","utc-mike"],
                 ["pub/tai/publication/utclab/","utc-usno"],
                 ["pub/tai/publication/utclab/","utc-ptb"],
                 ["pub/tai/publication/utclab/","utc-nict"],
                 ["pub/tai/publication/utclab/","utc-nist"],
                 ["pub/tai/publication/utclab/","utc-sp"],
                 ["pub/tai/publication/utclab/","utc-op"],
                 ["pub/tai/publication/utclab/","utc-npl"] ]

                   
    # Establish the connection
    ftp = ftplib.FTP(server)
    ftp.login(username, password)
    current_dir=""
    for filedata in utc_files:
        bipm_directory = filedata[0]
        bipm_file = filedata[1]
        local_file = target_dir + bipm_file
        print "Downloading: ", local_file
        # Change to the proper directory
        if bipm_directory != current_dir:
            ftp.cwd(bipm_directory)
            current_dir = bipm_directory
        # Loop through matching files and download each one individually
        fhandle = open(local_file, 'wb')
        ftp.retrbinary('RETR ' + bipm_file, fhandle.write)
        fhandle.close()
    ftp.close()
    sys.stdout.flush()
    print "bipm_utc_download Done ", datetime.datetime.now()

def read_UTC(prefixdir, station, rapid=False):
    """
    Read Circular-T or UTC-Rapid data
    """
    
    if rapid:
        utcfile = prefixdir + "/UTCr/utcr-%s" % station.utctag
    else:
        utcfile = prefixdir + "/UTC/utc-%s" % station.utctag
    print "read_UTC reading: ", utcfile
    t = [] # mjd
    x = [] # UTC-UTC(k) in nanoseconds
    with open(utcfile) as f: # parse the circular-T or UTC-rapid format
        for line in f:
            line2 = line.split()
            #print line2
            if len(line2) >= 2:
                try:
                    mjd =  int(line2[0]) 
                    ns =  float(line2[1]) 
                    t.append( mjd )
                    x.append( ns )
                    #print int(line2[0]), float(line2[1] )
                except:
                    pass
    assert( len(t) == len(x) )
    return (t,x)

class UTCStation():
    """
    Class to represent a GPS station producing RINEX files.
    
    May be modified later to include 'local' stations where we find the RINEX
    on disk rather than via FTP.
    """
    def __init__(self, name= "", utctag="", bipm_rinexdir="", lz=False, rinexname="", refdelay=0, prefixdir=""):
        self.name = name
        self.utctag = utctag
        self.bipm_dir = bipm_rinexdir
        self.lz = lz # do we need an LZ file or not?
        self.rinexname = rinexname # the name of the rinex file
        self.refdelay = float(refdelay) # reference delay, in nanoseconds
        self.receiver=""
        self.rinex = self.rinex1
        self.prefixdir=prefixdir
        self.hatanaka = False # some stations use Hatanaka compressed RINEX
        
    # the naming convention is that there is no convention...
    def rinex1(self,dt):# NIST style name
        fname = "%s%03d0.%02dO.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        return fname
        
    def rinex2(self,dt):# USNO style name
        fname = "%s%03d0.%02do.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        return fname

    def rinex3(self,dt): # OP style name
        fname = "%s%03d0.%02dd.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        self.hatanaka = True
        return fname
    
    def rinex4(self,dt): # PTB style name
        fname = "%s%03d0.%02dD.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        self.hatanaka = True
        return fname
        
    def rinex_download( self, dt):
        """
        Download the RINEX file for datetime dt.
        Place it in the station.name directory.
        If it already exists, don't download.
        Return the full filename.
        """
        rinex_file = self.rinex(dt)
        check_dir(self.prefixdir+"/stations/")
        target_dir = self.prefixdir + "/stations/" + self.name + "/"
        local_file = target_dir + rinex_file
        print "bipm_rinex_download start at", datetime.datetime.now()
        if not os.path.exists( local_file ):
            # check that target dir exists, if not create it
            check_dir(target_dir)
            
            server = '5.144.141.242' # Connection information
            username = 'labotai'
            password = 'dataTAI'
            print 'Remote ', rinex_file
            print 'Local ', local_file
            sys.stdout.flush()
             
            ftp = ftplib.FTP(server)  # Establish the connection
            ftp.login(username, password)
            ftp.cwd(self.bipm_dir) # Change to the proper directory
            # Loop through matching files and download each one individually
            fhandle = open(local_file, 'wb')
            ftp.retrbinary('RETR ' + rinex_file, fhandle.write)
            fhandle.close()
            ftp.close()
        else:
            print rinex_file," already exists. not downloading."
        print "bipm_rinex_download Done ", datetime.datetime.now()
        sys.stdout.flush()
        return local_file
        
    
# example stations
current_dir = os.getcwd() # the current directory

#### USNO 
usno = UTCStation( name="USNO", utctag="usno", 
                   bipm_rinexdir="/data/UTC/USNO/links/rinex/", 
                   refdelay=0.0,prefixdir=current_dir)
usno.receiver= "usn6"
usno.rinex = usno.rinex2

### NIST
nist = UTCStation( name="NIST", utctag="nist", 
                   bipm_rinexdir="data/UTC/NIST/links/rinex/", 
                   refdelay=120.0-7.043,prefixdir=current_dir)
# Note on NIST reference delay ftp://5.144.141.242/data/UTC/NIST/links/cggtts/GMNI0056.735
nist.receiver= "NIST"
nist.rinex = nist.rinex1

### MIKE
mike = UTCStation( name="MIKE", utctag="mike", 
                   bipm_rinexdir="data/UTC/MIKE/links/rinex/",
                   refdelay = 2.9, prefixdir= current_dir)
mike.rinex = mike.rinex1
mike.receiver = "MIGT"

### OP
op = UTCStation( name="OP", utctag="op",        
                 bipm_rinexdir = "data/UTC/OP/links/rinex/opmt/",
                 refdelay = 349.0, prefixdir = current_dir)
                 # refdelay is empirically found mean of CirT error vs. usn3
op.rinex = op.rinex3
op.receiver = "opmt"

### SP
sp = UTCStation( name="SP", utctag="sp",        
                 bipm_rinexdir = "data/UTC/SP/links/rinex/",
                 refdelay = 221.5-2.279, prefixdir = current_dir)
# ftp://5.144.141.242/data/UTC/SP/links/cggtts/gzSP0156.752 OR ftp://5.144.141.242/data/UTC/SP/links/cggtts/rzSP0256.751
sp.rinex = sp.rinex3
sp.receiver = "sp01"
        
### NICT
nict = UTCStation( name="NICT", utctag="nict",        
                 bipm_rinexdir = "data/UTC/NICT/links/rinex/",
                 refdelay = 17.628, prefixdir = current_dir)
nict.rinex = nict.rinex2
nict.receiver = "nc02"

### NPL
npl = UTCStation( name="NPL", utctag="npl",        
                 bipm_rinexdir = "data/UTC/NPL/links/rinex/",
                 refdelay = -2.797, prefixdir = current_dir)
npl.rinex = npl.rinex1
npl.receiver = "NP11"

### PTB
ptb = UTCStation( name="PTB", utctag="ptb",        
                 bipm_rinexdir = "data/UTC/PTB/links/rinex/PTBG/",
                 refdelay = 335.6+132.0, prefixdir = current_dir)
ptb.rinex = ptb.rinex4
ptb.receiver = "PTBG"

if __name__ == "__main__":
    
    
    # an example of how to download UTC/UTCr data
    #bipm_utcr_download(prefixdir=current_dir) # download UTCr files
    #bipm_utc_download(prefixdir=current_dir)  # download Circular-T files
    
    # an example of how to retrieve a RINEX file
    dt = datetime.datetime.now() - datetime.timedelta(days=5) # 5 days back from now
    
    print usno.rinex_download(dt)
    print nist.rinex_download(dt)
    print mike.rinex_download(dt)
    print op.rinex_download(dt)
    print sp.rinex_download(dt)
    print nict.rinex_download(dt)
    print npl.rinex_download(dt)
    print ptb.rinex_download(dt)


    pass
