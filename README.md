# PY_NTNDA_Viewer

PY_NTNDA_Viewer is Python code that is similar to the EPICS_NTNDA_VIEWER that comes with areaDector.
What is currently implemented is only a proof of concept.
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

Then run whatever opi tool you use to control the simDetector.
Then select all plugins and enable the PVA1 plugin.
Then click start.

You should see images being displayed.
You can also change the region sizes and select the color mode.

## Remaining work required

### race codition must be fixed

There are a couple of sleep statements that are used to prevent PY_NTNDA_Viewer from crashing.
It still crashes if lots of other activity is occuring.
This must be fixed.

### Additional Featured Desired

Implement additions features supported by EPICS_NTNDA_Viewer

Amoung these are

1) Add support for other Data Types
2) Allow monitoring to be started and stopped.
3) Allow the channelName to be changed.
4) Add support for compression

### Performance

Using the image with no changes to color or size I see 120-130 images per second.
With EPICS_NTNDA_Viewer I see 130-140 images per second.
BUT EPICS_NTNDA_Viewer uses more CPU then PY_NTNDA_Viewer.
