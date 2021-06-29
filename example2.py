#
# example file for ppp-tools
# https://github.com/aewallin/ppp-tools
#
import datetime
import os
import matplotlib.pyplot as plt
import time
import numpy
import matplotlib
matplotlib.rcParams['axes.formatter.useoffset'] = False

# import ppp_rtklib
# import ppp_glab
import ppp_gpsppp
import station
import ppp_common

station1 = station.mi04
station2 = station.mi05
products = "rapid"

def read_days( station1, station2, dt_list ):
    current_dir = os.getcwd()
    
    all_t=[]
    all_d=[]
    for dt in dt_list:
        (t_gpspace, d_gpspace) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "gpspace")
        for (t,d) in zip(t_gpspace, d_gpspace):
            all_t.append(t)
            all_d.append(d)
    return (all_t, all_d)
    
dt = datetime.datetime.utcnow()-datetime.timedelta(days=4) # 4 days ago
current_dir = os.getcwd()

day_list = []
#for n in [8, 7, 6, 5, 4, 3]:
for n in [ 9, 8, 7, 6, 5, 4, 3, 2]:
    day_list.append( datetime.datetime.utcnow()-datetime.timedelta(days=n) )

(t45, d45) = read_days( station.mi04, station.mi05, day_list )
(t25, d25) = read_days( station.mi02, station.mi05, day_list )
(t24, d24) = read_days( station.mi02, station.mi04, day_list )

# compute double difference
# (t_glab,d_glab) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "glab")
# (t_rtklib,d_rtklib) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "rtklib")
#(t_gpspace, d_gpspace) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "gpspace")

plt.figure()
plt.title("%s - %s receiver clock, double difference"%(station1.name, station2.name))
#plt.plot(t_glab,d_glab, label="glab")
#plt.plot(t_rtklib,d_rtklib, label="rtklib")
plt.plot(t45, numpy.array(d45), label="4-5 gpspace")
plt.plot(t25, numpy.array(d25), label="2-5 gpspace")
plt.plot(t24, d24, label="2-4 gpspace")

#plt.ylim((-3, 3))
plt.legend(loc="best")
plt.grid()
plt.ylabel("%s - %s / ns" %(station1.name, station2.name))
plt.show()
