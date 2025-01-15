# ppp-tools
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Faewallin%2Fppp-tools.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Faewallin%2Fppp-tools?ref=badge_shield)


This is a collection of python scripts for GPS-Precise Point Positioning 
post-processing of RINEX files. 
GPS-PPP solutions can be found with the following open source software packages: 
* rtklib, http://www.rtklib.com/
* ESA gLab, v5.5.1 (Jun 28 2021) http://gage.upc.edu/gLAB
* GPSPACE available from https://github.com/CGS-GIS/GPSPACE Note that this repository is 
inclomplete. A repository that includes the missing IERS2010 code is 
e.g. https://github.com/aewallin/GPSPACE

In addition to the GPS-PPP software some utilities may be required:
* GFZRNX (https://gnss.gfz-potsdam.de/services/gfzrnx) for RINEX file splice, split, repair, 
format conversion (RINEX 2 to 3). As of 2025 Janyary the version is gfzrnx-2.1.9
* RNXCMP, for decompressing Hatanaka compressed RINEX files,
http://terras.gsi.go.jp/ja/crx2rnx.html, install to e.g. /usr/local/bin and verify
that CRX2RNX is working with ```$ CRX2RNX -h```
As of 2025 January the latest version is 4.1.0.
* (__old__) Teqc, for concatenating many 1-day RINEX files into multi-day files, 
https://www.unavco.org/software/data-processing/teqc/teqc.html, install it to e.g. 
/usr/local/bin, and verify with ```$ teqc -version```
 that it is working. as of 2018 March the latest version is "2018Jan11". Teqc is no 
longer maintained, but binaries are available.

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
* Comparison to UTC-UTC(k) numbers published by BIPM monthly in Circular-T, or to Rapid-UTC published weekly.

## Folders

The scripts store input and output files under the main folder:
* 'stations' stores RINEX and LZ files from receiver stations
* 'products' stores clock, ephemeris/orbit, and ERP files from IGS datacenters
* 'common' has common files
* 'results' stores the output results of PPP processing
* 'UTC' has Circular-T data from the BIPM ftp site.
* 'UTCr' has rapid-UTC data from the BIPM ftp site.
* 'doc' has documentation
* 'temp' is used as a temporary directory for gpspace calculations

## ESA gLAB installation

* dowload package from http://gage.upc.edu/gLAB
* build binary gLAB_linux" with "make"
* test that it works ```$ ./gLAB_linux -help```
* move the binary to e.g. /usr/local/bin

## RTKLib installation

* clone from https://github.com/tomojitakasu/RTKLIB
* run "make" in RTKLIB/app/rnx2rtkp/gcc
* move the binary "rnx2rtkp" to e.g. /usr/local/bin
* test with "rnx2rtkp -help"


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Faewallin%2Fppp-tools.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Faewallin%2Fppp-tools?ref=badge_large)

