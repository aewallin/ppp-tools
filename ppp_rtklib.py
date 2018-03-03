import os
import datetime
import shutil
import subprocess
import numpy

import UTCStation
import ftp_tools
import bipm_ftp
import igs_ftp
import ppp_common

rtklib_tag = "rtklib" # used in the results-file filename
rtklib_binary = "rnx2rtkp" # must have this executable in path

def parse_result(fname, station):
    """
        parse the RTKLib output
        to a format defined by PPP_Result
    """
    ppp_result = ppp_common.PPP_Result()
    ppp_result.station=station
    with open(fname) as f:
        for line in f:
            if line.startswith("%"):
                pass # comments
            else:
                fields = line.split()
                #print fields
                ymd = fields[0]
                ymd = ymd.split("/")
                
                year = int(ymd[0])
                month = int(ymd[1])
                day = int(ymd[2])
                
                
                hms = fields[1]
                hms = hms.split(":")
                hour = int(hms[0])
                minute = int(hms[1])
                second = int( numpy.round( float(hms[2]) ) )
                
                clk = (second - float(hms[2]))*1.0e9
                #print year, month, day, hour, minute, second, clk
                
                #secs = float(ymd[2])
                
                dt = datetime.datetime(year, month, day, hour, minute, 0) + datetime.timedelta(seconds=second)
                #print dt
                (lat, lon, height ) = float(fields[2]), float(fields[3]), float(fields[4])
                #ppp_common.xyz2lla( x, y, z )
                #clk = float(fields[7]) * (1.0e9 / 299792458.0)   # Receiver clock [ns]
                ztd = 0 #??
                float(fields[8]) # Zenith Tropospheric Delay [m]
                p = ppp_common.PPP_Point( dt, lat, lon, height, clk, ztd )
                ppp_result.append(p)
    """
    if backward: # we retain data from the FILTER run backwards
        maxepoch=datetime.datetime(1900,1,1)
        bwd_obs = []
        #found = False
        for p in ppp_result.observations:
            if p.epoch > maxepoch:
                maxepoch = p.epoch
                maxpt = p
            else: # we are now in the backwards data
                #if not found:
                #    print "max epoch ", maxepoch
                #    bwd_obs.append(maxpt)
                #    found = True
                bwd_obs.append(p)
        bwd_obs.reverse() # back to chronological order
        ppp_result.observations = bwd_obs 
    """
    print len(ppp_result)
    return ppp_result

"""
def glab_result_write(outfile, data, preamble=""):
    
        write gLAB output results to a neatly formatted file
    
    with open(outfile,'wb') as f:
        for line in preamble.split('\n'):
            f.write( "# %s\n" % line)
        f.write( "# year doy secs x y z t ztd ambig.\n")
        for row in data:
            f.write( "%04d %03d %05.03f %f %f %f %f %f %f \n" % (row[0], row[1], row[2], row[3], row[4],  row[5], row[6], row[7], row[8] ) )
    print "gLAB parsed output: ", outfile
"""


def rtklib_run(station, dt, rapid=True, prefixdir=""):
    """
    PPP run using RTKLib rnx2rtkp
    
    """
    dt_start = datetime.datetime.utcnow()

    doy = dt.timetuple().tm_yday
    rinex = station.get_rinex( dt ) # doenload rinex file
    
    # GET NAV file
    navfile = igs_ftp.cddis_brdc_file(dt, prefixdir)
    
    # download IGS products 
    (clk, eph, erp) = igs_ftp.get_CODE_rapid(dt, prefixdir)

    # log input files, for writing to the result file
    run_log  = " run start: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute, dt_start.second)
    run_log += "   Station: %s\n" % station.name
    run_log += "      Year: %d\n" % dt.year
    run_log += "       DOY: %03d\n" % doy
    run_log += "      date:  %d-%02d-%02d\n" % (dt.year, dt.month, dt.day)
    run_log += "     RINEX: %s\n" % rinex
    run_log += "       CLK: %s\n" % clk
    run_log += "       EPH: %s\n" % eph
    run_log += "       ERP: %s\n" % erp
    print run_log

    # we do processing in a temp directory
    tempdir = prefixdir + "/temp/"
    ftp_tools.check_dir( tempdir )
    ftp_tools.delete_files(tempdir) # empty the temp directory

    # copy files to tempdir
    
    files_to_copy = [ rinex, clk, eph, eph, erp, navfile ]
    copied_files = []
    for f in files_to_copy:
        shutil.copy2( f, tempdir )
        (tmp,fn ) = os.path.split(f)
        copied_files.append( tempdir + fn )

    # unzip zipped files, if needed
    for f in copied_files:
        if f[-1] == "Z" or f[-1] == "z": # compressed .z or .Z file
            cmd ='/bin/gunzip'
            cmd = cmd + " -f " + f # -f overwrites existing file
            print "unzipping: ", cmd
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()

    # Hatanaka uncompress - if needed
    #rinexfile = copied_files[0] # the first file is the unzipped RINEX, in the temp dir
    if rinex[-3] == "d" or rinex[-3] == "D":
        hata_file = copied_files[0]
        hata_file = hata_file[:-2] # strip off ".Z"
        #print "hata ", hata_file
        cmd = "CRX2RNX " + hata_file
        print "Hatanaka uncompress: ", cmd
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    

    # figure out the rinex file name
    (tmp,rinexfile ) = os.path.split(rinex)
    inputfile = rinexfile[:-2] # strip off ".Z"
    if inputfile[-1] == "d" or rinex[-3] == "D":
        # if hatanaka compressed, we already uncompressed, so change to "O"
        inputfile = inputfile[:-1]+"O"
        
    # now ppp itself:
    os.chdir( tempdir )

    antfile = prefixdir + "/common/igs08.atx"
    outfile = tempdir + "out.txt"
    
    clk = copied_files[1]
    # RKLib wants eph files to be named sp3
    # from CODE they end .CLK_R
    clk_new = clk[:-6]+".clk"
    cmd = "cp "+clk + " " + clk_new
    #print cmd
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()
    clk = clk_new
    print clk
    # RKLib wants eph files to be named sp3
    # from CODE they end .CLK_R
    eph = copied_files[2]
    eph_new = eph[:-6]+".sp3"
    cmd = "cp "+eph + " " + eph_new
    #print cmd
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()
    eph = eph_new
    print eph
    
    navfile = copied_files[5]
    navfile = navfile[:-2] # strip off ".Z"
    
    inputfile = tempdir+inputfile
    print "input ", inputfile
    print "nav ", navfile
    print "clk ", clk
    print "eph ", eph
    cmd =  rtklib_binary # must have this executable in path
    
    conf_file = prefixdir + "/common/rtklib_opts1.conf"
    options = [ " -k %s"%conf_file,
                #" -p 7",               # mode 7:ppp-static
                #" -t", # lat/lon/height time output
                #" -u", # UTC time Don't use it, we get epochs of min:11 and min:41 instead of min:00 and min:00
                #" -d %d" % 12, # number of decimals in time output
                " -o %s" % outfile,
                #" -m 10",                       # elevation mask
                #" -c", # combined forward/backward solutions
                #" -y 1", # state output
                #" -h", # fix and hold for integer ambiguity resolution [off]
                #" -f 2", # 2:L1+L2
                #" -x 2", # debug level
                " %s" % inputfile, # RINEX file
                " %s" % navfile,   # brdc NAV file
                " %s" % clk,
                " %s" % eph,
                " %s" % (prefixdir + "/common/igs08.atx")
                ]

    for opt in options:
        cmd += opt
    p = subprocess.Popen(cmd, shell=True, cwd = tempdir )
    p.communicate() # wait for processing to finish

    dt_end = datetime.datetime.utcnow()
    delta = dt_end-dt_start
    run_log2  = "   run end: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_end.year, dt_end.month, dt_end.day, dt_end.hour, dt_end.minute, dt_end.second)
    run_log2 += "   elapsed: %.2f s\n" % (delta.seconds+delta.microseconds/1.0e6)
    print run_log2

    # here we may parse the output and store it to file somewhere
    ppp_result = parse_result(outfile, station)
    ppp_common.write_result_file( ppp_result=ppp_result, preamble=run_log+run_log2, rapid=rapid, tag=rtklib_tag, prefixdir=prefixdir )

if __name__ == "__main__":

    # example processing:
    station1 = UTCStation.ptb
    #station2 = UTCStation.ptb
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=4)
    current_dir = os.getcwd()

    # run gLAB PPP for given station, day
    rtklib_run(station1, dt, prefixdir=current_dir)
    #glab_run(station2, dt, prefixdir=current_dir)
