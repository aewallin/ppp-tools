# ppp-tools

This is a collection of python scripts for GPS-Precise Point Positioning 
post-processing of RINEX files. 
GPS-PPP solutions can be found with the following software packages: 
* rtklib, http://www.rtklib.com/
* ESA gLab, http://gage.upc.edu/gLAB
* NRCan gpsppp

In addition to the GPS-PPP software some utilities may be required:
* Teqc, for concatenating many 1-day RINEX files into multi-day files,  https://www.unavco.org/software/data-processing/teqc/teqc.html
* RNXCMP, for decompressing Hatanaka compressed RINEX files, http://terras.gsi.go.jp/ja/crx2rnx.html

The steps for PPP-processing are roughly:

1. Download RINEX files (from e.g. BIPM or other ftp-server)
2. Optionally pre-process RINEX files (i.e. decompress Hatanaka-files, and/or assemble daily files into longer batch)
3. Download SP3 orbit and CLK clock files (from e.g. CODE or other IGS datacenter)
4. Run PPP-algorthm
5. Post-process and visualize the results

Post-processing may include:
* Calculation of double-differences for time-transfer purposes, e.g.  (StationA - IGS) - (StationB - IGS) = StationA - StationB. 
* Some UTC-laboratories submit both a RINEX file and an "LZ" file with the offset between the RINEX receiver clock and the UTC-realization. The PPP receiver-clock result should be modified using the LZ file.
* Plotting using matplotlib
* Calculation of Allan deviations or other statistics (using e.g. allantools)
* Comparison to UTC(k)-UTC numbers published by BIPM monthly in Circular-T, or to Rapid-UTC published weekly.

The scripts store input and output files under the main folder:
* 'stations' stores RINEX and LZ files from receiver stations
* 'products' stores clock, ephemeris/orbit, and ERP files from IGS datacenters
* 'common' has common files
* 'results' stores the output results of PPP processing
* 'UTC' has Circular-T data from the BIPM ftp site.
* 'UTCr' has rapid-UTC data from the BIPM ftp site.
* 'doc' has documentation
