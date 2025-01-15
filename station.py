"""
    This file is part of ppp-tools, https://github.com/aewallin/ppp-tools
    GPLv2 license.
"""
import os
import datetime
import shutil
import subprocess

import bipm_ftp
import ftp_tools
import wget


class Station():
    """
    Class to represent a GPS station/receiver producing RINEX files.
    We get RINEX files by downloading them from an FTP site.

    May be modified later to include 'local' stations where we find the RINEX
    on disk rather than via FTP.
    """

    def __init__(self):
        self.name = ""          # station name e.g. "USNO"
        # when name is more than 4 characters, BIPM abbreviates with 4 chars, e.g. "MIKE"
        self.utctag = ""
        self.ftp_server = ""    # e.g. "my.ftp-server.com"
        self.ftp_dir = ""  # the directory/ for RINEX files on the ftp server
        self.ftp_username = ""
        self.ftp_password = ""
        self.lz = False         # do we need an LZ file or not?
        #self.refdelay = 0.0     # reference delay, in nanoseconds. FIXME: remove this!?
        self.receiver = ""        # receiver name, e.g. "MI02", used in the RINEX filename
        self.rinex_filename = self.rinex1
        self.hatanaka = False   # flag is True for Hatanaka compressed RINEX
        self.antex = True       # receiver antenna in ANTEX file?
        self.rinex3 = False     # RINEX version 3, requiring conversion to version 2
        
        self.ref_dly = 0.0 # delay of PPS-cable from reference plane to GNSS receiver input
        self.cab_dly = 0.0 # antenna cable delay from GNSS-receiver to antenna
        self.int_dly_p1 = 0.0 # internal GNSS receiver delay for L1
        self.int_dly_p2 = 0.0 # internal GNSS receiver delay for L2
        
        # raw PPP results are corrected with the calibrated delays as follows:
        # RX_clk_corrected = RX_clk_raw - station.cab_dly - station.int_dly_p3() + station.ref_dly
        
    def int_dly_p3(self):
        """
            ionosphere-free P3 internal delay.
            linear combination of calibrated P1 and P3 delays
        """
        return 2.5457*self.int_dly_p1 - 1.5457*self.int_dly_p2

        
    # the RINEX naming convention is that there is no convention...
    # we define rinex_filename() in the constructor, which calls one of rinex1(), rinex2(), etc.

    def rinex1(self, dt):  # NIST style name, with capital "O"
        fname = "%s%03d0.%02dO.Z" % (
            self.receiver, dt.timetuple().tm_yday, dt.year-2000)
        return fname

    def rinex2(self, dt):  # USNO style name, with small "o"
        fname = "%s%03d0.%02do.Z" % (
            self.receiver, dt.timetuple().tm_yday, dt.year-2000)
        return fname

    def rinex3(self, dt):  # OP style name, compressed with "d"
        fname = "%s%03d0.%02dd.Z" % (
            self.receiver, dt.timetuple().tm_yday, dt.year-2000)
        self.hatanaka = True
        return fname

    def rinex4(self, dt):  # PTB style name, compressed with "D"
        fname = "%s%03d0.%02dD.Z" % (
            self.receiver, dt.timetuple().tm_yday, dt.year-2000)
        self.hatanaka = True
        return fname

    def rinex5(self, dt):  # PTBG 2019 style name, compressed with "D", ending "gz"
        fname = "%s%03d0.%02dD.gz" % (
            self.receiver, dt.timetuple().tm_yday, dt.year-2000)
        self.hatanaka = True
        return fname

    def rinex6(self, dt):  # "o", ending "gz"
        fname = "%s%03d0.%02do.gz" % (
            self.receiver, dt.timetuple().tm_yday, dt.year-2000)
        self.hatanaka = False
        return fname
        
    def rinex7(self, dt):  # "O", ending "gz"
        fname = "%s%03d0.%02dO.gz" % (
            self.receiver, dt.timetuple().tm_yday, dt.year-2000)
        self.hatanaka = False
        return fname
        
    def antex(self):
        return self.antex

    def get_rinex(self, dt):
        """
            Retrieve RINEX file using ftp
            dt is the datetime for the file we want
            return filename (including path) of RINEX
            this is usually in the form:
            /stations/MYSTATION/rinex_filename.gz
        """
        current_dir = os.getcwd()
        ftp_tools.check_dir(current_dir+'/stations/')
        localdir = current_dir + '/stations/' + self.name + '/'
        ftp_tools.check_dir(localdir)
        localfile = localdir + self.rinex_filename(dt)
        if os.path.isfile(localfile):
            print(localfile, ' already exists, not downloading')
            return localfile
        else:
            print('wget from ', self.ftp_server+self.ftp_dir+self.rinex_filename(dt))
            return wget.download(self.ftp_server+self.ftp_dir+self.rinex_filename(dt), out=localdir)
        #ftp_tools.check_dir(localdir)  # create directory if it doesn't exist
        #return ftp_tools.ftp_download(self.ftp_server, self.ftp_username, self.ftp_password,
        #                              self.ftp_dir, self.rinex_filename(dt), localdir)

    def get_multiday_rinex(self, dtend, num_days=2):
        """
            get multiple 24h RINEX files
            splice them together with gfzrnx
            dtend is the datetime of the last day
            num_days is the number of days
            return filename (including path) of spliced RINEX
        """
        dtlist = [dtend - datetime.timedelta(days=n) for n in reversed(range(num_days))]
        day_files = []
        print(dtlist)
        for day in dtlist:
            day_files.append( self.get_rinex(day) )
        print('splicing files: ' + str(day_files))
        # we now have a list of zipped v2 or v3 files
        # we do processing in a temp directory
        current_dir = os.getcwd()
        tempdir = current_dir + "/temp/"
        ftp_tools.check_dir(tempdir)
        #ftp_tools.delete_files(tempdir)  # empty the temp directory
        
        # move files to the temp-directory
        moved_files=[]
        for f in day_files:
            shutil.copy2(f, tempdir)
            (tmp, fn) = os.path.split(f)
            moved_files.append(tempdir + fn)
        print(moved_files)
    
        
        
        # now unzip the files
        # unzip zipped files. this may include the RINEX, CLK, EPH files.
        for f in moved_files:
            if f[-1] == "Z" or f[-1] == "z":  # compressed .z or .Z file
                cmd = '/bin/gunzip'
                cmd = cmd + " -f " + f  # -f overwrites existing file
                print("unzipping: ", cmd)
                p = subprocess.Popen(cmd, shell=True)
                p.communicate()

        # figure out the unzipped rinex file name
        unzipped_files =[]
        #print("rinex= ", rinex)
        for f in moved_files:
            (tmp, rinexfile) = os.path.split(f)
            inputfile = rinexfile[:-2]  # strip off ".Z"
            if inputfile[-1] == ".":  # ends in a dot
                inputfile = inputfile[:-1]  # strip off
            unzipped_files.append(inputfile)
        print("unzipped files: ", str(unzipped_files))
        
        # if files are Hatanaka compressed, uncompress
        rnx_files=[]
        for inputfile in unzipped_files:
            if inputfile[-1] == "d" or inputfile[-1] == "D":
                cmd = "CRX2RNX " + tempdir+inputfile
                print("Hatanaka uncompress: ", cmd)
                p = subprocess.Popen(cmd, shell=True)
                p.communicate()
                rnx_files.append( inputfile[:-1]+"O" ) # CRX2RNX changes ending to "O"
            else:
                rnx_files.append( inputfile )
        
        print("rinex files to splice: ", len(rnx_files), " ", str(rnx_files))
        # now splice files together
        cmd = "gfzrnx -finp "
        for f in rnx_files:
            cmd += tempdir+f+" "
        # kv option to keep rinex version of splice same as input files
        # f option to overwrite output file, if it already exists
        cmd += " -fout " + tempdir+"splice.rnx" + " -kv -f"
        print("splice command: ",cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        
        # return the resulting spliced RINEX filename
        return dtlist, tempdir+"splice.rnx", moved_files
        
########################################################################
# example stations
#
# these are from the varous ftp-servers, usually UTC-laboratories.
#
########################################################################


#bipm_server = '5.144.141.242'
# NOTE: as of 2021 BIPM does not make public RINEX files anymore!
# bipm_server = 'ftp2.bipm.org'
# bipm_username = 'labotai'
# bipm_password = 'dataTAI'

mikes_server = "monitor.mikes.fi"
anonymous_username = "anonymous"
anonymous_password = "ppp-tools"

# MI04, VTT MIKES timing receiver
mi04 = Station()
mi04.name = "MI04"
mi04.utctag = "MI04"
mi04.ftp_server = "https://monitor.mikes.fi/ftp"
mi04.ftp_username = anonymous_username
mi04.ftp_password = anonymous_password
mi04.ftp_dir = "/GNSS/MI04/RINEX/"
mi04.receiver = "MI04"  # start of the RINEX filename
mi04.rinex_filename = mi04.rinex4  # naming style is MI040040.21D.Z

# MI05, VTT MIKES timing receiver, RINEX v2 files
# Information: https://monitor.mikes.fi/ftp/GNSS/MI05/MI05_info.txt
# RINEX v2 files: ftp://monitor.mikes.fi/GNSS/MI05/RINEX_v2_24h/
# Cal_ID: 1016-2019 https://webtai.bipm.org/ftp/pub/tai/publication/time-calibration/Current/1016-2019_GPSP3C1_MIKES_V1-0.pdf
mi05 = Station()
mi05.name = "MI05"
mi05.utctag = "MI05"
#mi05.ftp_server = mikes_server
mi05.ftp_server = "https://monitor.mikes.fi/ftp"
mi05.ftp_username = anonymous_username
mi05.ftp_password = anonymous_password
mi05.ftp_dir = "/GNSS/MI05/RINEX_v3_24h/"
mi05.receiver = "MI05"  # start of the RINEX filename
mi05.rinex_filename = mi05.rinex6  # naming style is MI050020.21o.gz
mi05.ref_dly = 5.092 # ns
mi05.cab_dly = 96.2 # ns
mi05.int_dly_p1 = 20.17 # ns, see Cal_ID: 1016-2019
mi05.int_dly_p2 = 18.18 # ns
mi05.rinex3 = True

# MI02, VTT MIKES timing receiver, RINEX v2 files
mi02 = Station()
mi02.name = "MI02"
mi02.utctag = "MI02"
mi02.ftp_server = mikes_server
mi02.ftp_username = anonymous_username
mi02.ftp_password = anonymous_password
mi02.ftp_dir = "/GNSS/MI02/RINEX/"
mi02.receiver = "MI02"  # start of the RINEX filename
mi02.rinex_filename = mi02.rinex1  # naming style is MI021690.21O.Z

# MI06, VTT MIKES timing receiver, RINEX v3 files
# https://monitor.mikes.fi/ftp/GNSS/MI06/
mi06 = Station()
mi06.name = "MI06"
mi06.utctag = "MI06"
#mi06.ftp_server = mikes_server
mi06.ftp_server = "https://monitor.mikes.fi/ftp"
mi06.ftp_username = anonymous_username
mi06.ftp_password = anonymous_password
mi06.ftp_dir = "/GNSS/MI06/"
mi06.receiver = "MI06"  # start of the RINEX filename
mi06.rinex_filename = mi06.rinex6  # naming style is .o.gz
mi06.rinex3 = True
mi06.ref_dly = 10.348 # ns
mi06.cab_dly = 95.715 # ns (label on cable)
mi06.int_dly_p1 = 20.17+1.7 # ns, MI05 Cal_ID: 1016-2019 - this applies for MI06 also?
mi06.int_dly_p2 = 18.18+1.7 # ns, NOTE 1.7ns added to make MI05 - MI06 results match

# prelim PPP analysis MI06-MI05 difference: 1.75 
# start 2021-04-13
# stop 2021-06-02
#
# new analysis DOY 122 to 153

# MI06 tests with local files (not on FTP-site)
mi06local = Station() # using local files, not on ftp-server
mi06local.name = "MI06local"
mi06local.utctag = "MI06local"
#mi06.ftp_server = mikes_server
#mi06.ftp_username = anonymous_username
#mi06.ftp_password = anonymous_password
#mi06.ftp_dir = "/GNSS/MI06/RINEX_v3_24h/"
mi06local.receiver = "MI06"  # start of the RINEX filename
mi06local.rinex_filename = mi06.rinex6  # naming style is .o.gz
mi06local.rinex3 = True # RINEX v3
mi06local.ref_dly = 10.348 # ns
mi06local.cab_dly = 95.715 # ns
mi06local.int_dly_p1 = 20.17+1.7  # ns
mi06local.int_dly_p2 = 18.18+1.7  # ns

# PTB, see ftp.ptb.de
# ftp://ftp.ptb.de/pub/time/GNSS/GNSS_readme_20200129.pdf
ptb_server = "ftp.ptb.de"
ptbb = Station()
ptbb.name = "PTBB" # PolaRx5_TR
ptbb.utctag = "pt13"
ptbb.ftp_server = ptb_server
ptbb.ftp_username = anonymous_username
ptbb.ftp_password = anonymous_password
ptbb.ftp_dir = "pub/time/GNSS/PT13/RINEX3/"
ptbb.refdelay = 335.6+132.0
ptbb.receiver = "PTBB"
ptbb.rinex_filename = ptbb.rinex7 # PTBB0880.21O.gz
ptbb.rinex3 = True

# PT10, Dicom/Mesit receiver
pt09 = Station()
pt09.name = "PT09" # mesit/Dicom
pt09.utctag = "PT09"
pt09.receiver = "PT09"  # start of the RINEX filename
pt09.rinex_filename = pt09.rinex7  # naming style is  "O", ending "gz"
pt09.rinex3 = True 

#pt10.ftp_server = ptb_server
#pt10.ftp_username = anonymous_username
#pt10.ftp_password = anonymous_password
#pt10.ftp_dir = "pub/time/GNSS/PT10/RINEX3/"
#pt10.refdelay = 335.6+132.0
#pt10.receiver = "PT10"
#pt10.rinex_filename = pt10.rinex1 # PT100880.21O.Z
#pt10.rinex3 = True


"""
# USNO
usno = Station()
usno.name = "USNO"
usno.utctag = "usno"
usno.ftp_server = bipm_server
usno.ftp_username = bipm_username
usno.ftp_password = bipm_password
usno.ftp_dir = "/data/UTC/USNO/links/rinex/"
usno.refdelay = 0.0
usno.receiver = "usn6"
usno.rinex_filename = usno.rinex2

# NIST
nist = Station()
nist.name = "NIST"
nist.utctag = "nist"
nist.ftp_server = bipm_server
nist.ftp_username = bipm_username
nist.ftp_password = bipm_password
nist.ftp_dir = "/data/UTC/NIST/links/rinex/"
# Note on NIST reference delay ftp://5.144.141.242/data/UTC/NIST/links/cggtts/GMNI0056.735
nist.refdelay = 120.0-7.043
nist.receiver = "NIST"
nist.rinex_filename = nist.rinex1




# OP
op = Station()
op.name = "OP"
op.utctag = "op"
op.ftp_server = bipm_server
op.ftp_username = bipm_username
op.ftp_password = bipm_password
op.ftp_dir = "data/UTC/OP/links/rinex/opmt/"
op.refdelay = 349.0  # refdelay is empirically found mean of CirT error vs. usn3
op.receiver = "opmt"
op.rinex_filename = op.rinex3


# SP
sp = Station()
sp.name = "SP"
sp.utctag = "sp"
sp.ftp_server = bipm_server
sp.ftp_username = bipm_username
sp.ftp_password = bipm_password
sp.ftp_dir = "data/UTC/SP/links/rinex/"
sp.refdelay = 221.5-2.279
# ftp://5.144.141.242/data/UTC/SP/links/cggtts/gzSP0156.752
# ftp://5.144.141.242/data/UTC/SP/links/cggtts/rzSP0256.751
sp.receiver = "sp01"
sp.rinex_filename = sp.rinex3


# NICT
nict = Station()
nict.name = "NICT"
nict.utctag = "nict"
nict.ftp_server = bipm_server
nict.ftp_username = bipm_username
nict.ftp_password = bipm_password
nict.ftp_dir = "data/UTC/NICT/links/rinex/"
nict.refdelay = 17.628
nict.receiver = "nc02"
nict.rinex_filename = nict.rinex2


# NPL
npl = Station()
npl.name = "NPL"
npl.utctag = "npl"
npl.ftp_server = bipm_server
npl.ftp_username = bipm_username
npl.ftp_password = bipm_password
npl.ftp_dir = "data/UTC/NPL/links/rinex/"
npl.refdelay = -2.797
npl.receiver = "NP11"
npl.rinex_filename = npl.rinex1
"""


########################################################################

if __name__ == "__main__":
    
    # results:
    # clk = clk - my_station.cab_dly - my_station.int_dly_p3() + my_station.ref_dly
    mi05d = -mi05.cab_dly + mi05.ref_dly - mi05.int_dly_p3()
    mi06d = -mi06local.cab_dly + mi06local.ref_dly - mi06local.int_dly_p3()
    print("mi05 corr: ",-mi05.cab_dly + mi05.ref_dly - mi05.int_dly_p3())
    print("mi06local corr: ",-mi06local.cab_dly + mi06local.ref_dly - mi06local.int_dly_p3())
    print(mi05d, mi06d, mi05d-mi06d)
    #print("mi05 cab ",mi05.cab_dly)
    
    # an example of how to retrieve a RINEX file
    #dt = datetime.datetime.utcnow() - datetime.timedelta(days=5)  # some days back from now
    #print(mi05.get_rinex(dt))
    #print(mi04.get_multiday_rinex(dt, 2))
    
    #print(mi05.get_multiday_rinex(dt, num_days = 8))
    
    """
    print(usno.get_rinex(dt))
    print(nist.get_rinex(dt))
    print(mikes.get_rinex(dt))
    print(op.get_rinex(dt))
    print(sp.get_rinex(dt))
    print(nict.get_rinex(dt))
    print(npl.get_rinex(dt))
    print(ptb.get_rinex(dt))
    """
