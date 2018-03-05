import datetime
import os
import matplotlib.pyplot as plt
import time
import matplotlib
matplotlib.rcParams['axes.formatter.useoffset'] = False

import ppp_rtklib
import ppp_glab
import ppp_nrcan
import station
import ppp_common

# define stations
station1 = station.ptb
station2 = station.mikes
products = "rapid" # IGS product type

# define day for analysis:
dt = datetime.datetime.utcnow()-datetime.timedelta(days=5)
current_dir = os.getcwd()

t0 = time.time()
# run gLAB PPP
ppp_glab.run(station1, dt, prefixdir=current_dir)
ppp_glab.run(station2, dt, prefixdir=current_dir)
# run RTKLIB
ppp_rtklib.run(station1, dt, prefixdir=current_dir)
ppp_rtklib.run(station2, dt, prefixdir=current_dir)
# run nrcan
ppp_nrcan.run(station1, dt, prefixdir=current_dir)
ppp_nrcan.run(station2, dt, prefixdir=current_dir)
runtime = time.time()-t0
print "ppp run in ", runtime, " seconds"


# read results from result-files
s1_glab = ppp_common.read_result_file(station1, dt, products, "glab", current_dir)
s1_rtklib = ppp_common.read_result_file(station1, dt, products, "rtklib", current_dir)
s1_nrcan = ppp_common.read_result_file(station1, dt, products, "nrcan", current_dir)

s2_glab = ppp_common.read_result_file(station2, dt, products, "glab", current_dir)
s2_rtklib = ppp_common.read_result_file(station2, dt, products, "rtklib", current_dir)
s2_nrcan = ppp_common.read_result_file(station2, dt, products, "nrcan", current_dir)


# plot lat/lon/heigh/ztd results
plt.figure()

plt.subplot(2,2,1)
plt.title(station1.name)

plt.plot( s1_glab.epoch(), s1_glab.lat(), label='glab')
plt.plot( s1_rtklib.epoch(), s1_rtklib.lat(), label='rtklib')
plt.plot( s1_nrcan.epoch(), s1_nrcan.lat(), label='nrcan')
plt.legend(loc='best')
plt.ylabel('lat / degrees')
plt.grid()
plt.legend(loc='best')

plt.subplot(2,2,2)
plt.plot( s1_glab.epoch(), s1_glab.lon(), label='glab')
plt.plot( s1_rtklib.epoch(), s1_rtklib.lon(), label='rtklib')
plt.plot( s1_nrcan.epoch(), s1_nrcan.lon(), label='nrcan')
plt.ylabel('lon / degrees')
plt.grid()
plt.legend(loc='best')

plt.subplot(2,2,3)
plt.plot( s1_glab.epoch(), s1_glab.height(), label='glab')
plt.plot( s1_rtklib.epoch(), s1_rtklib.height(), label='rtklib')
plt.plot( s1_nrcan.epoch(), s1_nrcan.height(), label='nrcan')
plt.ylabel('height / m')
plt.grid()
plt.legend(loc='best')

plt.subplot(2,2,4)
plt.plot( s1_glab.epoch(), s1_glab.clock(), label='glab')
plt.plot( s1_rtklib.epoch(), s1_rtklib.clock(), label='rtklib')
plt.plot( s1_nrcan.epoch(), s1_nrcan.clock(), label='nrcan')
plt.ylabel('clock / ns')
plt.ylim((473,476))
plt.grid()
plt.legend(loc='best')

plt.figure()

plt.subplot(2,2,1)
plt.title(station2.name)
plt.plot( s2_glab.epoch(), s2_glab.lat(), label='glab')
plt.plot( s2_rtklib.epoch(), s2_rtklib.lat(), label='rtklib')
plt.plot( s2_nrcan.epoch(), s2_nrcan.lat(), label='nrcan')
plt.legend(loc='best')
plt.ylabel('lat / degrees')
plt.grid()
plt.legend(loc='best')

plt.subplot(2,2,2)
plt.plot( s2_glab.epoch(), s2_glab.lon(), label='glab')
plt.plot( s2_rtklib.epoch(), s2_rtklib.lon(), label='rtklib')
plt.plot( s2_nrcan.epoch(), s2_nrcan.lon(), label='nrcan')
plt.ylabel('lon / degrees')
plt.grid()
plt.legend(loc='best')

plt.subplot(2,2,3)
plt.plot( s2_glab.epoch(), s2_glab.height(), label='glab')
plt.plot( s2_rtklib.epoch(), s2_rtklib.height(), label='rtklib')
plt.plot( s2_nrcan.epoch(), s2_nrcan.height(), label='nrcan')
plt.ylabel('height / m')
plt.grid()
plt.legend(loc='best')

plt.subplot(2,2,4)
plt.plot( s2_glab.epoch(), s2_glab.clock(), label='glab')
plt.plot( s2_rtklib.epoch(), s2_rtklib.clock(), label='rtklib')
plt.plot( s2_nrcan.epoch(), s2_nrcan.clock(), label='nrcan')
plt.ylabel('clock / ns')
#plt.ylim((473,476))
plt.grid()
plt.legend(loc='best')


# compute double difference
(t_glab,d_glab) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "glab")
(t_rtklib,d_rtklib) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "rtklib")
(t_nrcan,d_nrcan) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "nrcan")

plt.figure()
plt.title("%s - %s receiver clock, double difference"%(station1.name, station2.name))
plt.plot(t_glab,d_glab, label="glab")
plt.plot(t_rtklib,d_rtklib, label="rtklib")
plt.plot(t_nrcan,d_nrcan, label="nrcan")
plt.ylim((463,473))
plt.legend(loc="best")
plt.grid()
plt.ylabel("%s - %s / ns" %(station1.name, station2.name))
plt.show()
