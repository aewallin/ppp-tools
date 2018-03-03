"""
    This file is part of ppp-tools, https://github.com/aewallin/ppp-tools
    GPLv2 license.
    
    Library for downloading GPS products (orbits & clocks) from
    an IGS datacenter.
    
    Anders Wallin, 2013-2015
"""
import ftplib
import datetime
import sys
import os 

import ftp_tools
import gpstime

# ftp://cddis.gsfc.nasa.gov/gnss/data/daily/
# YYYY/DDD/YYn/brdcDDD0.YYn.Z   (merged GPS broadcast ephemeris file)
def cddis_brdc_file(dt, prefixdir=""):
  server =   "cddis.gsfc.nasa.gov"
  remotedir = "gnss/data/daily/%d/brdc" % dt.year
  doy = dt.timetuple().tm_yday
  f = "brdc%03d0.%dn.Z" % (doy, dt.year-2000)
  #YYYY/brdc/brdcDDD0.YYn.Z
  localdir = prefixdir + "/stations/brdc/"
  ftp_tools.check_dir(localdir)
  
  ftp_tools.ftp_download( server, username="anonymous", password="", remotedir=remotedir, remotefile=f, localdir=localdir)
  return localdir+f

def get_CODE_final(dt, prefixdir=""):
    (server, username, password, directory, files, localdir) = CODE_final_files(dt, prefixdir)
    (clk1, eph1, erp1) =  CODE_download(server, username, password, directory, files, localdir)
    return (clk1, eph1, erp1)

def get_CODE_rapid(dt, prefixdir=""):
    (server, username, password, directory, files, localdir) = CODE_rapid_files(dt, prefixdir)
    (clk1, eph1, erp1) =  CODE_download(server, username, password, directory, files, localdir)
    return (clk1, eph1, erp1)

def CODE_rapid_files(dt, prefixdir=""):
    """
        retrieve rapid CODE products for the datetime dt
        
        Examples of Rapid files: (FIXME: old paths!)
        ftp://ftp.unibe.ch/aiub/CODE/COD17840.EPH_R    ephemeris aka orbits
        ftp://ftp.unibe.ch/aiub/CODE/COD17840.ERP_R    erp, earth rotation parameters
        ftp://ftp.unibe.ch/aiub/CODE/COD17840.CLK_R    clk, clocks

    """
    server = "ftp.aiub.unibe.ch"
    remotedir = "CODE/"
    week = gpstime.gpsWeek( dt.year, dt.month, dt.day )
    dow  =  gpstime.dayOfWeek( dt.year, dt.month, dt.day )
    clk = "COD%s%s.CLK_R" % ( week,  dow )
    sp3 = "COD%s%s.EPH_R" % ( week, dow )
    erp = "COD%s%s.ERP_R" % ( week, dow )
    print "CODE rapid products for %d-%02d-%0d" %( dt.year , dt.month, dt.day )
    print "CLK = ", clk
    print "SP3 = ", sp3
    print "ERP = ", erp
    
    ftp_tools.check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/CODE_rapid/"
    print "local dir = ", localdir
    
    #return  CODE_download(server, directory, [clk, sp3, erp], localdir)
    return  (server, "", "", remotedir, [clk, sp3, erp], localdir)
    
# retrieve final CODE products
def CODE_final_files(dt, prefixdir=""):
    server = "ftp.aiub.unibe.ch"
    remotedir = "CODE/%s/" % (dt.year)
    week = gpstime.gpsWeek(   dt.year, dt.month, dt.day )
    dow  = gpstime.dayOfWeek( dt.year, dt.month, dt.day )
    clk = "COD%s%s.CLK.Z" % ( week, dow ) # clock
    sp3 = "COD%s%s.EPH.Z" % ( week, dow ) # orbit
    erp = "COD%s%s.ERP.Z" % ( week, dow ) # earth
    print "CODE final products for %d-%02d-%0d" %( dt.year , dt.month, dt.day )
    print "CLK = ", clk
    print "SP3 = ", sp3
    print "ERP = ", erp
    
    ftp_tools.check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/CODE_final/"
    print "local dir = ", localdir
    return  (server, "", "", remotedir, [clk, sp3, erp], localdir)

def CODE_download( server, username, password, remotedir, files, localdir):
    print "CODE_download start ", datetime.datetime.now()
    ftp_tools.check_dir(localdir)

    for f in files:
        local_file = localdir+f
        ftp_tools.ftp_download( server, username, password, remotedir, f, localdir)
    print "CODE_download Done ", datetime.datetime.now()
    sys.stdout.flush()
    output=[]
    for f in files:
        output.append( localdir+f)
    return output # returns list of files: [CLK, EPH, ERP]

def example_igs_ftp():
    current_dir = os.getcwd()
    # example of how to use the functions:
    dt_rapid = datetime.datetime.now() - datetime.timedelta(days=3) # rapid products avaible with 2(?) days latency
    dt_final = datetime.datetime.now() - datetime.timedelta(days=14) # final product worst case latency 14 days ?
    (server, username, password, directory, files, localdir) = CODE_final_files(dt_final, prefixdir=current_dir)
    files = CODE_download(server, username, password, directory, files, localdir)
    print files # [CLK, EPH, ERP]  note that final products are zipped
    (server, username, password, directory, files, localdir) = CODE_rapid_files(dt_rapid, prefixdir=current_dir)
    files = CODE_download(server, username, password, directory, files, localdir)
    print files # [CLK, EPH, ERP] rapid products are unzipped
    """
    sample output:
    
    CODE final products for  2015 - 5 - 25
    CLK =  COD18461.CLK.Z
    SP3 =  COD18461.EPH.Z
    ERP =  COD18461.ERP.Z
    local dir =  /home/anders/ppp-tools/CODE_final/
    CODE rapid products for  2015 - 5 - 25
    CLK =  COD18461.CLK_R
    SP3 =  COD18461.EPH_R
    ERP =  COD18461.ERP_R
    local dir =  /home/anders/ppp-tools/CODE_rapid/

    """
    
if __name__ == "__main__":
    example_igs_ftp()
        

