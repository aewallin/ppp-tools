import os
import datetime

import bipm_ftp

class UTCStation():
    """
    Class to represent a GPS station producing RINEX files.
    
    May be modified later to include 'local' stations where we find the RINEX
    on disk rather than via FTP.
    """
    def __init__(self, name= "", utctag="", ftp_server="", ftp_dir="", lz=False, rinexname="", refdelay=0, prefixdir=""):
        self.name = name      # e.g. "USNO
        self.utctag = utctag  # when name is more than 4 characters, BIPM abbreviates with 4 chars, e.g. "MIKE"
        self.ftp_server = ftp_server 
        self.ftp_dir = ftp_dir  # the directory for RINEX files on the ftp server
        self.lz = lz # do we need an LZ file or not?
        self.rinexname = rinexname # the name of the rinex file
        self.refdelay = float(refdelay) # reference delay, in nanoseconds
        self.receiver=""
        self.rinex_filename = self.rinex1
        self.hatanaka = False # some stations use Hatanaka compressed RINEX
        
    # the RINEX naming convention is that there is no convention...
    # we define rinex_filename() in the constructor, which calls one of rinex1(), rinex2(), etc.
    
    def rinex1(self,dt):# NIST style name, with capital "O"
        fname = "%s%03d0.%02dO.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        return fname
        
    def rinex2(self,dt):# USNO style name, with small "o"
        fname = "%s%03d0.%02do.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        return fname

    def rinex3(self,dt): # OP style name, compressed with "d"
        fname = "%s%03d0.%02dd.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        self.hatanaka = True
        return fname
    
    def rinex4(self,dt): # PTB style name, compressed with "D"
        fname = "%s%03d0.%02dD.Z" % (self.receiver, dt.timetuple().tm_yday, dt.year-2000) 
        self.hatanaka = True
        return fname
    
    def get_rinex(self,dt):
        """
            Retrieve RINEX file using ftp
        """
        current_dir = os.getcwd()
        localdir = current_dir + '/stations/' + self.name + '/'
        return bipm_ftp.ftp_download( self.ftp_server, self.ftp_username, self.ftp_password,
                         self.ftp_dir, self.rinex_filename(dt), localdir)
        
########################################################################
# example stations
#
# these are from the BIPM ftp-server, but could be from anywhere.
#
########################################################################

bipm_server = '5.144.141.242'
bipm_username = 'labotai'
bipm_password = 'dataTAI'


#### USNO 
usno = UTCStation()
usno.name="USNO"
usno.utctag="usno"
usno.ftp_server = bipm_server
usno.ftp_username = bipm_username
usno.ftp_password = bipm_password
usno.ftp_dir="/data/UTC/USNO/links/rinex/"
usno.refdelay=0.0
usno.receiver= "usn6"
usno.rinex_filename = usno.rinex2

### NIST
nist = UTCStation()
nist.name="NIST"
nist.utctag="nist" 
nist.ftp_server = bipm_server
nist.ftp_username = bipm_username
nist.ftp_password = bipm_password
nist.ftp_dir="/data/UTC/NIST/links/rinex/"
nist.refdelay=120.0-7.043 # Note on NIST reference delay ftp://5.144.141.242/data/UTC/NIST/links/cggtts/GMNI0056.735
nist.receiver= "NIST"
nist.rinex_filename = nist.rinex1


### MIKES
mikes = UTCStation()
mikes.name="MIKES"
mikes.utctag="mike" 
mikes.ftp_server = bipm_server
mikes.ftp_username = bipm_username
mikes.ftp_password = bipm_password
mikes.ftp_dir="data/UTC/MIKE/links/rinex/"
mikes.refdelay = 2.9
mikes.receiver = "MI02"
mikes.rinex_filename = mikes.rinex1


### OP
op = UTCStation()
op.name="OP"
op.utctag="op"        
op.ftp_server = bipm_server
op.ftp_username = bipm_username
op.ftp_password = bipm_password
op.ftp_dir = "data/UTC/OP/links/rinex/opmt/"
op.refdelay = 349.0 # refdelay is empirically found mean of CirT error vs. usn3
op.receiver = "opmt"
op.rinex_filename = op.rinex3


### SP
sp = UTCStation()
sp.name="SP"
sp.utctag="sp"        
sp.ftp_server = bipm_server
sp.ftp_username = bipm_username
sp.ftp_password = bipm_password
sp.ftp_dir = "data/UTC/SP/links/rinex/"
sp.refdelay = 221.5-2.279
# ftp://5.144.141.242/data/UTC/SP/links/cggtts/gzSP0156.752 
# ftp://5.144.141.242/data/UTC/SP/links/cggtts/rzSP0256.751
sp.receiver = "sp01"
sp.rinex_filename = sp.rinex3


### NICT
nict = UTCStation()
nict.name="NICT"
nict.utctag="nict"
nict.ftp_server = bipm_server
nict.ftp_username = bipm_username
nict.ftp_password = bipm_password
nict.ftp_dir = "data/UTC/NICT/links/rinex/"
nict.refdelay = 17.628
nict.receiver = "nc02"
nict.rinex_filename = nict.rinex2



### NPL
npl = UTCStation()
npl.name="NPL"
npl.utctag="npl"
npl.ftp_server = bipm_server
npl.ftp_username = bipm_username
npl.ftp_password = bipm_password 
npl.ftp_dir = "data/UTC/NPL/links/rinex/"
npl.refdelay = -2.797
npl.receiver = "NP11"
npl.rinex_filename = npl.rinex1


### PTB
ptb = UTCStation()
ptb.name="PTB"
ptb.utctag="ptb"
ptb.ftp_server = bipm_server
ptb.ftp_username = bipm_username
ptb.ftp_password = bipm_password
ptb.ftp_dir = "data/UTC/PTB/links/rinex/PTBG/"
ptb.refdelay = 335.6+132.0
ptb.receiver = "PTBG"
ptb.rinex_filename = ptb.rinex4

########################################################################

if __name__ == "__main__":
    
    # an example of how to retrieve a RINEX file
    dt = datetime.datetime.now() - datetime.timedelta(days=4) # 5 days back from now
    
    print usno.get_rinex(dt)
    print nist.get_rinex(dt)
    print mikes.get_rinex(dt)
    print op.get_rinex(dt)
    print sp.get_rinex(dt)
    print nict.get_rinex(dt)
    print npl.get_rinex(dt)
    print ptb.get_rinex(dt)
    
