import os
import datetime
import shutil
import subprocess
import struct

import station
import ftp_tools
import bipm_ftp
import igs_ftp
import ppp_gpsppp

if __name__ == "__main__":
    # example processing:
    #station1 = station.mi04
    #station1 = station.mi05
    #station1 = station.mi02
    
    my_stations = [station.mi04, station.mi05, station.mi02, station.pt10, station.ptbb]
    #my_stations = [station.pt10]
    
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=16)  # 4 days ago
    current_dir = os.getcwd()

    ppp_gpsppp.run_multiday( station.mi04, dt, num_days=2, rapid=False, prefixdir=current_dir)

    """
    # run NRCAN PPP for given station and datetime dt
    for s in my_stations:
        ppp_gpsppp.run(s, dt, prefixdir=current_dir)
    """
