import ftplib
import datetime
import os
import sys

def check_dir(target_dir):
    # check that local target directory exists, create it if not
    if not os.path.isdir(target_dir):
        print "creating target directory ", target_dir
        os.mkdir(target_dir)

def delete_files(folder):
    # delete all files in given local folder
    # used for clearing the temp/ directory
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e
            
def ftp_download( server, username, password, remotedir, remotefile, localdir, overwrite=False):
    """
    Generic function to download a file using ftp.
    Place it in the local_directory.
    If it already exists, don't download.
    Return the full local filename.
    """
    check_dir( localdir )  # check that target dir exists, if not create it
    local_fullname = localdir + remotefile 
    print "ftp_download start at ", datetime.datetime.utcnow()
    if not os.path.exists( local_fullname ) or overwrite:
        print 'Remote: ', remotedir + remotefile
        print 'Local : ', local_fullname
        sys.stdout.flush()
        ftp = ftplib.FTP(server)  # Establish the connection
        ftp.login(username, password)
        ftp.cwd(remotedir) # Change to the proper directory
        fhandle = open(local_fullname, 'wb')
        ftp.retrbinary('RETR ' + remotefile, fhandle.write)
        fhandle.close()
        ftp.close()
    else:
        print remotefile," already exists locally, not downloading."
    print "ftp_download Done ", datetime.datetime.utcnow()
    sys.stdout.flush()
    return local_fullname

if __name__ == "__main__":
    pass
