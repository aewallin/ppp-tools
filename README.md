# ppp-tools

This is a collection of python scripts for GPS-Precise Point Positioning 
post-processing of RINEX files. 
GPS-PPP solutions can be found with the following software packages: 
* rtklib, http://www.rtklib.com/
* ESA gLab, 5.1.3 released 2018-01 http://gage.upc.edu/gLAB
* NRCan gpsppp (CSRS-PPP)

In addition to the GPS-PPP software some utilities may be required:
* Teqc, for concatenating many 1-day RINEX files into multi-day files,  https://www.unavco.org/software/data-processing/teqc/teqc.html, install it to e.g. /usr/local/bin, and verify with "$ teqc -version" that it is working.
as of 2018 March the latest version is "2018Jan11"
* RNXCMP, for decompressing Hatanaka compressed RINEX files, http://terras.gsi.go.jp/ja/crx2rnx.html, install to e.g. /usr/local/bin and verify that CRX2RNX is working with "$ CRX2RNX -h".
As of 2018 March the latest version is 4.0.7.

## Running PPP

The steps for PPP-processing are roughly:

1. Download RINEX files (from e.g. BIPM or other ftp-server)
2. Optionally pre-process RINEX files (i.e. decompress Hatanaka-files, and/or assemble daily files into longer batch)
3. Download SP3 orbit and CLK clock files (from e.g. CODE or other IGS datacenter)
4. Run PPP-algorthm
5. Post-process and visualize the results

## Post-Processing PPP results

Post-processing may include:
* Calculation of double-differences for time-transfer purposes, e.g.  (StationA - IGS) - (StationB - IGS) = StationA - StationB. 
* Some UTC-laboratories submit both a RINEX file and an "LZ" file with the offset between the RINEX receiver clock and the UTC-realization. The PPP receiver-clock result should be modified using the LZ file.
* Plotting using matplotlib
* Calculation of Allan deviations or other statistics (using e.g. allantools)
* Comparison to UTC(k)-UTC numbers published by BIPM monthly in Circular-T, or to Rapid-UTC published weekly.

## Folders

The scripts store input and output files under the main folder:
* 'stations' stores RINEX and LZ files from receiver stations
* 'products' stores clock, ephemeris/orbit, and ERP files from IGS datacenters
* 'common' has common files
* 'results' stores the output results of PPP processing
* 'UTC' has Circular-T data from the BIPM ftp site.
* 'UTCr' has rapid-UTC data from the BIPM ftp site.
* 'doc' has documentation
* 'temp' is used as a temporary directory for gps-ppp calculations

## ESA gLAB installation

* dowload package from http://gage.upc.edu/gLAB
* build binary "gLAB_linux" with "make"
* test that it works "$ ./gLAB_linux -help"
* move the binary to e.g. /usr/local/bin

## NRCan gpsppp Installation

The gfortran package is required on Ubuntu. NRCAN gpsppp is compiled with

Dist34613b/source/$ gfortran -o gpsppp *.f

The resulting binary can be placed in e.g. /usr/local/bin

## RTKLib installation

* clone from https://github.com/tomojitakasu/RTKLIB
* run "make" in RTKLIB/app/rnx2rtkp/gcc
* move the binary "rnx2rtkp" to e.g. /usr/local/bin
* test with "rnx2rtkp -help"
