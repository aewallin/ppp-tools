import os
import datetime
import shutil
import subprocess

import UTCStation
import ftp_tools
import bipm_ftp
import igs_ftp

def glab_parse(fname):
    """
        parse the FILTER data fields from gLAB outuput
    """
    data=[]
    with open(fname) as f:
        for line in f:
            if line.startswith("FILTER"):
                fields = line.split()
                assert( fields[0] == "FILTER" )
                year = int(fields[1])
                doy = int(fields[2])
                secs = float(fields[3]) # seconds from start of day. GPS or UTC time??
                x = float(fields[4])  
                y = float(fields[5])
                z = float(fields[6])
                t = float(fields[7])   # Receiver clock [m]
                ztd = float(fields[8]) # Zenith Tropospheric Delay [m]
                amb = float(fields[9]) # Carrierphase ambiguities [m]
                row = (year,doy,secs,x,y,z,t,ztd,amb)
                data.append(row)
    return data

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
    
    year = dt.timetuple().tm_year
    doy = dt.timetuple().tm_yday
    rinex = station.get_rinex( dt )
    
    (server, username, password, igs_directory, igs_files, localdir) = igs_ftp.CODE_rapid_files(dt, prefixdir=prefixdir)
    files = igs_ftp.CODE_download(server, username, password, igs_directory, igs_files, localdir)
    (clk, eph, erp) = (files[0], files[1], files[2])

    run_log = ""
    run_log += " run start: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute, dt_start.second)
    run_log += "   Station: %s\n" % station.name
    run_log += "      Year: %d\n" % year
    run_log += "       DOY: %03d\n" % doy
    run_log += "      date:  %d-%02d-%02d\n" % (dt.year, dt.month, dt.day)
    run_log += "     RINEX: %s\n" % rinex
    run_log += "       CLK: %s\n" % clk  # allow for multiple clk-files!?
    run_log += "       EPH: %s\n" % eph
    run_log += "       ERP: %s\n" % erp
    print run_log

    # we do processing in a temp directory
    tempdir = prefixdir + "/temp/"
    ftp_tools.check_dir( tempdir )
    # empty the temp directory
    ftp_tools.delete_files(tempdir)
    
    # move files to tempdir
    files_to_move = [ rinex, clk, eph, eph, erp ]
    moved_files = []
    for f in files_to_move:
        shutil.copy2( f, tempdir )
        (tmp,fn ) = os.path.split(f)
        moved_files.append( tempdir + fn )
    #print moved_files
    
    # unzip zipped files
    for f in moved_files:
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
    glab = "gLAB_linux" # must have this executable in path
    
    antfile = prefixdir + "/common/igs08.atx"
    outfile = tempdir + "out.txt"
    
    cmd = glab  
    # see doc/glab_options.txt
    options = [ " -input:obs %s" % inputfile,
                " -input:clk %s" % clk,
                " -input:orb %s" % eph,
                " -input:ant %s" % antfile,
                " -model:recphasecenter no", # USNO receiver antenna is not in igs08.atx (?should it be?)
                " -output:file %s" % outfile,
                " -pre:dec 30", # rinex data is at 30s intervals, don't decimate
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
    run_log2=""
    run_log2 += "   run end: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_end.year, dt_end.month, dt_end.day, dt_end.hour, dt_end.minute, dt_end.second)
    delta = dt_end-dt_start
    run_log2+=  "   elapsed: %.2f s\n" % (delta.seconds+delta.microseconds/1.0e6)
    print run_log2
    
    # here we may parse the output and store it to file somewhere
    data = glab_parse(outfile)
    glab_result_write( "glab.txt", data, preamble=run_log+run_log2)
    
if __name__ == "__main__":

    # example processing:
    station = UTCStation.usno
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=5)
    current_dir = os.getcwd()
    
    # run gLAB PPP for given station, day
    glab_run(station, dt, prefixdir=current_dir)
