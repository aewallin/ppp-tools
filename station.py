"""
    This file is part of ppp-tools, https://github.com/aewallin/ppp-tools
    GPLv2 license.
"""
import os
import datetime

import bipm_ftp
import ftp_tools


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
        self.refdelay = 0.0     # reference delay, in nanoseconds
        self.receiver = ""        # receiver name, e.g. "MI02", used in the RINEX filename
        self.rinex_filename = self.rinex1
        self.hatanaka = False   # flag is True for Hatanaka compressed RINEX
        self.antex = True       # receiver antenna in ANTEX file?

        self.ref_dly = 0.0
        self.cab_dly = 0.0
        
    def int_dly_p3(self):
        """
            ionosphere-free P3 internal delay.
            linear combination of calibrated P1 and P3 delays
        """
        try:
            return 2.5457*self.int_dly_p1 - 1.5457*self.int_dly_p2
        except:
            return 0.0
        
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

    def antex(self):
        return self.antex

    def get_rinex(self, dt):
        """
            Retrieve RINEX file using ftp
        """
        current_dir = os.getcwd()
        localdir = current_dir + '/stations/' + self.name + '/'
        ftp_tools.check_dir(localdir)  # create directory if it doesn't exist
        return ftp_tools.ftp_download(self.ftp_server, self.ftp_username, self.ftp_password,
                                      self.ftp_dir, self.rinex_filename(dt), localdir)

########################################################################
# example stations
#
# these are from the BIPM ftp-server, but could be from anywhere.
#
########################################################################


#bipm_server = '5.144.141.242'
# NOTE: as of 2021 BIPM does not make public RINEX files anymore!
bipm_server = 'ftp2.bipm.org'
bipm_username = 'labotai'
bipm_password = 'dataTAI'

mikes_server = "monitor.mikes.fi"
mikes_username = "anonymous"
mikes_password = "ppp-tools"

# MI04, VTT MIKES timing receiver
mi04 = Station()
mi04.name = "MI04"
mi04.utctag = "MI04"
mi04.ftp_server = mikes_server
mi04.ftp_username = mikes_username
mi04.ftp_password = mikes_password
mi04.ftp_dir = "/GNSS/MI04/RINEX/"
mi04.receiver = "MI04"  # start of the RINEX filename
mi04.rinex_filename = mi04.rinex4  # naming style is MI040040.21D.Z

# MI05, VTT MIKES timing receiver, RINEX v2 files
#  ftp://monitor.mikes.fi/GNSS/MI05/RINEX_v2_24h/
mi05 = Station()
mi05.name = "MI05"
mi05.utctag = "MI05"
mi05.ftp_server = mikes_server
mi05.ftp_username = mikes_username
mi05.ftp_password = mikes_password
mi05.ftp_dir = "/GNSS/MI05/RINEX_v2_24h/"
mi05.receiver = "MI05"  # start of the RINEX filename
mi05.rinex_filename = mi05.rinex6  # naming style is MI050020.21o.gz
mi05.ref_dly = 5.092 # ns
mi05.cab_dly = 96.2 # ns
mi05.int_dly_p1 = 20.17 # ns, see Cal_ID: 1016-2019
mi05.int_dly_p2 = 18.18 # ns

# MI02, VTT MIKES timing receiver, RINEX v2 files
mi02 = Station()
mi02.name = "MI02"
mi02.utctag = "MI02"
mi02.ftp_server = mikes_server
mi02.ftp_username = mikes_username
mi02.ftp_password = mikes_password
mi02.ftp_dir = "/GNSS/MI02/RINEX/"
mi02.receiver = "MI02"  # start of the RINEX filename
mi02.rinex_filename = mi02.rinex1  # naming style is MI021690.21O.Z


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


# MIKES
mikes = Station()
mikes.name = "MIKES"
mikes.utctag = "mike"
mikes.ftp_server = bipm_server
mikes.ftp_username = bipm_username
mikes.ftp_password = bipm_password
mikes.ftp_dir = "data/UTC/MIKE/links/rinex/"
mikes.refdelay = 2.9
mikes.receiver = "MI04"
mikes.rinex_filename = mikes.rinex4
mikes.antex = False


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


# PTB
ptb = Station()
ptb.name = "PTB"
ptb.utctag = "ptb"
ptb.ftp_server = bipm_server
ptb.ftp_username = bipm_username
ptb.ftp_password = bipm_password
ptb.ftp_dir = "data/UTC/PTB/links/rinex/PTBG/"
ptb.refdelay = 335.6+132.0
ptb.receiver = "PTBG"
ptb.rinex_filename = ptb.rinex5

########################################################################

if __name__ == "__main__":

    # an example of how to retrieve a RINEX file
    dt = datetime.datetime.utcnow() - datetime.timedelta(days=5)  # some days back from now

    print(usno.get_rinex(dt))
    print(nist.get_rinex(dt))
    print(mikes.get_rinex(dt))
    print(op.get_rinex(dt))
    print(sp.get_rinex(dt))
    print(nict.get_rinex(dt))
    print(npl.get_rinex(dt))
    print(ptb.get_rinex(dt))
