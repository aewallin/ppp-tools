# ppp-tools

Progress:
2015-06-01: simple gLAB run works
2015-05-25: initial commits, nothing works yet.


This is a collection of python scripts for GPS-Precise Point Positioning post-processing of RINEX files based on open-source tools. I know of two open-source packages that can perform PPP calculations: rtklib and ESA gLab. Eventually both could be supported.

The steps for PPP-processing are roughly:

1. Download RINEX files (from e.g. BIPM or other ftp-server)
2. Download SP3 orbit and CLK clock files (from e.g. CODE or other IGS datacenter)
3. Run PPP-algorthm (this is a call to either rktpost or gLab)
4. Post-process and visualize the results

Step 4 may include:
* For time-transfer purposes one further wants to calculate double-differences, e.g.  (StationA - IGS) - (StationB - IGS) = StationA - StationB. 
* Some UTC-laboratories (e.g. OP) submit both a RINEX file and an "LZ" file with the offset between the RINEX receiver clock and the UTC-realization. The PPP receiver-clock result should be modified using the LZ file.
* Plotting using matplotlib
* Calculation of Allan deviations or other statistics (using e.g. allantools)
* Comparison to UTC(k)-UTC numbers published by BIPM monthly in Circular-T, or to Rapid-UTC published daily.

The scripts store input and output files under the main folder:
* 'stations' stores RINEX and LZ files for receiver stations
* 'products' stores clock, ephemeris/orbit, and ERP files from IGS datacenters
* 'common' has common files
* 'results' stores the output results of PPP processing
