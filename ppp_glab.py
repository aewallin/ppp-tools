"""
    This file is part of ppp-tools, https://github.com/aewallin/ppp-tools/
    
    This file implements PPP-runs with ESA gLAB
    http://gage.upc.edu/gLAB
    
"""
import os
import datetime
import shutil
import subprocess

import station
import ftp_tools
import bipm_ftp
import igs_ftp
import ppp_common

glab_tag = "glab" # used in the results-file filename
glab_binary = "gLAB_linux" # must have this executable in path

def glab_parse_result(fname, my_station, backward=True):
    """
        parse the FILTER data fields from gLAB outuput
        to a format defined by PPP_Result
        
    """
    ppp_result = ppp_common.PPP_Result()
    ppp_result.station = my_station
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
                clk = clk - my_station.cab_dly - my_station.int_dly_p3() + my_station.ref_dly
                ztd = float(fields[8]) # Zenith Tropospheric Delay [m]
                p = ppp_common.PPP_Point( dt, lat, lon, height, clk, ztd )
                ppp_result.append(p)
                
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
    print(len(ppp_result))
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
    print("gLAB parsed output: ", outfile)

def run(station, dt, rapid=True, prefixdir=""):
    """
    PPP run using ESA gLAB
    
    """
    print("ESA gLAB PPP-run")
    original_dir = prefixdir
    dt_start = datetime.datetime.utcnow()

    doy = dt.timetuple().tm_yday
    rinex = station.get_rinex( dt ) # download rinex file

    print("getting IGS products:")
    # download IGS products
    if rapid:
        (clk, eph, erp) = igs_ftp.get_CODE_rapid(dt, prefixdir)
    else:
        (clk, eph, erp) = igs_ftp.get_CODE_final(dt, prefixdir)

    print("IGS products done.")
    print("-------------------")

    #(rnx_dir,rnx_filename ) = os.path.split(rinex)
    # log input files, for writing to the result file
    run_log  = " run start: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute, dt_start.second)
    run_log += "   Station: %s\n" % station.name
    run_log += "      Year: %d\n" % dt.year
    run_log += "       DOY: %03d\n" % doy
    run_log += "      date:  %d-%02d-%02d\n" % (dt.year, dt.month, dt.day)
    run_log += "     RINEX: %s\n" % rinex[len(prefixdir):]

    run_log += "       CLK: %s\n" % clk[len(prefixdir):]
    run_log += "       EPH: %s\n" % eph[len(prefixdir):]
    run_log += "       ERP: %s\n" % erp[len(prefixdir):]
    print(run_log)
    print("-------------------")
    
    # we do processing in a temp directory
    tempdir = prefixdir + "/temp/"
    ftp_tools.check_dir( tempdir )
    ftp_tools.delete_files(tempdir) # empty the temp directory

    # copy files to tempdir
    files_to_copy = [ rinex, clk, eph,  erp ]
    copied_files = []
    for f in files_to_copy:
        shutil.copy2( f, tempdir )
        (tmp,fn ) = os.path.split(f)
        copied_files.append( tempdir + fn )
    print("copied files: ", copied_files)

    # unzip zipped files, if needed
    for f in copied_files:
        if f[-1] == "Z" or f[-1] == "z": # compressed .z or .Z file
            cmd ='/bin/gunzip'
            cmd = cmd + " -f " + f # -f overwrites existing file
            print("unzipping: ", cmd)
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()

    # Hatanaka uncompress - if needed
    #rinexfile = copied_files[0] # the first file is the unzipped RINEX, in the temp dir
    if rinex[-3] == "d" or rinex[-3] == "D" or rinex[-4] == "D":  # can end .z, .Z, or .gz - so the "d" is in position -3 or -4
        hata_file = copied_files[0]
        hata_file = hata_file[:-2] # strip off ".Z"
        if rinex[-4] == "D":
            hata_file = hata_file[:-1] # stip off more
        #print "hata ", hata_file
        cmd = "CRX2RNX " + hata_file
        print("Hatanaka uncompress: ", cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    

    # figure out the rinex file name
    (tmp,rinexfile ) = os.path.split(rinex)
    inputfile = rinexfile[:-2] # strip off ".Z"
    
    if inputfile[-1] == ".": # ends in a dot
        inputfile = inputfile[:-1] # strip off
        
    if inputfile[-1] == "d" or inputfile[-1] == "D":
        # if hatanaka compressed, we already uncompressed, so change to "O"
        inputfile = inputfile[:-1]+"O"
    
    
    # now ppp itself:
    os.chdir( tempdir )

    antfile = prefixdir + "/common/igs14.atx"
    outfile = tempdir + "out.txt"
    eph = copied_files[2]
    clk = copied_files[1]
    inputfile = tempdir + inputfile
    
    if eph[-1] == "Z":
        eph = eph[:-2]
    if clk[-1] == "Z":
        clk = clk[:-2]
            
    print("inputfile for gLAB is: ",inputfile)
    
    cmd =  glab_binary # must have this executable in path
    # see doc/glab_options.txt
    q_trop=1e-6 # [default 1e-4] (m^2/h)
    q_clk = 9e6 # [default 9e10] (m^2)
    p0_clk = 9e10 # [default 9e10] (m^2)
    
    options = [ " -input:obs %s" % inputfile,               # RINEX observation file
                " -input:clk %s" % clk,                     
                " -input:orb %s" % eph,                     # SP3 Orbits
                " -input:ant %s" % antfile,
                # " -model:recphasecenter ANTEX", 
                # " -model:recphasecenter no",              # use this option if RINEX-file antenna not in ANTEX file  
                " -model:trop",                             # correct for troposphere
                #" -model:iono FPPP",
                " -output:file %s" % outfile,
                " -pre:dec 30",                             # rinex data is at 30s intervals, don't decimate
                " -pre:elevation 10",                       # elevation mask
                " -pre:availf G12"                          # GPS frequencies L1 and L2
                " -filter:trop",
                " -filter:q:trop %.2g" % q_trop,            # Specify the Q noise variation value for troposphere unknown [default 1e-4] (m^2/h)
                " -filter:q:clk %.2g" % q_clk,              # Specify the Q noise value for clock unknown [default 9e10] (m^2)
                " -filter:p0:clk %.2g" % p0_clk,            # Specify the P0 initial value for clock unknown [default 9e10] (m^2)
                " -filter:backward",                        # runs filter both FWD and BWD
                " --print:input",                           # discard unnecessary output
                " --print:model",
                " --print:prefit",
                " --print:postfit",
                " --print:satellites" ]
    if station.antex:
        options.append(" -model:recphasecenter ANTEX")
    else:
        options.append(" -model:recphasecenter no") # USNO receiver antenna is not in igs08.atx (?should it be?)

    for opt in options:
        cmd += opt
    
    print("gLAB command: %s"% cmd)
    p = subprocess.Popen(cmd, shell=True, cwd = tempdir )
    p.communicate() # wait for processing to finish

    dt_end = datetime.datetime.utcnow()
    delta = dt_end-dt_start
    run_log2  = "   run end: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_end.year, dt_end.month, dt_end.day, dt_end.hour, dt_end.minute, dt_end.second)
    run_log2 += "   elapsed: %.2f s\n" % (delta.seconds+delta.microseconds/1.0e6)
    
    print(run_log2)
    print("-------------------")

    # here we may parse the output and store it to file somewhere
    ppp_result = glab_parse_result(outfile, station)
    run_log2 += " first obs: %s\n" % ppp_result.observations[0].epoch
    run_log2 += "  last obs: %s\n" % ppp_result.observations[-1].epoch
    run_log2 += "   num obs: %d\n" % len(ppp_result.observations)
    
    ppp_common.write_result_file( ppp_result=ppp_result, preamble=run_log+run_log2, rapid=rapid, tag=glab_tag, prefixdir=prefixdir )
    os.chdir(original_dir)

if __name__ == "__main__":

    # example processing:
    station1 = station.mi04
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=6)
    current_dir = os.getcwd()

    # run gLAB PPP for given station, day
    run(station1, dt, prefixdir=current_dir)
    
