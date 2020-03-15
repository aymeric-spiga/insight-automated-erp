# insight-automated-erp
a script to submit automatic ERPs related to convective vortices

## authorship
Codes written by RF Garcia [ERP and SISMOC interface] + Aymeric Spiga [vortex detection]

## how to run
Main program is run_ERP_DD.bash
Request to the user 
- the sol range to analyze (sol1 to sol2)
- SISMOC login and password
In the end results are in ERP_xml_SOLS_453_454

## what the program does:
1-
python ./auto_eventwindow_pressure_dd_erp.py --sol1 $sol1 --sol2 $sol2
is downloading the pressure data, detecting the dust devils and creating the ERP files (*.xml)
parameters for the detection are set in the file ./auto_eventwindow_pressure_dd_erp.py (param_pres_dd.txt not used), parameters for the ERP writing inside the function write_erp_function_dd of event_detection_module.py

2-
sismoc-client-post-erp.bash
send the ERPs to SISMOC and save the ERP xml files into directory ERP_xml
parameters defined inside the file

## install notes
conda create -n erp python=2.7
conda install -c conda-forge obspy
