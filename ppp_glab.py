import os
import datetime
import shutil
import subprocess

import UTCStation
import ftp_tools
import bipm_ftp
import igs_ftp
import ppp_common

glab_tag = "glab"
glab_binary = "gLAB_linux" # must have this executable in path

def glab_parse_result(fname, station):
    """
        parse the FILTER data fields from gLAB outuput
    """
    ppp_result = ppp_common.PPP_Result()
    ppp_result.station=station
    with open(fname) as f:
        for line in f:
            if line.startswith("FILTER"):
                fields = line.split()
                assert( fields[0] == "FILTER" )
                year = int(fields[1])
                doy = int(fields[2])
                secs = float(fields[3]) # seconds from start of day. GPS or UTC time??
                dt = datetime.datetime(year,1,1) + datetime.timedelta( days = doy-1, seconds=secs )
                x = float(fields[4])
                y = float(fields[5])
                z = float(fields[6])
                (lat, lon, height ) = ppp_common.xyz2lla( x, y, z )
                clk = float(fields[7]) * (1.0e9 / 299792458.0)   # Receiver clock [ns]
                ztd = float(fields[8]) # Zenith Tropospheric Delay [m]
                p = ppp_common.PPP_Point( dt, lat, lon, height, clk, ztd )
                ppp_result.append(p)
    return ppp_result

def glab_result_write(outfile, data, preamble=""):
    """
        write gLAB output results to a neatly formatted file
    """
    with open(outfile,'wb') as f:
        for line in preamble.split('\n'):
            f.write( "# %s\n" % line)
        f.write( "# year doy secs x y z t ztd ambig.\n")
        for row in data:
            f.write( "%04d %03d %05.03f %f %f %f %f %f %f \n" % (row[0], row[1], row[2], row[3], row[4],  row[5], row[6], row[7], row[8] ) )
    print "gLAB parsed output: ", outfile

def glab_run(station, dt, rapid=True, prefixdir=""):
    dt_start = datetime.datetime.utcnow()

    doy = dt.timetuple().tm_yday
    rinex = station.get_rinex( dt )

    (clk, eph, erp) = igs_ftp.get_CODE_rapid(dt, prefixdir)

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
    files_to_copy = [ rinex, clk, eph, eph, erp ]
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

    # TODO: if the RINEX file is hatanaka-compressed, uncompress it
    # this requires the CRX2RNX binary
    """
    if rinexfile[-3] == "d" or rinexfile[-3] == "D":
        hata_file = moved_files[0]
        cmd = "CRX2RNX " + hata_file[:-2]
        print "Hatanaka uncompress: ", cmd
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    """

    # figure out the rinex file name
    (tmp,rinexfile ) = os.path.split(rinex)
    inputfile = rinexfile[:-2] # strip off ".Z"

    # now ppp itself:
    os.chdir( tempdir )

    antfile = prefixdir + "/common/igs08.atx"
    outfile = tempdir + "out.txt"
    
    cmd =  glab_binary # must have this executable in path
    # see doc/glab_options.txt
    options = [ " -input:obs %s" % inputfile,
                " -input:clk %s" % clk,
                " -input:orb %s" % eph,
                " -input:ant %s" % antfile,
                " -model:recphasecenter no", # USNO receiver antenna is not in igs08.atx (?should it be?)
                " -output:file %s" % outfile,
                " -pre:dec 30", # rinex data is at 30s intervals, don't decimate
                " -pre:elevation 10", # elevation mask
                " --print:input", # discard unnecessary output
                " --print:model",
                " --print:prefit",
                " --print:postfit",
                " --print:satellites" ]

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
    ppp_result = glab_parse_result(outfile, station)
    ppp_common.write_result_file( ppp_result=ppp_result, preamble=run_log+run_log2, rapid=rapid, tag=glab_tag, prefixdir=prefixdir )

if __name__ == "__main__":

    # example processing:
    station = UTCStation.usno
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=4)
    current_dir = os.getcwd()

    # run gLAB PPP for given station, day
    glab_run(station, dt, prefixdir=current_dir)
