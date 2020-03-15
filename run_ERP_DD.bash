#!/usr/bin/env bash
# On RF Garcia machine, must kill the ISAE proxy before starting the program with the "killprox" command

# create storage folders for first use
mkdir ./ERP_xml
mkdir ./data_folder

# sol range to be analyzed
# I usually check the latest available sol here : https://mars.nasa.gov/insight/weather/
sol1=454
sol2=455

# Dust devils detection and ERP writing in xml format production
python ./auto_eventwindow_pressure_dd_erp.py --sol1 $sol1 --sol2 $sol2

## SENDING THE ERPs to SISMOC
## get the authentification token
## create zip file with ERP xml files and send it to the SISMOC API
## move the xml ERPs created into ERP_xml folder
./sismoc-client-post-erp.bash
