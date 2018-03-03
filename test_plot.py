import os
import datetime
import numpy
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

def parse(p):
    lat = [x.lat for x in p.observations]
    lon = [x.lon for x in p.observations]
    h = [x.height for x in p.observations]
    ztd = [x.ztd for x in p.observations]
    ns = [x.clock for x in p.observations]
    return lat, lon, h, ztd, ns
    
p1 = ppp_common.read_result_file(station2, dt, products, "nrcan", prefixdir)
p2 = ppp_common.read_result_file(station2, dt, products, "glab", prefixdir)
p3 = ppp_common.read_result_file(station2, dt, products, "rtklib", prefixdir)

lat1, lon1, h1, ztd1, ns1=parse(p1)
lat2, lon2, h2, ztd2, ns2=parse(p2)
lat3, lon3, h3, ztd3, ns3=parse(p3)
print lat1[0], lat2[0], lat3[0]
"""
plt.figure()
plt.plot( lat1)
plt.plot( lat2)
plt.plot( lat3)
plt.gca().ticklabel_format(useOffset=False)

plt.figure()
plt.plot( lon1)
plt.plot( lon2)
plt.plot( lon3)
plt.gca().ticklabel_format(useOffset=False)

plt.figure()
plt.plot( h1)
plt.plot( h2)
plt.plot( h3)
plt.gca().ticklabel_format(useOffset=False)

plt.figure()
plt.plot( ztd1)
plt.plot( ztd2)
plt.plot( ztd3)
plt.gca().ticklabel_format(useOffset=False)

plt.figure()
plt.plot( ns1)
plt.plot( ns2)
plt.plot( ns3)
plt.gca().ticklabel_format(useOffset=False)
"""
#plt.show()


(tt1, ns1, z1) = ppp_common.read_time(station1, dt, products, "nrcan", prefixdir)
(tt2, ns2, z2) = ppp_common.read_time(station1, dt, products, "glab", prefixdir)
(tt3, ns3, z3) = ppp_common.read_time(station1, dt, products, "rtklib", prefixdir)
"""
plt.figure()
plt.plot(tt1,ns1,label="nrcan")
plt.plot(tt2,ns2,label="glab")
plt.plot(tt3,ns3,label="rtklib")

plt.figure()
plt.plot(tt1,z1,label="nrcan")
plt.plot(tt2,z2,label="glab")
plt.plot(tt3,z3,label="rtklib")
"""

(tt1, ns1, z1) = ppp_common.read_time(station2, dt, products, "nrcan", prefixdir)
(tt2, ns2, z2) = ppp_common.read_time(station2, dt, products, "glab", prefixdir)
(tt3, ns3, z3) = ppp_common.read_time(station2, dt, products, "rtklib", prefixdir)

"""
plt.figure()
plt.plot(tt1,ns1,label="nrcan")
plt.plot(tt2,ns2,label="glab")
plt.plot(tt3,ns3,label="rtklib")

plt.figure()
plt.plot(tt1,z1,label="nrcan")
plt.plot(tt2,z2,label="glab")
plt.plot(tt3,z3,label="rtklib")
"""

plt.figure()
plt.plot(t,d,label="nrcan")
plt.plot(t2,d2,label="glab")
plt.plot(t3,d3,label="rtklib")

plt.grid()
plt.legend()

plt.figure()
plt.plot(t,d-numpy.mean(d),label="nrcan")
plt.plot(t2,d2-numpy.mean(d2),label="glab")
plt.plot(t3,d3-numpy.mean(d3),label="rtklib")

plt.grid()
plt.legend()
plt.show()
