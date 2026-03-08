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
import ppp_glab
import ppp_rtklib

if __name__ == "__main__":
    # example processing:
    #station1 = station.mi04
    #station1 = station.mi05
    #station1 = station.mi02
    #my_stations = [station.mi04, station.mi05, station.mi02, station.mi06local]
    #my_stations = [station.mi06local, station.mi05,]
    my_stations = [station.mi05]

    dt = datetime.datetime.utcnow()-datetime.timedelta(days=4)  # 4 days ago
    dt0 = datetime.datetime(2026,2,1)
    current_dir = os.getcwd()


    # run NRCAN PPP for given station and datetime dt
    for n in range(1):
        dt = dt0 + datetime.timedelta(days=n)
        for s in my_stations:
            rapid = False
            print(dt, rapid)
            ppp_gpsppp.run(s, dt, rapid=rapid, prefixdir=current_dir, products="CODE")
        #ppp_glab.run(s, dt, rapid=True, prefixdir=current_dir)
        #ppp_rtklib.run(s, dt, rapid=True, prefixdir=current_dir)
