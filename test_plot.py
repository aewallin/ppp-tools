import os
import datetime

import matplotlib.pyplot as plt

import ppp_common
import UTCStation

prefixdir = os.getcwd()
#fname = "results/USNO/usn6.58176.rapid.glab.txt"
#station = UTCStation.usno
dt = datetime.datetime.utcnow() - datetime.timedelta(days=4)
products="rapid"
#program="nrcan"
#r = read_result_file(station, dt, products, program, prefixdir)
#print "read ",len(r), " points"
station1 = UTCStation.usno
station2 = UTCStation.ptb
(t,d) = ppp_common.diff_stations(prefixdir, station1, station2, dt, products, "nrcan")
(t2,d2) = ppp_common.diff_stations(prefixdir, station1, station2, dt, products, "glab")
(t3,d3) = ppp_common.diff_stations(prefixdir, station1, station2, dt, products, "rtklib")

plt.figure()
plt.plot(t,d,label="nrcan")
plt.plot(t2,d2,label="glab")
plt.plot(t3,d3,label="rtklib")

plt.grid()
plt.legend()
plt.show()
