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
    
    my_stations = [station.mi06, station.mi04, station.mi05, station.mi02, station.pt10, station.ptbb]
    #my_stations = [station.mi05, station.mi02, station.pt10, station.ptbb]
    my_stations = [station.mi05]
    
    dt = datetime.datetime.utcnow()-datetime.timedelta(days=32)  # end of run is N days ago
    current_dir = os.getcwd()

    days = 20
    for s in my_stations:
        ppp_gpsppp.run_multiday( s, dt, num_days=days, rapid=False, prefixdir=current_dir, products="IGS")
    #ppp_gpsppp.run_multiday( station.mi05, dt, num_days=2, rapid=True, prefixdir=current_dir)
    #ppp_gpsppp.run_multiday( station.pt10, dt, num_days=2, rapid=True, prefixdir=current_dir)
    
    """
    # run NRCAN PPP for given station and datetime dt
    for s in my_stations:
        ppp_gpsppp.run(s, dt, rapid=True, prefixdir=current_dir)
        #ppp_glab.run(s, dt, rapid=True, prefixdir=current_dir)
        #ppp_rtklib.run(s, dt, rapid=True, prefixdir=current_dir)
    """
