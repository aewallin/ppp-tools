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

def bipm_utcr_download(prefixdir=""):
    """
    Download UTC-rapid datafile from BIPM
    """
    print "bipm_utcR_download start ", datetime.datetime.now()
    
    target_dir = prefixdir + "/UTCr/"
    # check that directory exists, if not create it
    if not os.path.isdir(target_dir):
        print "creating target directory ", target_dir
        os.mkdir(target_dir)
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
    # check that directory exists, if not create it
    if not os.path.isdir(target_dir):
        print "creating target directory ", target_dir
        os.mkdir(target_dir)
    
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


            
def bipm_file(station=None, day=None, prefixdir=""):

    if station=="opmt":
        
        bipm_dir = "data/UTC/OP/links/rinex/opmt/"
        outfile = prefixdir + "/%s/%s" % (station, fname)
        bipm_rinex_download(bipm_dir, fname, outfile)

    if station=="sp01":
        fname = "%s%03d0.%02dd.Z" % (station,doy, year)
        bipm_dir = "data/UTC/SP/links/rinex/"
        outfile = prefixdir + "/%s/%s" % (station, fname)
        bipm_rinex_download(bipm_dir, fname, outfile)
        #offset = 221.3
        
    if station=="nc02":
        fname = "%s%03d0.%02do.Z" % (station,doy, year)
        bipm_dir = "data/UTC/NICT/links/rinex/"
        outfile = prefixdir + "/%s/%s" % (station, fname)
        bipm_rinex_download(bipm_dir, fname, outfile)
        # REF DLY =   416.8 ns ??
        
    if station=="NP11":
        if doy in range(35,55+1):
            fname = "%s%03d0.%02dO.z" % (station,doy, year)
        elif doy in range(280,299+1):
            fname = "%s%03d0.%02dO.z" % (station,doy, year)
        else:
            fname = "%s%03d0.%02dO.Z" % (station,doy, year)
        bipm_dir = "data/UTC/NPL/links/rinex/"
        outfile = prefixdir + "/%s/%s" % (station, fname)
        bipm_rinex_download(bipm_dir, fname, outfile)
                


    return (outfile, fname)

# for OP, we also need an LZ file.
def bipm_lz_download(dt):
    """
    Download LZ file.
    
    example file:
    ftp://5.144.141.242/data/UTC/OP/links/rinex/opmt/LZOP0156.847
    """
    print "bipm_lz_download start ", datetime.datetime.now()
    bipm_directory = "data/UTC/OP/links/rinex/opmt/"
    
    mjd = jdutil.jd_to_mjd( jdutil.datetime_to_jd( dt ) )
    print "MJD = ", mjd, " floor = ", math.floor(mjd)
    bipm_file = "LZOP01%5d" % math.floor(mjd)
    # now insert the dot.
    bipm_file = bipm_file[:8] + '.' + bipm_file[8:]
    print bipm_file
    prefixdir = "/home/anders/Dropbox/gpsppp/BIPM"
    local_file = prefixdir + "/%s/%s" % ("opmt", bipm_file)
    print local_file
    localfile = bipm_rinex_download( bipm_directory, bipm_file, local_file)
    return localfile

def CODE_read_file(fname):
    """
    Read result file
    """
    t = [] # datetime
    x = [] # clock-offset ns
    print "reading ",fname
    with open(fname) as f:
        for line in f:
            if line.startswith("#"):
                pass
            else:
                line2 = line.split()
                if len(line2) == 8:
                    year   = int(line2[0])
                    month  = int(line2[1])
                    day    = int(line2[2])
                    hour   = int( line2[3] )
                    minute = int( line2[4] )
                    second = int( line2[5] )
                    # ignore column 6 (?)
                    ns =   float( line2[7] )
                    dt = datetime.datetime( year, month, day, hour, minute, second, tzinfo=pytz.UTC)                    
                    t.append(dt)
                    x.append(ns)
                elif len(line2) == 7:
                    year   =  int(line2[0])
                    month  = int(line2[1])
                    day    = int(line2[2])
                    hour   = int( line2[3] )
                    minute = int( line2[4] )
                    second = int( line2[5] )
                    ns =   float( line2[6] )
                    dt = datetime.datetime( year, month, day, hour, minute, second, tzinfo=pytz.UTC)                    
                    t.append(dt)
                    x.append(ns)
    return (t,x)

def COD_read_day(prefixdir, station, year, day, rapid):
    fname = ""
    rapidfinal = "Final"
    if rapid:
        rapidfinal = "Rapid"
    
    if station == "MIGT":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.%s.txt" % ( station , station, day, year-2000, rapidfinal)
    
    if station == "opmt":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dd.COD.%s.txt" % ( station , station, day, year-2000, rapidfinal)
        #if not os.path.exists(fname):
        #    fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dd.COD.Rapid.txt" % ( station , station, day, year-2000, )
    
    if station == "MI02":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.Rapid.txt" % ( station , station, day, year-2000, )

    if station == "usn3":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02do.COD.Final.txt" % ( station , station, day, year-2000, )
        if not os.path.exists(fname):
            if day > 105 or year==2015:
                fname = prefixdir + "/%s/COD_Final/%s%03d0.%02do.COD.%s.txt" % ( station , "usn6", day, year-2000, rapidfinal)
            else:
                fname = prefixdir + "/%s/COD_Final/%s%03d0.%02do.COD.Rapid.txt" % ( station , station, day, year-2000, )

    if station == "NIST":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.Final.txt" % ( station , station, day, year-2000, )
        if not os.path.exists(fname):
            fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.Rapid.txt" % ( station , station, day, year-2000, )

    if station == "nc02":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02do.COD.Final.txt" % ( station , station, day, year-2000, )
        if not os.path.exists(fname):
            fname = prefixdir + "/%s/COD_Final/%s%03d0.%02do.COD.Rapid.txt" % ( station , station, day, year-2000, )
    if station == "PTBG":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dD.COD.Final.txt" % ( station , station, day, year-2000, )
        if not os.path.exists(fname):
            fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dD.COD.Rapid.txt" % ( station , station, day, year-2000, )
    if station == "sp01":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dd.COD.Final.txt" % ( station , station, day, year-2000, )
        if not os.path.exists(fname):
            fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dd.COD.Rapid.txt" % ( station , station, day, year-2000, )
    if station == "NP11":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.Final.txt" % ( station , station, day, year-2000, )
        if not os.path.exists(fname):
            fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.Rapid.txt" % ( station , station, day, year-2000, )
    if station == "KAJA":
        fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.Final.txt" % ( "GTR51" , station, day, year-2000, )
        if not os.path.exists(fname):
            fname = prefixdir + "/%s/COD_Final/%s%03d0.%02dO.COD.Rapid.txt" % ( "GTR51" , station, day, year-2000, )
    if station == "WR01":
        fname = prefixdir + "/%s/%s%03d.%02d.txt" % ( station , station, day, year-2000, )

    if station == "oplz":
        fname = prefixdir + "/opmt/COD_Final/%s%03d0.%4d.txt" % ( station , day, year )
        
    (t,ns) = COD_read_file( fname )
    (t2,ns2) = mad.remove_timeseries_outliers(t,ns)
    return (t2,ns2)

def read_UTC(prefixdir, station, rapid=False):
    """
    Read Circular-T or UTC-Rapid data
    """
    
    """
    utctag = ""
    if station=="MIGT":
        utctag = "mike"
    elif station=="usn3":
        utctag = "usno"
    elif station=="NIST":
        utctag = "nist"
    elif station=="opmt":
        utctag = "op"
    elif station=="nc02":
        utctag = "nict"
    elif station=="PTBG":
        utctag = "ptb"
    elif station=="sp01":
        utctag = "sp"
    elif station=="NP11":
        utctag = "npl"
    elif station=="oplz":
        utctag = "op"
    elif station=="KAJA":
        return ([0],[0])
    """
    if rapid:
        utcfile = prefixdir + "/UTCr/utcr-%s" % station.utctag
    else:
        utcfile = prefixdir + "/UTC/utc-%s" % station.utctag
    print "read_UTC reading: ", utcfile
    t = []
    x = []
    # parse the circular-T or UTC-rapid format
    with open(utcfile) as f:
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
    # OP fname = "%s%03d0.%02dd.Z" % (station,doy, year)


    def rinex_download( self, dt):
        """
        Download the RINEX file for datetime dt.
        Place it in the station.name directory.
        If it already exists, don't download.
        Return the full filename.
        """
        rinex_file = self.rinex(dt)
        target_dir = self.prefixdir + "/" + self.name + "/"
        local_file = target_dir + rinex_file
        print "bipm_rinex_download start at", datetime.datetime.now()
        if not os.path.exists( local_file ):
            # check that target dir exists, if not create it
            if not os.path.isdir(target_dir):
                print "creating target directory ", target_dir
                os.mkdir(target_dir)
            
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

print usno.rinex(datetime.datetime(2015,5,5))

offset = { 'NP11': 0.0-2.797, 
           'usn3': 0.0,
           'MIGT': 0.0,   # 2.8ns ??
           'sp01': 221.5-2.279, # ftp://5.144.141.242/data/UTC/SP/links/cggtts/gzSP0156.752 OR ftp://5.144.141.242/data/UTC/SP/links/cggtts/rzSP0256.751
           'PTBG': 335.6+132.0,
            # PTBG receiver: RT902232501         ASHTECH Z-XII3T     1L01-1D04 
            # PT03 ASHTECH Z12T RT902232501      R2CGGTTS v4.3
            # CAB DLY =  251.4 ns (GPS)
            # REF DLY =   84.2 ns
            'nc02': 17.628,
            # CAB DLY =   248.5 ns (GPS)
            # REF DLY =   416.8 ns after 2014-04-22 REF DLY = 422.5 ns
            # REF = UTC(NICT)
            'MI02': 0.0,
            'oplz':  349} # mean of CirT error vs. usn3



def read_lz(lzfile):
    """
    read LZ file
    """
    t = []
    x = []
    with open(lzfile) as f:
        for line in f:

            line2 = line.split()
            #print line2
            if len(line2) >= 2:
                try:
                    mjd = float(line2[0]) 
                    ns =  float(line2[1]) 
                    
                    t.append( mjd )
                    x.append( ns )
                    #print int(line2[0]), float(line2[1] )
                except:
                    pass
    assert( len(t) == len(x) )
    return (t,x)

def op_lz_process(prefixdir,dt, rapid):
    mjd = jdutil.jd_to_mjd( jdutil.datetime_to_jd( dt ) )
    doy = dt.timetuple().tm_yday
    year = dt.year
    print "op_lz_process()"
    print "year= ", year
    print "mjd=  ", mjd
    print "doy=  ", doy
    
    station = "oplz" # new output file name
    fname = "%s%03d0.%02d.txt" % (station,doy, year)
    #prefixdir = "/home/anders/Dropbox/gpsppp/BIPM"
    resultfile = prefixdir + "/opmt/COD_Final/%s" % fname
    print resultfile
    if os.path.exists(resultfile):
        print "result exists, nothing to do: ", resultfile
        return
        
    # get the lz file
    lzfile = bipm_lz_download( dt )
    print lzfile
    (mjd,x) = read_lz( lzfile )
    #print mjd,x 
    # polyfit a line to the data
    p = numpy.polyfit(mjd,x,1)
    print p
    print numpy.polyval(p,mjd[0])
    
    station = "oplz"
    fname = "%s%03d0.%02d.txt" % (station,doy, year)
    prefixdir = "/home/anders/Dropbox/gpsppp/BIPM"
    resultfile = prefixdir + "/opmt/COD_Final/%s" % fname
    print resultfile
    if not os.path.exists(resultfile):
        # generate a new file
        station = "opmt"
        (dtlist, nslist) = COD_read_day(prefixdir, station, year, doy, rapid)
        dt2list = []
        ns2list = []
        for (dtl, nsl) in zip(dtlist,nslist):
            mjdl = jdutil.jd_to_mjd( jdutil.datetime_to_jd( dtl ) )
            lzcorr = numpy.polyval(p,mjdl)
            nscorr = nsl + lzcorr
            #print mjdl, nsl, lzcorr, nscorr
            dt2list.append( dtl )
            ns2list.append( nscorr )
        archive_oplz(resultfile, dt2list, ns2list)
    else:
        print "result already exists nothing to do."

def archive_oplz(fname, dtl, nsl):
    print "archiving ", len(dtl), " numbers to", fname
    with open(fname,'w') as f:
        datastring = "# " + fname + " \n"
        f.write(datastring)
        datastring = "# Year\tMonth\tDay\tHour\tMin\tSec\tSecs\tClock(ns)\n"
        f.write(datastring)
        for (t,n) in zip(dtl,nsl):
            datastring = "%d\t%d\t%d\t%d\t%d\t%d\t%d\t%0.3f\n" % ( t.year, t.month, t.day, t.hour, t.minute, t.second, t.second, float(n)  )
            #datastring = "%d %d %d %d %d %d %d %f \n" % ( int(t[0]), int(t[1]),int(t[2]),int(t[3]),int(t[4]), int(t[5]),int(s),float(n) )
            #print datastring 
            f.write(datastring)

if __name__ == "__main__":
    
    
    # an example of how to download UTC/UTCr data
    #bipm_utcr_download(prefixdir=current_dir) # download UTCr files
    #bipm_utc_download(prefixdir=current_dir)  # download Circular-T files
    
    # an example of how to retrieve a RINEX file
    dt = datetime.datetime.now() - datetime.timedelta(days=5) # 5 days back from now
    
    print usno.rinex_download(dt)
    print nist.rinex_download(dt)
    print mike.rinex_download(dt)
    
    #
    #op_lz_process(prefixdir,dt)
    
    #(t,ns) = COD_read_file('/home/anders/Dropbox/gpsppp/BIPM/GTR51/COD_Final/KAJA0100.14O.COD.Final.txt')
    #(t,ns) = COD_read_file('/home/anders/Dropbox/gpsppp/BIPM/MIGT/COD_Final/MIGT0190.14O.COD.Final.txt')
    #(t2,ns2) = COD_remove_outliers(t,ns) 
    #(t,x) = COD_read_day('/home/anders/Dropbox/gpsppp/BIPM/', 'MIGT', 2014, 19)
    #(t,x) = read_UTC('/home/anders/Dropbox/gpsppp/BIPM/', 'MIGT')
    #print len(t), len(x)
    #print t
    #print x
    pass
