#!/usr/bin/env bash
# On RF Garcia machine, must kill the ISAE proxy before starting the program with the "killprox" command

# clean the place
rm -rf sol*_DD_3.txt
rm -rf ERP_xml

# create storage folders for first use
mkdir ./ERP_xml 2> /dev/null
mkdir ./data_folder 2> /dev/null

# sol range to be analyzed
# I usually check the latest available sol here : https://mars.nasa.gov/insight/weather/
sol1=$1 #453
sol2=$2 #459

read -p "sol1 ? " rep
sol1=$rep
read -p "sol2 ? " repp
sol2=$repp

echo "LOG file: ERP_AUTOMATED_LOG_SOLS_${sol1}_${sol2}.txt"

# Dust devils detection and ERP writing in xml format production
echo "1. perform detection (please wait)"
python ./auto_eventwindow_pressure_dd_erp.py --sol1 $sol1 --sol2 $sol2 > ERP_AUTOMATED_LOG_SOLS_${sol1}_${sol2}.txt

## SENDING THE ERPs to SISMOC
## get the authentification token
## create zip file with ERP xml files and send it to the SISMOC API
## move the xml ERPs created into ERP_xml folder
echo "2. push to SISMOC (please wait)"
./sismoc-client-post-erp.bash > ERP_AUTOMATED_LOG_SOLS_${sol1}_${sol2}.txt


## save a folder with everything in it for reference or checks
mv ERP_xml ERP_xml_SOLS_${sol1}_${sol2}
mv ERP_AUTOMATED_LOG_SOLS_${sol1}_${sol2}.txt ERP_xml_SOLS_${sol1}_${sol2}/
mv sol*_DD_3.txt ERP_xml_SOLS_${sol1}_${sol2}/
