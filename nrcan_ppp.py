import os
import datetime
import shutil
import subprocess
import struct

import UTCStation
import ftp_tools
import bipm_ftp
import igs_ftp

gpsppp_binary = "gpsppp"

# write an inp-file for gpsppp. 
# this corresponds to the keyboard-input we would type if we would
# run gpsppp manually.
#
# example:
# ---------------
# usn30730.14o
# 1day.cmd
# 0 0
# 0 0
# igr17835.sp3
# igr17836.sp3
# igr17835.clk
# igr17836.clk
# ----------------
def nrcan_inp_file(inpfile, rinex, cmdfile, eph_files, clk_files, rapid):
    with open(inpfile, 'w') as f:
        (tmp, rinexfile) = os.path.split( rinex[:-2] ) # strip off ".Z" from end of filename

        if rinexfile[-1] == "d":  # hatanaka compressed
             rinexfile = rinexfile[:-1] + 'o'
        if rinexfile[-1] == "D":
            rinexfile = rinexfile[:-1] + 'O'
            
        f.write( rinexfile +"\n" ) 
        f.write( cmdfile+"\n" )
        f.write( "0 0"+"\n" )
        f.write( "0 0"+"\n" )
        for a in eph_files:
            (tmp, a) = os.path.split( a )
            if rapid:
                f.write(a+"\n")
            else:
                f.write(a[:-2]+"\n")
        for a in clk_files:
            (tmp, a) = os.path.split( a )
            if rapid:
                f.write(a+"\n")
            else:
                f.write(a[:-2]+"\n")
        f.close()
    print "INP= ", inpfile
    return inpfile

# create a gpsppp.def file
#
# The four DLG-lines are included in the header of the output .pos file
#
# example:
# ---------
# 'LNG' 'ENGLISH' 
# 'TRF' '/home/anders/gpsppp/gpsppp.trf'
# 'SVB' '/home/anders/gpsppp/gpsppp.svb_gnss_yrly'
# 'PCV' '/home/anders/gpsppp/igs08.atx'
# 'FLT' '/home/anders/gpsppp/gpsppp.flt'
# 'OLC' '/home/anders/gpsppp/gpsppp_with_mike_kaja.olc'
# 'MET' '/home/anders/gpsppp/gpsppp.met'
# 'ERP' '/home/anders/BIPM/temp/gpsppp.ERP'
# 'GSD' 'Natural Resources Canada, Geodetic Survey Division, Geomatics Canada'
# 'GSD' '615 Booth Street, room 440, Ottawa, Ontario, Canada, K1A 0E9'
# 'GSD' 'Phone: (613) 995-4410, fax: (613) 995-3215'
# 'GSD' 'Email: information@geod.nrcan.gc.ca'
# 'DLG' 'Ressources naturelles Canada, Division des leves geodesiques, Geomatique Canada'
# 'DLG' '615 rue Booth, piece 440, Ottawa, Ontario, Canada, K1A 0E9'
# 'DLG' 'Telephone: (613) 995-4410, telecopieur: (613) 995-3215'
# 'DLG' 'Courriel: information@geod.nrcan.gc.ca '
# ---------
def nrcan_def_file(prefixdir, def_file):
    
    # these are fixed files for now. in principle they could vary from run to run.
    trf = "'%s/gpsppp/gpsppp.trf'" % prefixdir
    svb = "'%s/gpsppp/gpsppp.svb_gnss_yrly'" % prefixdir
    atx = "'%s/common/igs08.atx'" % prefixdir
    flt = "'%s/gpsppp/gpsppp.flt'" % prefixdir
    olc = "'%s/gpsppp/gpsppp.olc'" % prefixdir
    met = "'%s/gpsppp/gpsppp.met'" % prefixdir
    erp = "'%s/temp/gpsppp.ERP'" % prefixdir  # NOTE: this file is in the temp directory!
    
    with open(prefixdir  + "/temp/" +def_file, 'w') as f:
        f.write("'LNG' 'ENGLISH'\n")
        f.write("'SVB' %s\n" % svb)  
        f.write("'TRF' %s\n" % trf)  # coordinate transformations (?)
        f.write("'PCV' %s\n" % atx)  # antenna phase center variations 
        f.write("'FLT' %s\n" % flt)  # Filter configuration file
        f.write("'OLC' %s\n" % olc)  # ocean tide loading coefficients
        f.write("'MET' %s\n" % met)  # meteorological conditions (?)
        f.write("'ERP' %s\n" % erp)  # earth rotation parameters
        
        # this might include a version-string for ppp-tools also?
        f.write("'GSD' 'ppp-tools, from https://github.com/aewallin/ppp-tools'\n")

# PPP-processing with NRCan ppp
def nrcan_run(station, dt, rapid=True, prefixdir=""):
    dt_start = datetime.datetime.utcnow()
    
    year = dt.timetuple().tm_year
    doy = dt.timetuple().tm_yday
    rinex = station.get_rinex( dt ) # this downloads RINEX over ftp, if needed
    
    # get GPS Products
    clk_files =[]
    eph_files = []
    erp_file = "" # we do not use the ERP files, for now.
    if not rapid:
        (server, username, password, directory, files, localdir) = igs_ftp.CODE_final_files(dt, prefixdir)
        (clk1, eph1, erp1) =  igs_ftp.CODE_download(server, username, password, directory, files, localdir) # returns: [clk, sp3, erp]
        (server, username, password, directory, files, localdir) = igs_ftp.CODE_final_files(dt+datetime.timedelta(days=1), prefixdir) 
        (clk2, eph2, erp2) = igs_ftp.CODE_download(server, username, password, directory, files, localdir)
        clk_files = [ clk1, clk2 ]
        eph_files = [ eph1, eph2 ]
        erp_file = erp1
    elif rapid:
        (server, username, password, directory, files, localdir) = igs_ftp.CODE_rapid_files(dt, prefixdir)
        (clk1, eph1, erp1) =  igs_ftp.CODE_download(server, username, password, directory, files, localdir) # returns: [clk, sp3, erp]
        (server, username, password, directory, files, localdir) = igs_ftp.CODE_rapid_files(dt+datetime.timedelta(days=1), prefixdir)
        (clk2, eph2, erp2) = igs_ftp.CODE_download(server, username, password, directory, files, localdir)
        clk_files = [ clk1, clk2 ]
        eph_files = [ eph1, eph2 ]
        erp_file = erp1
    
    # we do processing in a temp directory
    tempdir = prefixdir + "/temp/"
    ftp_tools.check_dir( tempdir )
    # empty the temp directory
    ftp_tools.delete_files(tempdir)
    
    # us an existing cmd-file (doesn't change from run to run)
    cmdfile = prefixdir + "/gpsppp/1day.cmd"
    
    # write an INP file, corresponding to the keyboard-input required
    inp_file = nrcan_inp_file( tempdir + "run.inp", rinex, cmdfile, eph_files, clk_files, rapid )

    # write a DEF file
    nrcan_def_file( prefixdir, "gpsppp.def")
    
    # result will be stored in a POS file:
    (rinexdir,fn ) = os.path.split(rinex)
    nrcan_pos_file = tempdir + fn[:-5] + "pos"
    
    # copy the DEF file to the temp/ directory
    """
    def_source = prefixdir + '/gpsppp/gpsppp.def'
    def_target = prefixdir + '/temp/gpsppp.def'
    shutil.copy2( def_source , def_target )
    print "DEF= ", def_target
    """
    
    run_log = ""
    run_log += " run start: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute, dt_start.second)
    run_log += "   Station: %s\n" % station.name
    run_log += "      Year: %d\n" % year
    run_log += "       DOY: %03d\n" % doy
    run_log += "      date: %d-%02d-%02d\n" % (dt.year, dt.month, dt.day)
    run_log += "     RINEX: %s\n" % rinex
    run_log += "       CLK: %s\n" % clk_files  # allow for multiple clk-files!?
    run_log += "       EPH: %s\n" % eph_files
    run_log += "       ERP: %s\n" % erp_file
    print run_log

    # move RINEX, CLK, EPH, ERP files to temp_dir
    files_to_move = [ rinex, clk1, clk2, eph1, eph2, erp_file ]
    moved_files = []
    for f in files_to_move:
        shutil.copy2( f, tempdir )
        (tmp,fn ) = os.path.split(f)
        moved_files.append( tempdir + fn )
    print moved_files
    
    # unzip zipped files. this may include the RINEX, CLK, EPH files.
    for f in moved_files:
        if f[-1] == "Z" or f[-1] == "z": # compressed .z or .Z file
            cmd ='/bin/gunzip'
            cmd = cmd + " -f " + f # -f overwrites existing file
            print "unzipping: ", cmd
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()
    
    # rename the ERP file - becase the name is fixed to gpsppp.ERP in the DEF file.
    cmd ='/bin/mv'
    gpsppp_erp = prefixdir + "/temp/gpsppp.ERP"
    (tmp,fn ) = os.path.split(erp_file)  # [:-2]
    cmd = cmd + " " + tempdir + fn + " " + gpsppp_erp 
    print "rename command: ", cmd
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()
    
    # figure out the rinex file name
    print "rinex= ", rinex
    (tmp,rinexfile ) = os.path.split(rinex)
    inputfile = rinexfile[:-2] # strip off ".Z"
    
    # if the RINEX file is hatanaka-compressed, uncompress it
    if rinexfile[-3] == "d" or rinexfile[-3] == "D":
        hatanaka_file = moved_files[0]
        cmd = "CRX2RNX " + hatanaka_file[:-2]
        print "Hatanaka uncompress: ", cmd
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    
    # now gpsppp itself:
    os.chdir( tempdir )
    cmd = gpsppp_binary + " < " + inp_file
    p = subprocess.Popen(cmd, shell=True, cwd = tempdir )
    p.communicate() # wait for processing to finish

    dt_end = datetime.datetime.utcnow()
    run_log2=""
    run_log2 += "   run end: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_end.year, dt_end.month, dt_end.day, dt_end.hour, dt_end.minute, dt_end.second)
    delta = dt_end-dt_start
    run_log2+=  "   elapsed: %.2f s\n" % (delta.seconds+delta.microseconds/1.0e6)
    print run_log2

    # we may now do postprocessing and store the results.
    #
    # the result is named RINEX.pos, for example "usn63440.pos"
    #
    #
    # read pos-file and archive result.
    #products = [clk1, clk2, eph1, eph2, erp_file ]
    # archive_result( rinex, products, pos_file, result_file )
    # else:
    #    print pos_file, " exists. no need to run gpsppp."
    
    nrcan_archive_result( pos_file=nrcan_pos_file, prefixdir=prefixdir, result_file="result.txt", preamble=run_log+run_log2)

# parse the pos file and store the relevant results.
def nrcan_archive_result( pos_file , prefixdir, result_file, preamble="" ):
    print " read results from ", pos_file
    if os.path.exists(pos_file):
        result = nrcan_pos_read(pos_file, bwd=True)
        outfile = prefixdir + "/" + result_file
        with open(outfile,'w') as f:
            datastring = "# " + result_file + " \n"
            f.write(datastring)
            for line in preamble.split('\n'):
                f.write( "# %s\n" % line)

            datastring = "# Year\tMonth\tDay\tHour\tMin\tSec\tLat(deg)\tLon(deg)\tHeight(m)\tClock(ns)\tZTD(m)\n"
            f.write(datastring)
            for point in result.observations:
                f.write(str(point) + "\n")
    else:
        print "No pos file to read!"
    print " wrote results to ", outfile
    
    
# This function reads and parses the .pos file
#
# This is an older format:
#
# DIR FRAME        STN         DOY YEAR-MM-DD HR:MN:SS.SSS NSV GDOP    SDC    SDP       DLAT(m)       DLON(m)       DHGT(m)         CLK(ns)   TZD(m)  SLAT(m)  SLON(m)  SHGT(m) SCLK(ns)  STZD(m) LAT(d) LAT(m)    LAT(s) LON(d) LON(m)    LON(s)   HGT(m) NORTHING(m)  EASTING(m) ZONE SCALE_FACTOR HEMI  AM COMBINED_SCALE_FACTOR 
# FWD ITRF(IGb08) MARK 290.0003472 2013-10-17 00:00:30.000   6  3.4   0.83 0.0000         2.543        -0.205         2.830         250.994   2.3093   22.344   15.908   55.671   14.038   0.1000     64     13 58.18167     27     41  3.38254       173.566  7123137.761  533190.009   35      0.99961349 N   6 0.99958626 
#
# This is a more recent (2015 December) format:
#
# 0   1             2          3   4          5              6   7       8      9           19             11            12              13       14       15       16       17         18       19     20     21      22      23      24      25        26     27    28    29    30    31       32        33           34     35     36        37        38            39            40             41
# DIR FRAME        STN         DOY YEAR-MM-DD HR:MN:SS.SSS NSV GDOP    SDC    SDP       DLAT(m)       DLON(m)       DHGT(m)         CLK(ns)   TZD(m)   SLAT(m)  SLON(m)  SHGT(m)   SCLK(ns)  STZD(m) LAT(d) LAT(m)    LAT(s) LON(d) LON(m)    LON(s)   HGT(m)   AM GRAD1 GRAD2 SGRD1 SGRD2 WETZD(m) GLNCLK(ns) SGLNCLK(ns)  MAXNL  MAXWL  AVGNL(m)  AVGWL(m)  VTEC(.1TECU)  GPS_DP1P2(ns) GLN_DP1P2(ns)
# FWD ITRF(IGb08) usn6 344.0000000 2015-12-10 00:00:00.000  14  2.3   0.69 0.0000         0.532        -0.960        -2.344          -4.054   2.3456    1.286    1.217     2.935     7.468   0.0999     38     55 14.05525    -77      3 58.63558        56.579 14   0.0   0.0   0.0   0.0   0.0542     33.576       8.911 0.2000 1.5000   0.0000     0.0000         100.0            0.0           0.0
def nrcan_pos_read(filename, bwd=False):
    #nrcan_ns = []   # receiver clock in nanoseconds
    #nrcan_dt = []   # observation time-stamp
    nrcan_result = PPP_Result()
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("FWD") or line.startswith("BWD"):
                vals = line.split(" ")
                vals = filter(None, vals)
                (year,month,day) = struct.unpack("4sx2sx2s", vals[4])
                tod = vals[5].replace(":","")
                (h,m,s) = struct.unpack("2s2s6s", tod)
                if bwd: # if we want BWD, then retain only backward solution
                    if vals[0] != "BWD":
                        continue
                
                dt = datetime.datetime( int(year),int(month),int(day),int(h),int(m),int(float(s))) 
                clk = float( vals[13] )
                ztd = float( vals[14] )
                lat_deg = float( vals[20] )
                lat_min = float( vals[21] )
                lat_sec = float( vals[22] )
                lon_deg = float( vals[23] )
                lon_min = float( vals[24] )
                lon_sec = float( vals[25] )
                height  = float( vals[26] )
                lat = lat_deg + lat_min/60.0 + lat_sec/(3600.0)
                lon = lon_deg + lon_min/60.0 + lon_sec/(3600.0)
                
                p = PPP_Point( dt, lat, lon, height, clk, ztd )
                nrcan_result.append(p)
                #print float( vals[13] )
                """
                csrs_ztd.append( float( vals[14] ) )
                
                lat = lat_deg + lat_min/60 + lat_sec/(60*60)
                lon = lon_deg + lon_min/60 + lon_sec/(60*60)
                csrs_ecef.append( xyz2lla.lla2ecef( lat, lon, height ) )
                #print lat_deg, lat_min, lat_sec, lat
                csrs_lat.append(lat)
                csrs_lon.append(lon)
                csrs_h.append( height )                """
    #print len(csrs_secs)
    if bwd:
        # for the BWD solution, flip order
        nrcan_result.reverse()
    return nrcan_result

class PPP_Result():
    def __init__(self):
        self.observations=[]
        
    def append(self,p):
        self.observations.append(p)
    def reverse(self):
        self.observations.reverse()
        
class PPP_Point():
    def __init__(self,epoch, lat, lon, h, clock, ztd):
        self.epoch = epoch # epoch of observation, as a datetime object
        self.lat = lat # latitude in float degrees
        self.lon = lon # longitude in float degrees
        self.height = h
        self.clock = clock # receiver clock in nanoseconds
        self.ztd = ztd # zenith tropospheric delay in meters
        
    def __str__(self): # string representation
         return "%d\t%d\t%d\t%d\t%d\t%d\t%0.6f\t%0.6f\t%0.3f\t\t%0.3f\t\t%0.4f" % ( self.epoch.year, self.epoch.month, self.epoch.day, 
                                                                   self.epoch.hour, self.epoch.minute, self.epoch.second, 
                                                                   self.lat, self.lon, self.height, self.clock, self.ztd  )

if __name__ == "__main__":

    # example processing:
    station = UTCStation.usno
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=5)
    current_dir = os.getcwd()
    
    # run NRCAN PPP for given station and datetime dt
    nrcan_run(station, dt, prefixdir=current_dir)
    #nrcan_def_file(prefixdir=current_dir, def_file='test.def')
    
