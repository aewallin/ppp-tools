import math

import ftp_tools
import jdutil 
# common classes and functions for all ppp-implementations.
# this file is part of ppp-tools, https://github.com/aewallin/ppp-tools


def write_result_file( ppp_result ,  preamble="" , rapid=True, tag="ppp", prefixdir=""):
    """ write the ppp result out to a text file """
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

class PPP_Result():
    """ this class stores the result of a ppp run """
    def __init__(self):
        self.observations=[]
        self.station=""
        
    def append(self,p):
        self.observations.append(p)
    def reverse(self):
        self.observations.reverse()
        
class PPP_Point():
    """ a single point obsevation """
    def __init__(self,epoch, lat, lon, h, clock, ztd):
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
