# PY_NTNDA_Viewer 2020.01.03


PY_NTNDA_Viewer is Python code that is similar to the EPICS_NTNDA_Viewer that comes with areaDector.
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
Then click connect and then start.

You should see images being displayed.
You can also change the region sizes and select the Color mode and Data type

## Remaining work required


1) changing region sizes to non square image is different than EPICS_NTNDA_Viewer.
I think that EPICS_NTNDA_Viewer works properly.
2) RGB1 works but RGB2 and RGB3 have strange behavior
3) Only blosc compression is currently implemented.


## Additional Features Desired

Implement additions features supported by EPICS_NTNDA_Viewer

Amoung these are

1) all pixel data types, except float64, appear to work correectly.
Note that EPICS_NTNDA_Viewer does not appear to work correctly
2) Currrently only blosc compression is implemented.

### Performance

I set acquire period to .001 (it was initially .005)
EPICS_NTDA_Viewer could only do about 140 frames/second
PY_NTDA_Viewer does about 330 frames/second.

EPICS_NTNDA_Viewer uses MORE CPU then PY_NTNDA_Viewer.
