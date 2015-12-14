import os
import datetime
import shutil
import subprocess

import UTCStation
import ftp_tools
import bipm_ftp
import igs_ftp

gpsppp_binary = "gpsppp"

# write an inp-file for gpsppp. example:
# usn30730.14o
# 1day.cmd
# 0 0
# 0 0
# igr17835.sp3
# igr17836.sp3
# igr17835.clk
# igr17836.clk
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
    
def nrcan_run(station, dt, rapid=True, prefixdir=""):
    dt_start = datetime.datetime.utcnow()
    
    year = dt.timetuple().tm_year
    doy = dt.timetuple().tm_yday
    rinex = station.get_rinex( dt )
    

    
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
    
    # cmd-file
    cmdfile = prefixdir + "/gpsppp/1day.cmd"
    
    # write INP file
    inp_file = nrcan_inp_file( tempdir + "run.inp", rinex, cmdfile, eph_files, clk_files, rapid )

    # copy the DEF file to the temp/ directory
    def_source = prefixdir + '/gpsppp/gpsppp.def'
    def_target = prefixdir + '/temp/gpsppp.def'
    shutil.copy2( def_source , def_target )
    print "DEF= ", def_target
    
    #(server, username, password, igs_directory, igs_files, localdir) = igs_ftp.CODE_rapid_files(dt, prefixdir=prefixdir)
    #files = igs_ftp.CODE_download(server, username, password, igs_directory, igs_files, localdir)
    #(clk, eph, erp) = (files[0], files[1], files[2])

    run_log = ""
    run_log += " run start: %d-%02d-%02d %02d:%02d:%02d\n" % ( dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute, dt_start.second)
    run_log += "   Station: %s\n" % station.name
    run_log += "      Year: %d\n" % year
    run_log += "       DOY: %03d\n" % doy
    run_log += "      date:  %d-%02d-%02d\n" % (dt.year, dt.month, dt.day)
    run_log += "     RINEX: %s\n" % rinex
    run_log += "       CLK: %s\n" % clk_files  # allow for multiple clk-files!?
    run_log += "       EPH: %s\n" % eph_files
    run_log += "       ERP: %s\n" % erp_file
    print run_log


    
    # move files to temp_dir
    files_to_move = [ rinex, clk1, clk2, eph1, eph2, erp_file ]
    moved_files = []
    for f in files_to_move:
        shutil.copy2( f, tempdir )
        (tmp,fn ) = os.path.split(f)
        moved_files.append( tempdir + fn )
    print moved_files
    
    # unzip zipped files
    for f in moved_files:
        if f[-1] == "Z" or f[-1] == "z": # compressed .z or .Z file
            cmd ='/bin/gunzip'
            cmd = cmd + " -f " + f # -f overwrites existing file
            print "unzipping: ", cmd
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()
    
    # rename the ERP file - WHY
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
        hata_file = moved_files[0]
        cmd = "CRX2RNX " + hata_file[:-2]
        print "Hatanaka uncompress: ", cmd
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    

    
    # now gpsppp itself:
    #if not os.path.exists( result_file ):
    os.chdir( tempdir )
    cmd = gpsppp_binary + " < " + inp_file
    p = subprocess.Popen(cmd, shell=True, cwd = tempdir )
    p.communicate() # wait for processing to finish
    # read pos-file and archive result.
    products = [clk1, clk2, eph1, eph2, erp_file ]
    # archive_result( rinex, products, pos_file, result_file )
    # else:
    #    print pos_file, " exists. no need to run gpsppp."



    dt_end = datetime.datetime.utcnow()
    print "ppp_run Done ", dt_end
    print " elapsed = ", dt_end-dt_start
    
    """
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
    """
    
if __name__ == "__main__":

    # example processing:
    station = UTCStation.usno
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=5)
    current_dir = os.getcwd()
    
    # run NRCAN PPP for given station and datetime dt
    nrcan_run(station, dt, prefixdir=current_dir)
