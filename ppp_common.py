"""
    this file is part of ppp-tools, https://github.com/aewallin/ppp-tools

    Licensed under GPLv2
    Anders Wallin 2018

    common classes and functions for all ppp-implementations.
"""
import math
import os
import datetime
import UTCStation

import ftp_tools
import jdutil 

def diff_stations(prefixdir, station1, station2, dt, products, program):
    """
    calculate clock difference between two stations
    Station1 PPP result is receive_clock_offset = IGST(rapid/final) - Station1
    Station2 PPP result is receive_clock_offset = IGST(rapid/final) - Station2
    
    Double difference Station1-Station2 gives:
    (IGST(rapid/final) - Station1) - (IGST(rapid/final) - Station2)
    =
    Station2 - Station1
    """
    year = dt.timetuple().tm_year
    doy = dt.timetuple().tm_yday
    mjd = jdutil.datetime_to_mjd(dt)
    # output filename
    diff_dir = prefixdir + "/results/diff/"
    ftp_tools.check_dir(diff_dir)
    fname = diff_dir + "%s.diff.%s.%d.%s.%s.txt" % ( station1.receiver , station2.receiver, mjd, products, program )
    if os.path.exists(fname):
        print fname," already exists - nothing to do."
        return # result already exists, nothing to do
    
    r1 = read_result_file(station1, dt, products, program, prefixdir)
    r2 = read_result_file(station2, dt, products, program, prefixdir)
    print "diff station1 ", len(r1)
    print "diff station2 ", len(r2)
    #read_result_file( )
    #2,x2) = bipm_ftp.COD_read_day(prefixdir, station2, year, doy, rapid)
    #print len(t1), len(t2)
    
    
    (t_diff, clock_diff) = diff(r1, r2)
    #print len(td), len(d)
    #print d
    #print numpy.median(d)
    #(td2,d2) = mad.remove_timeseries_outliers(td,d)
    # write_diff_file(prefixdir, station1, station2, year, doy, td2, d2)
    # print len(td2)
    return (t_diff, clock_diff)

def diff(result1, result2):
    """
    calculate receiver clock double-difference of two PPP_Result objects
    
    """
    # choose the longer t-vector for the outer loop!
    td=[]
    d=[]
    t1 = [x.epoch for x in result1.observations]
    ns1 = [x.clock for x in result1.observations]
    t2 = [x.epoch for x in result2.observations]
    ns2 = [x.clock for x in result2.observations]
    if (len(t1)>=len(t2)):
        for t in t1:
            if t in t2:
                idx1 = t1.index(t)
                idx2 = t2.index(t)
                d.append( ns1[idx1] - ns2[idx2] )
                td.append(t)
    else:
        for t in t2: # t2 is longer than t1
            if t in t1:
                idx1 = t1.index(t)
                idx2 = t2.index(t)
                if idx1<0 or idx1>len(ns1)-1: # an error!
                    print t, idx1, len(ns1), t1.index(t), t in t1
                    print t, idx2, len(ns2), t2.index(t), t in t2
                d.append( ns1[idx1]-ns2[idx2] )
                td.append(t)
    assert( len(td) == len(d) )
    return (td,d)

def write_result_file( ppp_result ,  preamble="" , rapid=True, tag="ppp", prefixdir=""):
    """ 
    write a PPP_Result object out to a text file 
    """
    ftp_tools.check_dir(prefixdir + "/results")
    ftp_tools.check_dir(prefixdir + "/results/" + ppp_result.station.name)
    first_obs = ppp_result.observations[0]
    first_obs_mjd = int(jdutil.datetime_to_mjd( first_obs.epoch ) )
    rapid_final = "final"
    if rapid:
        rapid_final = "rapid"
    result_file = ppp_result.station.receiver +"." + str(first_obs_mjd) + "." + rapid_final + "." + tag + ".txt"
    
    outfile = prefixdir + "/results/" + ppp_result.station.name + "/" + result_file
    with open(outfile,'w') as f:
        datastring = "# " + result_file + " \n"
        f.write(datastring)
        for line in preamble.split('\n'):
            f.write( "# %s\n" % line)

        f.write(PPP_Point.column_labels())
        for point in ppp_result.observations:
            f.write(str(point) + "\n")

    print " wrote results to ", outfile

def read_result_file(station, dt, products, program, prefixdir):
    """
    read text-file and return PPP_Result
    """
    mjd = jdutil.datetime_to_mjd(dt)
    fname = "%s.%d.%s.%s.txt" % (station.receiver, mjd, products, program)
    r=PPP_Result()
    with open(prefixdir+"/results/" + station.name + "/" + fname) as f:
        for line in f:
            if line.startswith("#"):
                pass
            else:
                line = line.split()
                # 0     1       2   3       4   5   6           7           8           9           10
                # Year	Month	Day	Hour	Min	Sec	Lat(deg)	Lon(deg)	Height(m)	Clock(ns)	ZTD(m)
                
                epoch = datetime.datetime( int(line[0]), int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]) )
                lat = float(line[6])
                lon = float(line[7])
                height = float(line[8])
                clock = float(line[9])
                ztd = float(line[10])
                r.append(PPP_Point(epoch, lat, lon, height, clock, ztd))
    return r
    
class PPP_Result():
    """ 
    this class stores the result of a ppp run 
    
    it consists of a list of observations, each a PPP_Point
    
    """
    def __init__(self):
        self.observations=[]
        self.station=""
        
    def append(self,p):
        self.observations.append(p)
    def reverse(self):
        self.observations.reverse()
    def __len__(self):
        return len(self.observations)
        
class PPP_Point():
    """ 
    a single point obsevation 
    """
    def __init__(self, epoch, lat, lon, h, clock, ztd):
        self.epoch = epoch # epoch of observation, as a datetime object
        self.lat = lat     # latitude in float degrees
        self.lon = lon     # longitude in float degrees
        self.height = h    # height in meters
        self.clock = clock # receiver clock in nanoseconds
        self.ztd = ztd     # zenith tropospheric delay in meters
    
    @staticmethod
    def column_labels():
        labels = "# Year\tMonth\tDay\tHour\tMin\tSec\tLat(deg)\tLon(deg)\tHeight(m)\tClock(ns)\tZTD(m)\n"
        return labels
        
    def __str__(self): # string representation
         return "%d\t%d\t%d\t%d\t%d\t%d\t%0.6f\t%0.6f\t%0.3f\t\t%0.3f\t\t%0.4f" % ( self.epoch.year, self.epoch.month, self.epoch.day, 
                                                                   self.epoch.hour, self.epoch.minute, self.epoch.second, 
                                                                   self.lat, self.lon, self.height, self.clock, self.ztd  )


def xyz2lla(x,y,z):
    """ 
        convert from ECEF (x,y,z) to WGS (lat,lon,height) 
    
        http://www.nicolargo.com/dev/xyz2lla/
        Convert XYZ coordinates to cartesien LLA (Latitude/Longitude/Altitude)
        Alcatel Alenia Space - Nicolas Hennion
        Version 0.1
        Python version translation by John Villalovos
    """
    # Constants (WGS ellipsoid)
    a = 6378137
    e = 8.1819190842622e-2
    # Calculation
    b =  math.sqrt(pow(a,2) * (1-pow(e,2)))
    ep = math.sqrt((pow(a,2)-pow(b,2))/pow(b,2))
    p =  math.sqrt(pow(x,2)+pow(y,2))
    th = math.atan2(a*z, b*p)
    lon = math.atan2(y, x)
    lat = math.atan2((z+ep*ep*b*pow(math.sin(th),3)), (p-e*e*a*pow(math.cos(th),3)))
    n = a/math.sqrt(1-e*e*pow(math.sin(lat),2))
    alt = p/math.cos(lat)-n
    lat = (lat*180)/math.pi
    lon = (lon*180)/math.pi
    return (lat, lon, alt)

if __name__=="__main__":
    prefixdir = os.getcwd()
    #fname = "results/USNO/usn6.58176.rapid.glab.txt"
    station = UTCStation.usno
    dt = datetime.datetime.utcnow() - datetime.timedelta(days=4)
    products="rapid"
    program="nrcan"
    r = read_result_file(station, dt, products, program, prefixdir)
    print "read ",len(r), " points"
    station1 = UTCStation.usno
    station2 = UTCStation.ptb
    (t,d) = diff_stations(prefixdir, station1, station2, dt, products, program)
    print d
