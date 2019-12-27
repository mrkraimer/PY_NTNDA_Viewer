# PY_NTNDA_Viewer 2019.12.27


PY_NTNDA_Viewer is Python code that is similar to the EPICS_NTNDA_Viewer that comes with areaDector.
What is currently implemented is a working version but stll needs more features
A later section briefy explains currently planned extensions.

## Running the example

Note that my computer is using fedora 30, which also means python3.

Start an IOC running the simDetector.
For example I start it as follows

    mrk> pwd
    /home/epics7/areaDetector/ADSimDetector/iocs/simDetectorIOC/iocBoot/iocSimDetector
    mrk> ./start_epics

Then start the viewer.
For example I start it via

    mrk> pwd
    /home/epics7/modules/PY_NTNDA_Viewer
    mrk> python PY_NTNDA_Viewer.py 13SIM1:Pva1:Image

You will see errors if You have not installed all the python packages required.
If it shows no errors click connect and start.

Then run whatever opi tool you use to control the simDetector.
Then select plugins All and enable the PVA1 plugin.
Then click start.

You should see images being displayed.
You can also change the region sizes and select the color mode.

## Remaining work required


1) changing region sizes to non square image can lead to weird behavior
2) RGB1 works but RGB2 and RGB3 have strange behavior


## Additional Features Desired

Implement additions features supported by EPICS_NTNDA_Viewer

Amoung these are

1) Add support for other Data Types, currently only uint8 and int8 work.
2) Add support for compression

### Performance

I set acquire period to .001 (it was initially .005)
EPICS_NTDA_Viewer could only do about 140 frames/second
PY_NTDA_Viewer does about 330 frames/second.

EPICS_NTNDA_Viewer uses MORE CPU then PY_NTNDA_Viewer.
