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
    
    #my_stations = [station.mi06, station.mi04, station.mi05, station.mi02, station.pt10, station.ptbb]
    #my_stations = [station.mi05, station.mi02, station.pt10, station.ptbb]
    #my_stations = [station.mi04, station.mi05, station.mi06]
    #my_stations = [station.pt09, station.mi04, station.mi05,  station.ptbb]
    #my_stations = [station.mi05, station.mi06local ]
    #my_stations = [station.mi06local ]
    #my_stations = [station.mi04]
    my_stations = [station.pt09]
    
    # 2024 DOY 69 = 2024-03-09
    # 2024 DOY 107 = 2024-04-16, duration 39 days
    
    # ublox gnss comparison, first interval (MIKES)
    # DOY
    # 136 2024-05-15
    # 137 -05-16
    # 138 -05-17
    # 139 -05-18
    # 140 2024-05-19
    # t = datetime.datetime(2024,5,15)+datetime.timedelta(days=4)
    # days = 5 # length of run in days
    
        
    # ublox 2nd interval, (UBLOX)
    # 
    # 143  2024-05-22
    # 144  2024-05-23
    # 145  2024-05-24
    # 146  2024-05-25
    # 147  2024-05-26
    # 148  2024-05-27
    # 149  2024-05-28
    # 150  2024-05-29
    # dt = datetime.datetime(2024,5,22)+datetime.timedelta(days=7)
    # days = 8 # length of run in days
    
    # ublox 3rd interval at MIKES
    # DOY
    # 152 2024-05-31
    # 153 2024-06-01
    # 154 2024-06-02
    # 155 2024-06-03
    # 156 2024-06-04
    # dt = datetime.datetime(2024,5,31)+datetime.timedelta(days=4)
    # days = 5 
    
    #dt = datetime.datetime.utcnow()-datetime.timedelta(days=17)  # end of run is N days ago
    #dt = datetime.datetime(2024,3,9)+datetime.timedelta(days=38)
    days = 2 # length of run in days
    dt = datetime.datetime(2024,6,30)+datetime.timedelta(days=days)
    print(dt)
    current_dir = os.getcwd()
    
    # MI06 data starts 179 (partial day). DOY=180 is full day
    # on 2021-08-16 32-days back is DOY 195, MJD 59410
    # 47 / 2 -> end on DOY 181
    # 37 / 10 -> DOY 182 -> 191
    # 27 / 10 -> DOY 192 -> 201
    # 17 / 10 -> DOY 202 -> 211
    # 17 / 2  -> DOY 210 -> 211 ?
    # 15 /  2 -> DOY 212 -> 213 (no final IGS products?)
    # 15 /  2 -> DOY 211 -> 212 (no IGS products?)
    # 17 / 32 -> DOY 180 -> 211
    
    # 5-day run
    # start 149
    # stop  153
    
    # ( on 2021-08-16 latest file is DOY 227 = 2021-08-15 )
    # large jump on 59414 2021-07-19
    
    #days = 39 # length of run in days
    
    #days = 8 # length of run in days
    
    for s in my_stations:
        #ppp_gpsppp.run_multiday( s, dt, num_days=days, rapid=False, prefixdir=current_dir, products="IGS")
        ppp_gpsppp.run_multiday( s, dt, num_days=days, rapid=False, prefixdir=current_dir, products="CODE")
    #ppp_gpsppp.run_multiday( station.mi05, dt, num_days=2, rapid=True, prefixdir=current_dir)
    #ppp_gpsppp.run_multiday( station.pt10, dt, num_days=2, rapid=True, prefixdir=current_dir)
    
    """
    # run NRCAN PPP for given station and datetime dt
    for s in my_stations:
        ppp_gpsppp.run(s, dt, rapid=True, prefixdir=current_dir)
        #ppp_glab.run(s, dt, rapid=True, prefixdir=current_dir)
        #ppp_rtklib.run(s, dt, rapid=True, prefixdir=current_dir)
    """
