"""
    Library for downloading GPS products (orbits & clocks) from
    an IGS datacenter.
    
    Anders Wallin, 2013-2015
"""
import ftplib
import datetime
import sys
import os 

import gpstime

# Examples of Rapid files:
# ftp://ftp.unibe.ch/aiub/CODE/COD17840.EPH_R    ephemeris aka orbits
# ftp://ftp.unibe.ch/aiub/CODE/COD17840.ERP_R    erp, earth rotation parameters
# ftp://ftp.unibe.ch/aiub/CODE/COD17840.CLK_R    clk, clocks

def check_dir(target_dir):
    # check that directory exsits, create if not
    if not os.path.isdir(target_dir):
        print "creating target directory ", target_dir
        os.mkdir(target_dir)

# retrieve rapid CODE products
def CODE_rapid_files(dt, prefixdir=""):
    server = "ftp.unibe.ch"
    directory = "aiub/CODE/"
    week = gpstime.gpsWeek( dt.year, dt.month, dt.day )
    dow  =  gpstime.dayOfWeek( dt.year, dt.month, dt.day )
    clk = "COD%s%s.CLK_R" % ( week,  dow )
    sp3 = "COD%s%s.EPH_R" % ( week, dow )
    erp = "COD%s%s.ERP_R" % ( week, dow )
    print "CODE rapid products for ", dt.year ,"-", dt.month, "-",dt.day
    print "CLK = ", clk
    print "SP3 = ", sp3
    print "ERP = ", erp
    
    check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/CODE_rapid/"
    print "local dir = ", localdir
    
    #return  CODE_download(server, directory, [clk, sp3, erp], localdir)
    return  (server, directory, [clk, sp3, erp], localdir)
    
# retrieve final CODE products
def CODE_final_files(dt, prefixdir=""):
    #(server, directory, clk, sp3, erp) = CODE_final_files( year, doy )
    server = "ftp.unibe.ch"
    directory = "aiub/CODE/%s/" % (dt.year)
    #dt = gpstime.dateFromJulian( dt.year, dt.doy )
    week = gpstime.gpsWeek( dt.year, dt.month, dt.day )
    dow  =  gpstime.dayOfWeek( dt.year, dt.month, dt.day )
    clk = "COD%s%s.CLK.Z" % ( week,  dow ) # clock
    sp3 = "COD%s%s.EPH.Z" % ( week, dow )  # orbit
    erp = "COD%s%s.ERP.Z" % ( week, dow )  # earth
    print "CODE final products for ", dt.year ,"-", dt.month, "-",dt.day
    print "CLK = ", clk
    print "SP3 = ", sp3
    print "ERP = ", erp
    
    check_dir(prefixdir + "/products/")
    localdir = prefixdir + "/products/CODE_final/"
    print "local dir = ", localdir
    return  (server, directory, [clk, sp3, erp], localdir)

def CODE_download( server, directory, files, localdir):
    print "CODE_download start ", datetime.datetime.now()
    check_dir(localdir)

    for f in files:
        local_file = localdir+f
        if not os.path.exists( local_file ):
            # Connection information
            server = server
            username = ''
            password = ''
            print 'Remote ', f
            print 'Local ', local_file
            sys.stdout.flush()
             
            # Establish the connection
            ftp = ftplib.FTP(server)
            ftp.login(username, password)
             
            # Change to the proper directory
            ftp.cwd(directory)
             
            # Loop through matching files and download each one individually
            fhandle = open(local_file, 'wb')
            ftp.retrbinary('RETR ' + f, fhandle.write)
            fhandle.close()
            ftp.close()
        else: # don't download if file already exists on disk
            print f," already exists. not downloading."
    print "CODE_download Done ", datetime.datetime.now()
    sys.stdout.flush()
    output=[]
    for f in files:
        output.append( localdir+f)
    return output # returns list of files: [CLK, EPH, ERP]

if __name__ == "__main__":
    current_dir = os.getcwd()
    # example of how to use the functions:
    dt_rapid = datetime.datetime.now() - datetime.timedelta(days=3) # rapid products avaible with 2(?) days latency
    dt_final = datetime.datetime.now() - datetime.timedelta(days=14) # final product worst case latency 14 days ?
    (server, directory, files, localdir) = CODE_final_files(dt_final, prefixdir=current_dir)
    files = CODE_download(server, directory, files, localdir)
    print files # [CLK, EPH, ERP]  note that final products are zipped
    (server, directory, files, localdir) = CODE_rapid_files(dt_rapid, prefixdir=current_dir)
    files = CODE_download(server, directory, files, localdir)
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
