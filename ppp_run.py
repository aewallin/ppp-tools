import os
import datetime
import shutil
import subprocess

import bipm_ftp
import igs_ftp

def check_dir(target_dir):
    # check that directory exsits, create if not
    if not os.path.isdir(target_dir):
        print "creating target directory ", target_dir
        os.mkdir(target_dir)

def delete_files(folder):
    # delete all files in given folder
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e

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

def result_write(outfile, data):
    """
        write gLAB output results to a neatly formatted file
        
        TODO: same format for rtkpost/gpsppp/gipsy ?
    """
    # TODO: preamble with metadata
    with open(outfile,'wb') as f:
        for row in data:
            f.write( "%04d %03d %05.03f %f %f %f %f %f %f \n" % (row[0], row[1], row[2], row[3], row[4],  row[5], row[6], row[7], row[8] ) )
    print "gLAB parsed output: ", outfile
    
def glab_run(station, dt, rapid=True, prefixdir=""):
    dt_start = datetime.datetime.now()
    
    year = dt.timetuple().tm_year
    doy = dt.timetuple().tm_yday
    rinex = station.rinex_download( dt )
    
    (server, igs_directory, igs_files, localdir) = igs_ftp.CODE_rapid_files(dt, prefixdir=prefixdir)
    files = igs_ftp.CODE_download(server, igs_directory, igs_files, localdir)
    (clk, eph, erp) = (files[0], files[1], files[2])

    print "ppp_run start: ", dt_start
    print "      Station: ", station.name
    print "          DOY: ", doy
    print "         Year: ", year
    print "        RINEX: ", rinex
    print "          CLK: ", clk
    print "          EPH: ", eph
    print "          ERP: ", erp
    # we do processing in a temp directory
    tempdir = prefixdir + "/temp/"
    check_dir( tempdir )
    # empty the temp directory
    delete_files(tempdir)
    
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

    dt_end = datetime.datetime.now()
    print "ppp_run Done: ", dt_end
    print "    elapsed : ", dt_end-dt_start
    print "gLAB raw output: ", outfile
    
    # here we may parse the output and store it to file somewhere
    data = glab_parse(outfile)
    result_write( "glab.txt", data)
    
if __name__ == "__main__":
    st = bipm_ftp.usno
    dt = datetime.datetime.now()-datetime.timedelta(days=3)
    current_dir = os.getcwd()
    
    # run PPP for given station, day
    glab_run(st, dt, prefixdir=current_dir)
