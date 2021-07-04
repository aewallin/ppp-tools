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

"""
    plot result of multi-day run
"""

# import ppp_rtklib
# import ppp_glab
import ppp_gpsppp
import station
import ppp_common
import jdutil

station1 = station.mi02
station1 = station.mi04
station2 = station.mi05
# mi05 - ptbb: +3.96e-16    4.13-16
# mi05 - pt10: +2.62e-16    4.095e-16
#    
# mi05 - mi04:  5.43e-16

products = "rapid"
program = "gpspace"
current_dir = os.getcwd()

    
dt = datetime.datetime.utcnow()-datetime.timedelta(days=3) # 4 days ago
current_dir = os.getcwd()
num_days = 12

#day_list = []
#for n in [8, 7, 6, 5, 4, 3]:
#for n in [ 10, 9, 8, 7, 6, 5, 4, 3, 2]:
#    day_list.append( datetime.datetime.utcnow()-datetime.timedelta(days=n) )
r1 = ppp_common.read_result_file(station1, dt, products, program, current_dir, num_days=num_days)
r2 = ppp_common.read_result_file(station2, dt, products, program, current_dir, num_days=num_days)
    
(t45, d45) = ppp_common.diff_stations( current_dir, station1, station2, dt, products, program, num_days=num_days)
mjd = jdutil.dt2mjd(t45)
d45 = numpy.array(d45)
#(t25, d25) = read_days( station.mi02, station.mi05, day_list )
#(t24, d24) = read_days( station.mi02, station.mi04, day_list )

# compute double difference
# (t_glab,d_glab) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "glab")
# (t_rtklib,d_rtklib) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "rtklib")
#(t_gpspace, d_gpspace) = ppp_common.diff_stations(current_dir, station1, station2, dt, products, "gpspace")

plt.figure()
plt.subplot(3,1,1)
plt.plot( jdutil.dt2mjd( [x.epoch for x in r1.observations]), [x.clock for x in r1.observations], label="%s" % (station1.name))
plt.ylabel('%s / ns' % station1.name)
plt.grid()

plt.subplot(3,1,2)
plt.plot( jdutil.dt2mjd( [x.epoch for x in r2.observations]), [x.clock for x in r2.observations], label="%s" % (station2.name))
plt.ylabel('%s / ns' % station2.name)
plt.grid()

plt.subplot(3,1,3)
plt.title("%s - %s receiver clock, double difference"%(station1.name, station2.name))
#plt.plot(t_glab,d_glab, label="glab")
#plt.plot(t_rtklib,d_rtklib, label="rtklib")
plt.plot(mjd, numpy.array(d45), label="%s -%s" % (station1.name, station2.name))

p = numpy.polyfit(mjd, d45, 1)
rate = p[0]
y = -1e-9*rate/(24.0*3600.0)
plt.plot(mjd, numpy.polyval(p, mjd),'r--',label='fit %.3f ns/day = %.6g'%(rate, y))

#plt.plot(t25, numpy.array(d25), label="2-5 gpspace")
#plt.plot(t24, d24, label="2-4 gpspace")

#plt.ylim((-3, 3))
plt.legend(loc="best")
plt.grid()
plt.ylabel("%s - %s / ns" %(station1.name, station2.name))
plt.show()
