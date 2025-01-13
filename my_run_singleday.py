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
    my_stations = [station.mi06local, station.mi05,]
    #my_stations = [station.mi04]

    dt = datetime.datetime.utcnow()-datetime.timedelta(days=4)  # 4 days ago
    dt0 = datetime.datetime(2024,5,31)
    current_dir = os.getcwd()

    #ppp_gpsppp.run_multiday( station.mi04, dt, num_days=2, rapid=False, prefixdir=current_dir, products="IGS")
    #ppp_gpsppp.run_multiday( station.mi05, dt, num_days=2, rapid=True, prefixdir=current_dir)
    #ppp_gpsppp.run_multiday( station.pt10, dt, num_days=2, rapid=True, prefixdir=current_dir)
    
    
    # 2022-02-19    first day of MI06 data with AHM3 as reference
    
    
    # Final results     GPSw/day   RINEX             VTT SR+ data
    # 59635 2022-02-25
    # 59636 2022-02-26  21986
    # 59637 2022-02-27  21990
    # 59638 2022-02-28  21991
    # 59639 2022-03-01
    # 59640 2022-03-02  21993
    # 59641 2022-03-03  21994
    # 59642 2022-03-04  21995      MI060630.22o.gz   0.27         
    # 59643 2022-03-05  21996 (product update 2022-03-21)
    
    #"""
    # run NRCAN PPP for given station and datetime dt
    for n in range(1):
        dt = dt0 + datetime.timedelta(days=n)
        for s in my_stations:
            rapid = False
            #rapid = True
            #if dt-datetime.datetime(2021, 8,20) > datetime.timedelta(days=0):
            #    rapid = True
            print(dt, rapid)
            ppp_gpsppp.run(s, dt, rapid=rapid, prefixdir=current_dir, products="CODE")
        #ppp_glab.run(s, dt, rapid=True, prefixdir=current_dir)
        #ppp_rtklib.run(s, dt, rapid=True, prefixdir=current_dir)
    #"""
