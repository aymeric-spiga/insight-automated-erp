# insight-automated-erp
a script to submit automatic ERPs related to convective vortices


Codes written by RF Garcia + Aymeric Spiga
Main program is run_ERP_DD.bash.
Set the sol range to analyze (sol1 to sol2) inside this program before running it.

What the program do:
1-
python ./auto_eventwindow_pressure_dd_erp.py --sol1 $sol1 --sol2 $sol2
is downloading the pressure data, detecting the dust devils and creating the ERP files (*.xml)
parameters for the detection are set in the file ./auto_eventwindow_pressure_dd_erp.py (param_pres_dd.txt not used), parameters for the ERP writing inside the function write_erp_function_dd of event_detection_module.py

2-
sismoc-client-post-erp.bash
send the ERPs to SISMOC and save the ERP xml files into directory ERP_xml
parameters defined inside the file

