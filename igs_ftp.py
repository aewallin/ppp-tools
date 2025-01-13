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
    """
        This was used previously for rtklib runs.
        
        Could be replaced with a nav-file from the station?
    """
    server = "cddis.gsfc.nasa.gov"
    remotedir = "gnss/data/daily/%d/brdc" % dt.year
    doy = dt.timetuple().tm_yday
    f = "brdc%03d0.%dn.Z" % (doy, dt.year-2000)
    # YYYY/brdc/brdcDDD0.YYn.Z
    localdir = prefixdir + "/stations/brdc/"
    ftp_tools.check_dir(localdir)

    ftp_tools.ftp_download(server, username="anonymous", password="",
                           remotedir=remotedir, remotefile=f, localdir=localdir)
    return localdir+f

def get_IGS_rapid(dt, prefixdir=""):
    (server, username, password, directory, files,
     localdir) = IGS_rapid_files(dt, prefixdir)
    (clk1, eph1, erp1) = download(
        server, username, password, directory, files, localdir)
    return (clk1, eph1, erp1)
    
def get_IGS_final(dt, prefixdir=""):
    (server, username, password, directory, files,
     localdir) = IGS_final_files(dt, prefixdir)
    (clk1, eph1, erp1) = download(
        server, username, password, directory, files, localdir)
    return (clk1, eph1, erp1)

def get_CODE_final(dt, prefixdir=""):
    (server, username, password, directory, files,
     localdir) = CODE_final_files(dt, prefixdir)
    (clk1, eph1, erp1) = download(
        server, username, password, directory, files, localdir)
    return (clk1, eph1, erp1)


def get_CODE_rapid(dt, prefixdir=""):
    (server, username, password, directory, files,
     localdir) = CODE_rapid_files(dt, prefixdir)
    (clk1, eph1, erp1) = download(
        server, username, password, directory, files, localdir)
    return (clk1, eph1, erp1)


def CODE_rapid_files(dt, prefixdir=""):
    """
        retrieve rapid CODE products for the datetime dt
        
        Products are stored in <prefixdir>/products/CODE_rapid/

        Examples of Rapid files: (FIXME: old paths!)
        ftp://ftp.unibe.ch/aiub/CODE/COD17840.EPH_R    ephemeris aka orbits
        ftp://ftp.unibe.ch/aiub/CODE/COD17840.ERP_R    erp, earth rotation parameters
        ftp://ftp.unibe.ch/aiub/CODE/COD17840.CLK_R    clk, clocks

        updated working link (as of 2021 July)
        ftp://ftp.aiub.unibe.ch/CODE/
    """
    server = "ftp.aiub.unibe.ch"
    remotedir = "CODE/"
    week = gpstime.gpsWeek(dt.year, dt.month, dt.day)
    dow = gpstime.dayOfWeek(dt.year, dt.month, dt.day)
    clk = "COD%s%s.CLK_R" % (week,  dow)
    sp3 = "COD%s%s.EPH_R" % (week, dow)
    erp = "COD%s%s.ERP_R" % (week, dow)
    print("CODE rapid products for %d-%02d-%0d" % (dt.year, dt.month, dt.day))
    print("CLK = ", clk)
    print("SP3 = ", sp3)
    print("ERP = ", erp)

    ftp_tools.check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/CODE_rapid/"
    print("local dir = ", localdir)

    # return  CODE_download(server, directory, [clk, sp3, erp], localdir)
    return (server, "", "", remotedir, [clk, sp3, erp], localdir)


def CODE_final_files_old(dt, prefixdir=""):
    """
        retrieve final CODE products for the datetime dt
        
        files are in:
        ftp://ftp.aiub.unibe.ch/CODE/2021/
        
    """
    server = "ftp.aiub.unibe.ch"
    remotedir = "CODE/%s/" % (dt.year)
    week = gpstime.gpsWeek(dt.year, dt.month, dt.day)
    dow = gpstime.dayOfWeek(dt.year, dt.month, dt.day)
    clk = "COD%s%s.CLK.Z" % (week, dow)  # clock
    sp3 = "COD%s%s.EPH.Z" % (week, dow)  # orbit
    erp = "COD%s%s.ERP.Z" % (week, dow)  # earth
    print("CODE final products for %d-%02d-%0d" % (dt.year, dt.month, dt.day))
    print("CLK = ", clk)
    print("SP3 = ", sp3)
    print("ERP = ", erp)

    ftp_tools.check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/CODE_final/"
    print("local dir = ", localdir)
    return (server, "", "", remotedir, [clk, sp3, erp], localdir)

def CODE_final_files(dt, prefixdir=""):
    """
        retrieve final CODE products for the datetime dt
        
        files are in:
        ftp://ftp.aiub.unibe.ch/CODE/2021/
        
        new format, update code 2024-06
        COD0OPSFIN_20241510000_01D_30S_CLK.CLK.gz   new v3 format? not supported by gpsppp
        COD0OPSFIN_20241390000_01D_30S_CLK.CLK_V2.gz
        COD0OPSFIN_20241510000_01D_01D_ERP.ERP.gz
        COD0OPSFIN_20241510000_01D_05M_ORB.SP3.gz 
    """
    server = "ftp.aiub.unibe.ch"
    remotedir = "CODE/%s/" % (dt.year)
    week = gpstime.gpsWeek(dt.year, dt.month, dt.day)
    dow = gpstime.dayOfWeek(dt.year, dt.month, dt.day)
    doy = dt.timetuple().tm_yday
    clk = "COD0OPSFIN_%d%03d0000_01D_30S_CLK.CLK_V2.gz" % (dt.year, doy)  # clock
    sp3 = "COD0OPSFIN_%d%03d0000_01D_05M_ORB.SP3.gz" % (dt.year, doy)  # orbit
    erp = "COD0OPSFIN_%d%03d0000_01D_01D_ERP.ERP.gz" % (dt.year, doy)  # earth
    print("CODE final products for %d-%02d-%0d" % (dt.year, dt.month, dt.day))
    print("CLK = ", clk)
    print("SP3 = ", sp3)
    print("ERP = ", erp)

    ftp_tools.check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/CODE_final/"
    print("local dir = ", localdir)
    return (server, "", "", remotedir, [clk, sp3, erp], localdir)
    
def IGS_rapid_files(dt, prefixdir=""):
    """
        retrieve rapid IGS products for the datetime dt
        
        files are in:
        ftp://gssc.esa.int/gnss/products/<gpsWeek>/
        
        WWWW/igrWWWWD.sp3.Z     Satellite orbit solution
        WWWW/igrWWWWD.erp.Z     Earth orientation parameter solution
        WWWW/igrWWWWd.clk_30.Z  Satellite and station clock solution (30 second)
    """
    week = gpstime.gpsWeek(dt.year, dt.month, dt.day)
    dow = gpstime.dayOfWeek(dt.year, dt.month, dt.day)
    
    #server = "gssc.esa.int"
    #remotedir = "gnss/products/%d/" % (week)

    server = "igs.ensg.ign.fr"
    remotedir = "pub/igs/products/%d/" % (week)

    
    #clk = "igs%s%s.clk_30s.Z" % (week, dow)  # clock, 30s interval
    #clk = "igs%s%s.clk.Z" % (week, dow)  # clock, (5 minute interval?)
    
    #server = "gssc.esa.int"
    #week = gpstime.gpsWeek(dt.year, dt.month, dt.day)
    #dow = gpstime.dayOfWeek(dt.year, dt.month, dt.day)
    
    #remotedir = "gnss/products/%d/" % (week)

    clk = "igr%s%s.clk.Z" % (week, dow)  # clock
    sp3 = "igr%s%s.sp3.Z" % (week, dow)  # orbit
    erp = "igr%s%s.erp.Z" % (week, dow)  # earth rotation parameters, 7 = weeklys
    print("IGS rapid products for %d-%02d-%0d" % (dt.year, dt.month, dt.day))
    print("CLK = ", clk)
    print("SP3 = ", sp3)
    print("ERP = ", erp)

    ftp_tools.check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/IGS_rapid/"
    print("local dir = ", localdir)
    return (server, "", "", remotedir, [clk, sp3, erp], localdir)

def IGS_final_files(dt, prefixdir=""):
    """
        retrieve final IGS products for the datetime dt
        
        files are in:
        ftp://gssc.esa.int/gnss/products/<gpsWeek>/
        ftp://igs.ensg.ign.fr/pub/igs/products/2160/
        
        
        WWWW/igsWWWWD.sp3.Z     Satellite orbit solution
        WWWW/igsWWWWD.erp.Z     Earth orientation parameter solution
        WWWW/igsWWWWd.clk_30.Z  Satellite and station clock solution (30 second)
    """
    week = gpstime.gpsWeek(dt.year, dt.month, dt.day)
    dow = gpstime.dayOfWeek(dt.year, dt.month, dt.day)
    
    #server = "gssc.esa.int"
    #remotedir = "gnss/products/%d/" % (week)

    server = "igs.ensg.ign.fr"
    remotedir = "pub/igs/products/%d/" % (week)

    
    clk = "igs%s%s.clk_30s.Z" % (week, dow)  # clock, 30s interval
    #clk = "igs%s%s.clk.Z" % (week, dow)  # clock, (5 minute interval?)
    sp3 = "igs%s%s.sp3.Z" % (week, dow)  # orbit
    erp = "igs%s%s.erp.Z" % (week, 7)  # earth rotation parameters, 7 = weeklys
    print("IGS final products for %d-%02d-%0d" % (dt.year, dt.month, dt.day))
    print("CLK = ", clk)
    print("SP3 = ", sp3)
    print("ERP = ", erp)

    ftp_tools.check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/IGS_final/"
    print("local dir = ", localdir)
    return (server, "", "", remotedir, [clk, sp3, erp], localdir)
        

def download(server, username, password, remotedir, files, localdir):
    """
        Download a list of files from given ftp server
        
        Return list of local downloaded files
    """
    print("download start ", datetime.datetime.now())
    ftp_tools.check_dir(localdir)

    for f in files:
        local_file = localdir+f
        ftp_tools.ftp_download(
            server, username, password, remotedir, f, localdir)
    print("download Done ", datetime.datetime.now())
    sys.stdout.flush()
    output = []
    for f in files:
        output.append(localdir+f)
    return output  # returns list of local files: [CLK, EPH, ERP]


def example_igs_ftp():
    current_dir = os.getcwd()
    # example of how to use the functions:
    # rapid products avaible with 2(?) days latency
    dt_rapid = datetime.datetime.now() - datetime.timedelta(days=3)
    # final product worst case latency 14 days ?
    dt_final = datetime.datetime.now() - datetime.timedelta(days=15)
    (server, username, password, directory, files,
     localdir) = CODE_final_files(dt_final, prefixdir=current_dir)
    files = download(server, username, password,
                          directory, files, localdir)
    print(files)  # [CLK, EPH, ERP]  note that final products are zipped
    (server, username, password, directory, files,
     localdir) = CODE_rapid_files(dt_rapid, prefixdir=current_dir)
    files = download(server, username, password,
                          directory, files, localdir)
    print(files)  # [CLK, EPH, ERP] rapid products are unzipped
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
