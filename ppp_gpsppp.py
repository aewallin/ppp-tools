# this file is part of PPP-Tools
# https://github.com/aewallin/ppp-tools
# Licensed under GPLv2

import os
import datetime
import shutil
import subprocess
import struct

import station
import ftp_tools
import bipm_ftp
import igs_ftp
import ppp_common

# NRCAN Fortran code requiring license
#gpsppp_binary = "gpsppp"
#gpsppp_version = "GPS Precise Point Positioning (CSRS-PPP ver.1.05/34613/2013-12-12)" # FIXME, obtain at run-time from binary
#gpsppp_tag = "gpsppp" # used in the result file names

# GPSPACE open source version
# from https://github.com/aewallin/GPSPACE

gpsppp_binary = "gpspace"
gpsppp_version = "GPSPACE Precise Point Positioning (Version 1.10/25018/2018-09-07)"
gpsppp_tag = "gpspace"


def nrcan_inp_file(inpfile, rinex, cmdfile, eph_files, clk_files, rapid):
    """
    write an inp-file for gpsppp. 
    this corresponds to the keyboard-input we would type if we would
    run gpsppp/gpspace manually.

    example:
    ---------------
    usn30730.14o       # the RINEX file
    1day.cmd           # CMD-file
    0 0
    0 0
    igr17835.sp3       # orbit file
    igr17836.sp3       # orbit file
    igr17835.clk       # clock file
    igr17836.clk       # clock file
    ----------------
    """
    with open(inpfile, 'w') as f:
        # strip off ".Z" from end of filename
        (tmp, rinexfile) = os.path.split(rinex[:-2])
        if rinexfile[-1] == ".":  # if ending was .gz
            rinexfile = rinexfile[:-1]

        if rinexfile[-1] == "d":  # hatanaka compressed
            rinexfile = rinexfile[:-1] + 'o'
        if rinexfile[-1] == "D":
            rinexfile = rinexfile[:-1] + 'O'

        f.write(rinexfile + "\n")
        f.write(cmdfile+"\n")
        f.write("0 0"+"\n")
        f.write("0 0"+"\n")
        for a in eph_files:
            (tmp, a) = os.path.split(a)
            if rapid:
                f.write(a+"\n")
            else:
                f.write(a[:-2]+"\n")
        for a in clk_files:
            (tmp, a) = os.path.split(a)
            if rapid:
                f.write(a+"\n")
            else:
                f.write(a[:-2]+"\n")
        f.close()
    print("INP= ", inpfile)
    return inpfile


def nrcan_def_file(prefixdir, def_file):
    """
    create a gpsppp.def file
    the file defines locations of helper files

    GSD/DLG-lines are headers in English/French, included in the header of the output .pos file

    example gpsppp.def file:
    ---------
    'LNG' 'ENGLISH' 
    'TRF' '/gpsppp/gpsppp.trf'
    'SVB' '/gpsppp/gpsppp.svb_gnss_yrly'
    'PCV' '/gpsppp/igs08.atx'
    'FLT' '/gpsppp/gpsppp.flt'
    'OLC' '/gpsppp/gpsppp_with_mike_kaja.olc'
    'MET' '/gpsppp/gpsppp.met'
    'ERP' '/BIPM/temp/gpsppp.ERP'
    'GSD' 'Natural Resources Canada, Geodetic Survey Division, Geomatics Canada'
    'GSD' '615 Booth Street, room 440, Ottawa, Ontario, Canada, K1A 0E9'
    'GSD' 'Phone: (613) 995-4410, fax: (613) 995-3215'
    'GSD' 'Email: information@geod.nrcan.gc.ca'
    'DLG' 'Ressources naturelles Canada, Division des leves geodesiques, Geomatique Canada'
    'DLG' '615 rue Booth, piece 440, Ottawa, Ontario, Canada, K1A 0E9'
    'DLG' 'Telephone: (613) 995-4410, telecopieur: (613) 995-3215'
    'DLG' 'Courriel: information@geod.nrcan.gc.ca '
    ---------
    """
    # these are fixed files for now. in principle they could vary from run to run.
    trf = "'%s/gpsppp/gpsppp.trf'" % prefixdir
    svb = "'%s/gpsppp/gpsppp.svb'" % prefixdir # _gnss_yrly
    atx = "'%s/common/igs14.atx'" % prefixdir
    flt = "'%s/gpsppp/gpsppp.flt'" % prefixdir
    olc = "'%s/gpsppp/gpsppp.olc'" % prefixdir
    met = "'%s/gpsppp/gpsppp.met'" % prefixdir
    # NOTE: this file is in the temp directory!
    erp = "'%s/temp/gpsppp.ERP'" % prefixdir

    with open(prefixdir + "/temp/" + def_file, 'w') as f:
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

def nrcan_cmd_file(prefixdir, cmd_file, num_days=1):
    """
    create a  cmd file for gpspace

    example 1day.cmd file:
    ---------
    ' UT DAYS OBSERVED                      (1-45)'                   2
    ' USER DYNAMICS         (1=STATIC,2=KINEMATIC)'                   1
    ' OBSERVATION TO PROCESS         (1=COD,2=C&P)'                   2
    ' FREQUENCY TO PROCESS        (1=L1,2=L2,3=L3)'                   3
    ' SATELLITE EPHEMERIS INPUT     (1=BRD ,2=SP3)'                   2
    ' SAT CLOCKS(1=NO,2=Prc,3=RTCA,4=RTCM,+10=!AR)'                   2
    ' SATELLITE CLOCK INTERPOLATION   (1=NO,2=YES)'                   1
    ' IONOSPHERIC GRID (1=NO,2=YES,3=INIT,+10*MFi)'                   1
    ' SOLVE STATION COORDINATES       (1=NO,2=YES)'                   2
    ' SOLVE TROP. (1=NO,2-5=RW MM/HR)  (+100=grad)'                 105
    ' BACKWARD SUBSTITUTION    (1=NO,2=YES,3=!CLK)'                   2
    ' REFERENCE SYSTEM            (1=NAD83,2=ITRF)'                   2
    ' COORDINATE SYSTEM(1=ELLIPSOIDAL,2=CARTESIAN)'                   1
    ' A-PRIORI PSEUDORANGE SIGMA(m)    [&MISC TOL]'              5.0000   9.00
    ' A-PRIORI CARRIER PHASE SIGMA(m)  [&MISC TOL]'               .0100   9.00
    ' LAT(ddmmss.sss,+N) | ECEF X(m) [&VEL(mm/yr)]'              0.0000   0.00
    ' LON(ddmmss.sss,+E) | ECEF Y(m) [&VEL(mm/yr)]'              0.0000   0.00
    ' HEIGHT (m)         | ECEF Z(m) [&VEL(mm/yr)]'              0.0000   0.00
    ' ANTENNA HEIGHT                           (m)'              0.0000
    ' CUTOFF ELEVATION                       (deg)'              5.0000
    ' GDOP CUTOFF                                 '             20.0000
    ---------
    """
    with open(prefixdir + "/temp/" + cmd_file, 'w') as f:
        f.write("' UT DAYS OBSERVED                      (1-45)'%20d\n"%(num_days+1))
        # f.write("' UT DAYS OBSERVED                      (1-45)'                   2\n")
        f.write("' USER DYNAMICS         (1=STATIC,2=KINEMATIC)'                   1\n")
        f.write("' OBSERVATION TO PROCESS         (1=COD,2=C&P)'                   2\n")
        f.write("' FREQUENCY TO PROCESS        (1=L1,2=L2,3=L3)'                   3\n")
        f.write("' SATELLITE EPHEMERIS INPUT     (1=BRD ,2=SP3)'                   2\n")
        f.write("' SAT CLOCKS(1=NO,2=Prc,3=RTCA,4=RTCM,+10=!AR)'                   2\n")
        f.write("' SATELLITE CLOCK INTERPOLATION   (1=NO,2=YES)'                   1\n")
        f.write("' IONOSPHERIC GRID (1=NO,2=YES,3=INIT,+10*MFi)'                   1\n")
        f.write("' SOLVE STATION COORDINATES       (1=NO,2=YES)'                   2\n")
        f.write("' SOLVE TROP. (1=NO,2-5=RW MM/HR)  (+100=grad)'                 105\n")
        f.write("' BACKWARD SUBSTITUTION    (1=NO,2=YES,3=!CLK)'                   2\n")
        f.write("' REFERENCE SYSTEM            (1=NAD83,2=ITRF)'                   2\n")
        f.write("' COORDINATE SYSTEM(1=ELLIPSOIDAL,2=CARTESIAN)'                   1\n")
        f.write("' A-PRIORI PSEUDORANGE SIGMA(m)    [&MISC TOL]'              5.0000   9.00\n")
        f.write("' A-PRIORI CARRIER PHASE SIGMA(m)  [&MISC TOL]'               .0100   9.00\n")
        f.write("' LAT(ddmmss.sss,+N) | ECEF X(m) [&VEL(mm/yr)]'              0.0000   0.00\n")
        f.write("' LON(ddmmss.sss,+E) | ECEF Y(m) [&VEL(mm/yr)]'              0.0000   0.00\n")
        f.write("' HEIGHT (m)         | ECEF Z(m) [&VEL(mm/yr)]'              0.0000   0.00\n")
        f.write("' ANTENNA HEIGHT                           (m)'              0.0000\n")
        f.write("' CUTOFF ELEVATION                       (deg)'              5.0000\n")
        f.write("' GDOP CUTOFF                                 '             20.0000\n")
    return cmd_file
    
def nrcan_parse_result(filename, my_station, inputfile, bwd=False):
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
    #
    # as of 2021 June the pos file format with gpspace is:
    # (numbers refer to list-index after split())
    #
    # 0   1              2           3          4            5   6    7      8      9            10           11            12               13       14      15        16       17       18       19     20     21        22     23    24        25        26
    # DIR FRAME        STN         DOY YEAR-MM-DD HR:MN:SS.SSS NSV GDOP    SDC    SDP       DLAT(m)       DLON(m)       DHGT(m)         CLK(ns)   TZD(m)  SLAT(m)  SLON(m)  SHGT(m) SCLK(ns)  STZD(m) LAT(d) LAT(m)    LAT(s) LON(d) LON(m)    LON(s)   HGT(m)    AM GRAD1 GRAD2 SGRD1 SGRD2 WETZD(m) GLNCLK(ns) SGLNCLK(ns) GALCLK(ns) SGALCLK(ns) BEICLK(ns) SBEICLK(ns) MAXNL MAXWL AVGNL(m) AVGWL(m) VTEC(.1TECU) GPS_DP1P2(ns) GLN_DP1P2(ns) RIFRATE NAMBFIX NSVDWGT
    # FWD ITRF(IGb14) MARK 171.0000000 2021-06-20 00:00:00.000  10  2.2   0.80 0.0000        -0.156         0.286         2.134           4.111   2.3917    1.510    1.073    2.987    7.352   0.0999     60     10 49.23731     24     49 35.53626        62.451 10   0.0   0.0   0.0   0.0   0.0901           0.000    0.000          0.000    0.000          0.000    0.000     0.2000     1.5000     0.0000     0.0000    100.0      0.0      0.0      0.0  0  0

    nrcan_result = ppp_common.PPP_Result()
    nrcan_result.station = my_station
    if not os.path.exists(filename):
        print("No pos file to read!")
        print("expexted to find ", filename)
        assert(0)

    print(" read results from ", filename)
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("FWD") or line.startswith("BWD"):
                vals = line.split(" ")
                vals = [_f for _f in vals if _f]
                #(year,month,day) = struct.unpack("4sx2sx2s", bytes(vals[4]))
                #tod = vals[5].replace(":","")
                #(h,m,s) = struct.unpack("2s2s6s", bytes(tod))
                if bwd:  # if we want BWD, then retain only backward solution
                    if vals[0] != "BWD":
                        continue

                #dt = datetime.datetime( int(year),int(month),int(day),int(h),int(m),int(float(s)))

                dt = datetime.datetime.strptime(
                    vals[4]+" "+vals[5][:-4], '%Y-%m-%d %H:%M:%S')

                clk = float(vals[13])  # receiver clock (ns)
                clk = clk - my_station.cab_dly - my_station.int_dly_p3() + my_station.ref_dly
                ztd = float(vals[14])  # zenith trposphere delay (m)
                lat = float(vals[20]) + float(vals[21])/60.0 + \
                    float(vals[22])/(3600.0)  # latitude
                lon = float(vals[23]) + float(vals[24])/60.0 + \
                    float(vals[25])/(3600.0)  # longitude
                height = float(vals[26])  # height (m)
                p = ppp_common.PPP_Point(dt, lat, lon, height, clk, ztd)
                nrcan_result.append(p)

    if bwd:  # for the BWD solution, flip order so results are 'forward' again
        nrcan_result.reverse()
    return nrcan_result

def run_multiday(station, dtend, num_days, rapid=True, prefixdir=""):
    """
        multi-day run, ending at given datetime dtend
        num_days specifies number of days.
        
    """
    original_dir = prefixdir
    dt_start = datetime.datetime.utcnow()  # for timing how long processing takes

    # we do processing in a temp directory
    tempdir = prefixdir + "/temp/"
    ftp_tools.check_dir(tempdir)
    ftp_tools.delete_files(tempdir)  # empty the temp directory
    
    # get spliced multi-day rinex file
    dtlist, rinex, rlist = station.get_multiday_rinex(dtend, num_days=num_days)  # this downloads RINEX over ftp, if needed
    # results in uncompressed "splice.rnx" file in the temp-directory.
    # dtlist has the datetimes for the days we will process
    print(dtlist)
    print(rinex)
    

    
    # get GPS Products
    # nrcan ppp wants IGS products for two days.
    # if we process day N, we need products for N and N+1
    clk_files = []
    eph_files = []
    erp_file = ""  # we do not use the ERP files, for now.
    dtlist.append( dtlist[-1]+datetime.timedelta(days=1) ) # add one day
    for dt in dtlist:
        if not rapid:  # Final products
            (clk1, eph1, erp1) = igs_ftp.get_CODE_final(dt, prefixdir)

        elif rapid:  # Rapid products
            (clk1, eph1, erp1) = igs_ftp.get_CODE_rapid(dt, prefixdir)
        clk_files.append(clk1)
        eph_files.append(eph1)
        erp_file = erp1
    print("clk_files: ",str(clk_files))
    print("eph_files: ",str(eph_files))
    
    run_log = ""
    run_log += " run start: %d-%02d-%02d %02d:%02d:%02d\n" % (
        dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute, dt_start.second)
    run_log += "   Program: %s\n" % gpsppp_version
    run_log += "   Station: %s\n" % station.name
    run_log += "  Year_end: %d\n" % dtend.timetuple().tm_year
    run_log += "   DOY_end: %03d\n" % dtend.timetuple().tm_yday
    run_log += "      date: %d-%02d-%02d\n" % (dtend.year, dtend.month, dtend.day)
    run_log += "  num_days: %d\n" % num_days
    run_log += "     RINEX: %s\n" % rinex[len(tempdir):]
    for r in rlist:
        run_log += " src RINEX: %s\n" % r[len(tempdir):]
    for c in clk_files:
        run_log += "       CLK: %s\n" % c[len(prefixdir):]
    for e in eph_files:
        run_log += "       EPH: %s\n" % e[len(prefixdir):]
    run_log += "       ERP: %s\n" % erp_file[len(prefixdir):]
    print(run_log)
    
    
    cmd_file = nrcan_cmd_file(prefixdir, "md.cmd", num_days)
    
    # use an existing cmd-file (doesn't change from run to run)
    #cmdfile = prefixdir + "/gpsppp/2day.cmd"
    cmdfile = tempdir + cmd_file
    
    # write an INP file, corresponding to the keyboard-input required
    inp_file = nrcan_inp_file(
        tempdir + "run.inp", rinex+".Z", cmdfile, eph_files, clk_files, rapid)
    
    # write a DEF file
    nrcan_def_file(prefixdir, "gpsppp.def")
    nrcan_pos_file = tempdir + "splice.pos"
    
    # move  CLK, EPH, ERP files to temp_dir
    files_to_move = clk_files + eph_files + [erp_file]
    moved_files = []
    for f in files_to_move:
        shutil.copy2(f, tempdir)
        (tmp, fn) = os.path.split(f)
        moved_files.append(tempdir + fn)
    print("moved files: ",str(moved_files))

    # unzip zipped files. this may include the RINEX, CLK, EPH files.
    for f in moved_files:
        if f[-1] == "Z" or f[-1] == "z":  # compressed .z or .Z file
            cmd = '/bin/gunzip'
            cmd = cmd + " -f " + f  # -f overwrites existing file
            print("unzipping: ", cmd)
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()

    # rename the ERP file - becase the name is fixed to gpsppp.ERP in the DEF file.
    cmd = '/bin/mv'
    gpsppp_erp = prefixdir + "/temp/gpsppp.ERP"
    (tmp, fn) = os.path.split(erp_file)  # [:-2]
    if fn[-1]=='Z': # final products are zipped
        fn = fn[:-2] # strip off '.Z'S
    cmd = cmd + " " + tempdir + fn + " " + gpsppp_erp
    print("rename command: ", cmd)
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()
    
    # if RINEX version 3, use gfzrnx to convert 3->2
    if station.rinex3:
        print('Converting RINEX v3 to v2')
        v3file = rinex + "_rx3" # rename the v3 file
        cmd = "mv " + rinex + " " + v3file
        print("rename v3 file: ", cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    
        #v2file = inputfile[:-1]+"2"  # name ending in "O" or "o" is replaced with "2" for v2 rinex
        cmd = "gfzrnx -finp " + v3file + " -fout " + rinex + " --version_out 2"
        print("3to2 command: ",cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        # use the v2 file for the rest of the run
        #inputfile = v2file

    # now gpsppp itself:
    os.chdir(tempdir)
    cmd = gpsppp_binary + " < " + inp_file
    p = subprocess.Popen(cmd, shell=True, cwd=tempdir)
    p.communicate()  # wait for processing to finish

    dt_end = datetime.datetime.utcnow()
    delta = dt_end-dt_start
    run_log2 = "   run end: %d-%02d-%02d %02d:%02d:%02d\n" % (
        dt_end.year, dt_end.month, dt_end.day, dt_end.hour, dt_end.minute, dt_end.second)
    run_log2 += "   elapsed: %.2f s\n" % (delta.seconds +
                                          delta.microseconds/1.0e6)
    print(run_log2)
    print("---------------------------------")

    # we may now do postprocessing and store the results.
    # the result is named RINEX.pos, for example "usn63440.pos"
    ppp_result = nrcan_parse_result(
        nrcan_pos_file, station, rinex, bwd=True)
        
    run_log2 += " first obs: %s\n" % ppp_result.observations[0].epoch
    run_log2 += "  last obs: %s\n" % ppp_result.observations[-1].epoch
    run_log2 += "   num obs: %d\n" % len(ppp_result.observations)
    
    result_file = ppp_common.write_result_file(
        ppp_result=ppp_result, preamble=run_log+run_log2, rapid=rapid, tag=gpsppp_tag, prefixdir=prefixdir, num_days=num_days)
    os.chdir(original_dir)  # change back to original directory
    return result_file
    
def run(station, dt, rapid=True, prefixdir=""):
    """
    PPP-processing with NRCan ppp.

    requires "gpsppp" or "gpspace" binary

    """
    print("------------------------------------")

    print("PPP-processing with NRCan ppp.")

    original_dir = prefixdir
    dt_start = datetime.datetime.utcnow()  # for timing how long processing takes

    year = dt.timetuple().tm_year
    doy = dt.timetuple().tm_yday
    rinex = station.get_rinex(dt)  # this downloads RINEX over ftp, if needed

    # get GPS Products
    # nrcan ppp wants IGS products for two days.
    # if we process day N, we need products for N and N+1
    clk_files = []
    eph_files = []
    erp_file = ""  # we do not use the ERP files, for now.
    if not rapid:  # Final products
        (clk1, eph1, erp1) = igs_ftp.get_CODE_final(dt, prefixdir)
        (clk2, eph2, erp2) = igs_ftp.get_CODE_final(
            dt+datetime.timedelta(days=1), prefixdir)
        clk_files = [clk1, clk2]
        eph_files = [eph1, eph2]
        erp_file = erp1
    elif rapid:  # Rapid products
        (clk1, eph1, erp1) = igs_ftp.get_CODE_rapid(dt, prefixdir)
        (clk2, eph2, erp2) = igs_ftp.get_CODE_rapid(
            dt+datetime.timedelta(days=1), prefixdir)
        clk_files = [clk1, clk2]
        eph_files = [eph1, eph2]
        erp_file = erp1

    # we do processing in a temp directory
    tempdir = prefixdir + "/temp/"
    ftp_tools.check_dir(tempdir)
    ftp_tools.delete_files(tempdir)  # empty the temp directory

    # use an existing cmd-file (doesn't change from run to run)
    cmdfile = prefixdir + "/gpsppp/1day.cmd"

    # write an INP file, corresponding to the keyboard-input required
    inp_file = nrcan_inp_file(
        tempdir + "run.inp", rinex, cmdfile, eph_files, clk_files, rapid)

    # write a DEF file
    nrcan_def_file(prefixdir, "gpsppp.def")

    # result will be stored in a POS file:
    (rinexdir, fn) = os.path.split(rinex)
    if fn[-3:] == ".gz":
        nrcan_pos_file = tempdir + fn[:-6] + "pos"
    else:
        nrcan_pos_file = tempdir + fn[:-5] + "pos"

    run_log = ""
    run_log += " run start: %d-%02d-%02d %02d:%02d:%02d\n" % (
        dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute, dt_start.second)
    run_log += "   Program: %s\n" % gpsppp_version
    run_log += "   Station: %s\n" % station.name
    run_log += "      Year: %d\n" % year
    run_log += "       DOY: %03d\n" % doy
    run_log += "      date: %d-%02d-%02d\n" % (dt.year, dt.month, dt.day)
    run_log += "     RINEX: %s\n" % rinex[len(prefixdir):]
    run_log += "       CLK: %s\n" % [c[len(prefixdir):] for c in clk_files]
    run_log += "       EPH: %s\n" % [e[len(prefixdir):] for e in eph_files]
    run_log += "       ERP: %s\n" % erp_file[len(prefixdir):]
    print(run_log)

    # move RINEX, CLK, EPH, ERP files to temp_dir
    files_to_move = [rinex, clk1, clk2, eph1, eph2, erp_file]
    moved_files = []
    for f in files_to_move:
        shutil.copy2(f, tempdir)
        (tmp, fn) = os.path.split(f)
        moved_files.append(tempdir + fn)
    print(moved_files)

    # unzip zipped files. this may include the RINEX, CLK, EPH files.
    for f in moved_files:
        if f[-1] == "Z" or f[-1] == "z":  # compressed .z or .Z file
            cmd = '/bin/gunzip'
            cmd = cmd + " -f " + f  # -f overwrites existing file
            print("unzipping: ", cmd)
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()

    # rename the ERP file - becase the name is fixed to gpsppp.ERP in the DEF file.
    cmd = '/bin/mv'
    gpsppp_erp = prefixdir + "/temp/gpsppp.ERP"
    (tmp, fn) = os.path.split(erp_file)  # [:-2]
    cmd = cmd + " " + tempdir + fn + " " + gpsppp_erp
    print("rename command: ", cmd)
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()

    # figure out the rinex file name
    print("rinex= ", rinex)
    (tmp, rinexfile) = os.path.split(rinex)
    inputfile = rinexfile[:-2]  # strip off ".Z"
    if inputfile[-1] == ".":  # ends in a dot
        inputfile = inputfile[:-1]  # strip off

    # if the RINEX file is hatanaka-compressed, uncompress it
    if inputfile[-1] == "d" or inputfile[-1] == "D":
        hata_file = moved_files[0]
        hata_file = hata_file[:-2]  # strip off ".Z"
        if hata_file[-1] == ".":
            hata_file = hata_file[:-1]  # stip off more

        cmd = "CRX2RNX " + hata_file
        print("Hatanaka uncompress: ", cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()

    # if RINEX version 3, use gfzrnx to convert 3->2
    if station.rinex3:
        print('Converting RINEX v3 to v2')
        v3file = tempdir+inputfile + "_rx3" # rename the v3 file
        cmd = "mv " + tempdir + inputfile + " " + v3file
        print("rename v3 file: ", cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    
        #v2file = inputfile[:-1]+"2"  # name ending in "O" or "o" is replaced with "2" for v2 rinex
        cmd = "gfzrnx -finp " + v3file + " -fout " + tempdir+inputfile + " --version_out 2"
        print("3to2 command: ",cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        # use the v2 file for the rest of the run
        #inputfile = v2file

    # now gpsppp itself:
    os.chdir(tempdir)
    cmd = gpsppp_binary + " < " + inp_file
    p = subprocess.Popen(cmd, shell=True, cwd=tempdir)
    p.communicate()  # wait for processing to finish

    dt_end = datetime.datetime.utcnow()
    delta = dt_end-dt_start
    run_log2 = "   run end: %d-%02d-%02d %02d:%02d:%02d\n" % (
        dt_end.year, dt_end.month, dt_end.day, dt_end.hour, dt_end.minute, dt_end.second)
    run_log2 += "   elapsed: %.2f s\n" % (delta.seconds +
                                          delta.microseconds/1.0e6)
    print(run_log2)
    print("---------------------------------")

    # we may now do postprocessing and store the results.
    # the result is named RINEX.pos, for example "usn63440.pos"
    ppp_result = nrcan_parse_result(
        nrcan_pos_file, station, inputfile, bwd=True)
    run_log2 += " first obs: %s\n" % ppp_result.observations[0].epoch
    run_log2 += "  last obs: %s\n" % ppp_result.observations[-1].epoch
    run_log2 += "   num obs: %d\n" % len(ppp_result.observations)
    result_file = ppp_common.write_result_file(
        ppp_result=ppp_result, preamble=run_log+run_log2, 
        rapid=rapid, tag=gpsppp_tag, prefixdir=prefixdir)
    os.chdir(original_dir)  # change back to original directory
    return result_file


if __name__ == "__main__":
    # example processing:
    #station1 = station.mi04
    #station1 = station.mi05
    station1 = station.mi02
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=4)  # 4 days ago
    current_dir = os.getcwd()

    # run NRCAN PPP for given station and datetime dt
    run(station1, dt, prefixdir=current_dir)
