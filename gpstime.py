""" 
  2  A Python implementation of GPS related time conversions. 
  3   
  4  Copyright 2002 by Bud P. Bruegger, Sistema, Italy 
  5  mailto:bud@sistema.it 
  6  http://www.sistema.it 
  7   
  8  Modifications for GPS seconds by Duncan Brown 
  9   
 10  PyUTCFromGpsSeconds added by Ben Johnson 
 11   
 12  This program is free software; you can redistribute it and/or modify it under 
 13  the terms of the GNU Lesser General Public License as published by the Free 
 14  Software Foundation; either version 2 of the License, or (at your option) any 
 15  later version. 
 16   
 17  This program is distributed in the hope that it will be useful, but WITHOUT ANY 
 18  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
 19  PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more 
 20  details. 
 21   
 22  You should have received a copy of the GNU Lesser General Public License along 
 23  with this program; if not, write to the Free Software Foundation, Inc., 59 
 24  Temple Place, Suite 330, Boston, MA  02111-1307  USA 
 25   
 26  GPS Time Utility functions 
 27   
 28  This file contains a Python implementation of GPS related time conversions. 
 29   
 30  The two main functions convert between UTC and GPS time (GPS-week, time of 
 31  week in seconds, GPS-day, time of day in seconds).  The other functions are 
 32  convenience wrappers around these base functions.   
 33   
 34  A good reference for GPS time issues is: 
 35  http://www.oc.nps.navy.mil/~jclynch/timsys.html 
 36   
 37  Note that python time types are represented in seconds since (a platform 
 38  dependent Python) Epoch.  This makes implementation quite straight forward 
 39  as compared to some algorigthms found in the literature and on the web.   
 40  """ 

import time, math 
import datetime

secsInWeek = 604800 
secsInDay = 86400 
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss) 
   
def dayOfWeek(year, month, day):
    "returns day of week: 0=Sun, 1=Mon, .., 6=Sat" 
    hr = 12 #make sure you fall into right day, middle is save 
    t = time.mktime((year, month, day, hr, 0, 0, 0, 0, -1)) 
    pyDow = time.localtime(t)[6] 
    gpsDow = (pyDow + 1) % 7
    return gpsDow
 
def gpsWeek(year, month, day):
    "returns (full) gpsWeek for given date (in UTC)"  
    hr = 12 #make sure you fall into right day, middle is save 
    return gpsFromUTC(year, month, day, hr, 0, 0.0)[0]

def julianDay(year, month, day):
    "returns julian day=day since Jan 1 of year"
    hr = 12 #make sure you fall into right day, middle is save 
    t = time.mktime((year, month, day, hr, 0, 0, 0, 0, -1)) 
    julDay = time.localtime(t)[7] # tm_yday
    return julDay

def dateFromJulian( year, julian_day ):
    t0 = datetime.datetime( year, 1, 1 ) # first day of year
    t0 = t0 + datetime.timedelta( days=julian_day-1 )
    return t0

def mkUTC(year, month, day, hour, min, sec):
    "similar to python's mktime but for utc" 
    spec = [year, month, day, hour, min, int(sec)] + [0, 0, 0] 
    utc = time.mktime(spec) - time.timezone 
    return utc

def ymdhmsFromPyUTC(pyUTC):
    "returns tuple from a python time value in UTC" 
    ymdhmsXXX = time.gmtime(pyUTC) 
    return ymdhmsXXX[:-3]

def wtFromUTCpy(pyUTC, leapSecs=14):
    """convenience function: 87 allows to use python UTC times and 
    returns only week and tow""" 
    ymdhms = ymdhmsFromPyUTC(pyUTC) 
    wSowDSoD = gpsFromUTC(*ymdhms + (leapSecs,)) 
    return wSowDSoD[0:2]

def gpsFromUTC(year, month, day, hour, min, sec, leapSecs=14):
    """converts UTC to: gpsWeek, secsOfWeek, gpsDay, secsOfDay 95 96 
    a good reference is: http://www.oc.nps.navy.mil/~jclynch/timsys.html 97 98 
    This is based on the following facts (see reference above): 99 100 
    GPS time is basically measured in (atomic) seconds since 101 
    January 6, 1980, 00:00:00.0 (the GPS Epoch) 102 103 
    The GPS week starts on Saturday midnight (Sunday morning), and runs 104 
    for 604800 seconds. 105 106 
    Currently, GPS time is 13 seconds ahead of UTC (see above reference). 107 
    While GPS SVs transmit this difference and the date when another leap 108 
    second takes effect, the use of leap seconds cannot be predicted. This 109 
    routine is precise until the next leap second is introduced and has to be 110 
    updated after that. 111 112 
    SOW = Seconds of Week 113 
    SOD = Seconds of Day 114 115 N
    ote: Python represents time in integer seconds, fractions are lost!!! 116 
    """  
    secFract = sec % 1 
    epochTuple = gpsEpoch + (-1, -1, 0) 
    t0 = time.mktime(epochTuple) 
    t = time.mktime((year, month, day, hour, min, int(sec), -1, -1, 0)) 
    # Note: time.mktime strictly works in localtime and to yield UTC, it should be 122 
    # corrected with time.timezone 123 
    # However, since we use the difference, this correction is unnecessary. 124 
    # Warning: trouble if daylight savings flag is set to -1 or 1 !!! 125 
    t = t + leapSecs 
    tdiff = t - t0 
    gpsSOW = (tdiff % secsInWeek) + secFract 
    gpsWeek = int(math.floor(tdiff/secsInWeek)) 
    gpsDay = int(math.floor(gpsSOW/secsInDay)) 
    gpsSOD = (gpsSOW % secsInDay) 
    return (gpsWeek, gpsSOW, gpsDay, gpsSOD)

def UTCFromGps(gpsWeek, SOW, leapSecs=14):
    """converts gps week and seconds to UTC 136 137 
    see comments of inverse function! 138 139 
    SOW = seconds of week 140 
    gpsWeek is the full number (not modulo 1024) 141 
    """ 
    secFract = SOW % 1 
    epochTuple = gpsEpoch + (-1, -1, 0) 
    t0 = time.mktime(epochTuple) - time.timezone #mktime is localtime, correct for UTC 145 
    tdiff = (gpsWeek * secsInWeek) + SOW - leapSecs 
    t = t0 + tdiff 
    (year, month, day, hh, mm, ss, dayOfWeek, julianDay, daylightsaving) = time.gmtime(t) 
    #use gmtime since localtime does not allow to switch off daylighsavings correction!!! 149 
    return (year, month, day, hh, mm, ss + secFract)

def GpsSecondsFromPyUTC( pyUTC, leapSecs=14 ):
    """converts the python epoch to gps seconds 153 154 
    pyEpoch = the python epoch from time.time() 155 
    """ 
    t = t=gpsFromUTC(*ymdhmsFromPyUTC( pyUTC )) 
    return int(t[0] * 60 * 60 * 24 * 7 + t[1])

def PyUTCFromGpsSeconds(gpsseconds):
    """converts gps seconds to the 161 python epoch. 
    That is, the time 162 that would be returned from time.time() 163 
    at gpsseconds. 164 
    """ 
    pyUTC

#===== Tests  ========================================= 

def testTimeStuff():
    print("-"*20) 
    print() 
    print("The GPS Epoch when everything began (1980, 1, 6, 0, 0, 0, leapSecs=0)") 
    (w, sow, d, sod) = gpsFromUTC(1980, 1, 6, 0, 0, 0, leapSecs=0) 
    print("**** week: %s, sow: %s, day: %s, sod: %s" % (w, sow, d, sod)) 
    print(" and hopefully back:") 
    print("**** %s, %s, %s, %s, %s, %s\n" % UTCFromGps(w, sow, leapSecs=0))
    print("The time of first Rollover of GPS week (1999, 8, 21, 23, 59, 47)") 
    (w, sow, d, sod) = gpsFromUTC(1999, 8, 21, 23, 59, 47) 
    print("**** week: %s, sow: %s, day: %s, sod: %s" % (w, sow, d, sod)) 
    print(" and hopefully back:") 
    print("**** %s, %s, %s, %s, %s, %s\n" % UTCFromGps(w, sow, leapSecs=14))
    
    print("Today is GPS week 1186, day 3, seems to run ok (2002, 10, 2, 12, 6, 13.56)") 
    (w, sow, d, sod) = gpsFromUTC(2002, 10, 2, 12, 6, 13.56) 
    print("**** week: %s, sow: %s, day: %s, sod: %s" % (w, sow, d, sod)) 
    print(" and hopefully back:") 
    print("**** %s, %s, %s, %s, %s, %s\n" % UTCFromGps(w, sow))

def testJulD():
    print("testJulD()")
    print('2002, 10, 11 -> 284 ==??== ', julianDay(2002, 10, 11))
    print(" ")
    
def testGpsWeek():
    print("testGpsWeek()")
    print('2002, 10, 11 -> 1187 ==??== ', gpsWeek(2002, 10, 11))
    print(" ")
    
def testDayOfWeek():
    print("testDayOfWeek()")
    print('2002, 10, 12 -> 6 ==??== dayOfWeek = ', dayOfWeek(2002, 10, 12)) 
    print('2002, 10, 6 -> 0 ==??== dayOfWeek =', dayOfWeek(2002, 10, 6))
    print(" ")

def testNow():
    now = datetime.datetime.now() - datetime.timedelta(days=2)
    #now = datetime.datetime(2014,2,23 ) # doy 54
    print("testNow()")
    print(" now = ", now)
    print(" Julian day      = ", julianDay( now.year, now.month, now.day ))
    print(" GPS week        = ", gpsWeek( now.year, now.month, now.day)) 
    print(" GPS day of week = ", dayOfWeek( now.year, now.month, now.day)) 
    print(" date from Julian= ", dateFromJulian( now.year, julianDay(now.year, now.month, now.day) ))
    print('2002, 10, 6 -> 0 ==??== dayOfWeek =', dayOfWeek(2014, 0o1, 9))
    
def testPyUtilties():
    print("testDayOfWeek()")
    ymdhms = (2014, 1, 9, 8, 34, 12.3) 
    print("testing for: ", ymdhms) 
    pyUtc = mkUTC(*ymdhms) 
    back = ymdhmsFromPyUTC(pyUtc) 
    print("yields : ", back) 
    #*********************** !!!!!!!! 
    #assert(ymdhms == back) 208 
    #! TODO: this works only with int seconds!!! fix!!! 
    (w, t) = wtFromUTCpy(pyUtc) 
    print("week and time: ", (w,t))
    print(" ")

#===== Main ========================================= 
if __name__ == "__main__": 
    pass 
    testTimeStuff() 
    testGpsWeek() 
    testJulD() 
    testDayOfWeek() 
    testPyUtilties() 
    testNow()
