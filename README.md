# PY_NTNDA_Viewer 2020.01.06

PY_NTNDA_Viewer is Python code that is similar to the EPICS_NTNDA_Viewer that comes with areaDector.

## Status

The current version works but still has problems.

### Remaining work required

1) See the issues for some of the known problems.
2) changing region sizes to a non square image is different than EPICS_NTNDA_Viewer.
3) RGB1 works but RGB2 and RGB3 have strange behavior
4) Only blosc compression is currently implemented.


## Running the example

Note that my computer is using fedora 30, which also means python3.

### Starting simDetector

Start an IOC running the simDetector.
For example I start it as follows

    mrk> pwd
    /home/epics7/areaDetector/ADSimDetector/iocs/simDetectorIOC/iocBoot/iocSimDetector
    mrk> ./start_epics

### Start a display manager

At least the following choices are available: **medm**, **edm**, **pydm**, and **css**.
For any choice the display file, with name **simDetector**, to load is located in
**areaDetector/ADSimDetector/simDetectorApp/op**

For example to use **medm** I have the files **setEnv** and **startSimDetector**, which are:

    export PATH=$PATH:/home/epics7/extensions/bin/${EPICS_HOST_ARCH}
    export EPICS_DISPLAY_PATH=/home/epics7/areaDetector/ADCore/ADApp/op/adl
    export EPICS_DISPLAY_PATH=${EPICS_DISPLAY_PATH}:/home/epics7/areaDetector/pvaDriver/pvaDriverApp/op/adl
    export EPICS_DISPLAY_PATH=${EPICS_DISPLAY_PATH}:/home/epics7/areaDetector/ADSimDetector/simDetectorApp/op/adl
    export EPICS_CA_MAX_ARRAY_BYTES=40000000

and

    source ./setEnv
    medm  -x -macro "P=13SIM1:,R=cam1:" simDetector.adl 

then I just enter

    ./startSimDetector



### start PY_NTNDA_Viewer

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

## Required python modules

You must have python and pip installed.
I am using ferora core 30 and it has python3 and pip3 installed.

The other python modules can be installed via **pip install ...**

For example I can issue the command

    sudo pip install numpy

The following shows all installed python modules

    pip list

The following is a list of modules required by PY_NTNDA_Viewer

1) numpy
2) PyQt5
3) PyQt5-sip
4) QtPy
5) pvapy
6) pyqtgraph
7) blosc

But when Mark Rivers tried PY_NTNDA_Viewer, he found other problems with his python setup.
He did resolve his problems and got it to work.

## Other things to try

### pixel data types

In the display manager **simDetector** window try the various **Data type**s.
The default is **Uint8**.

Now select **Int8**.
This works just like **Uint8**.

Now select **Int16** and also set **Gain** to 255.
This works. **UInt16** also works.

I think that **Int32**, **UInt32**, **Int64**, **UInt64**, and **Float32** also work.
But is is not easy to test.

I think that python does not support **Float64**, but not sure that this is true.


### color mode

Set **Data type** to either **Int8** or **Uint8**.

Then set **Color mode** to **RGB1**.
This works.

**RGB2** and **RGB3** have behavior that looks wrong.
Needs further investigation.

### codec

Set **Data type** to either **Int8** or **Uint8** and
**Color mode** to **Mono** or **RGB1**

Then select plugins All.
On the new window set the Port for PVA1 to **CODEC1**.
Then on the line for CODEC1 click on **More**.
In the new window set Enable to **Enable**.

You should see what you saw before.

Next select Compressor **Blosc**.
You should see what you did before,
except that on the PY_NTNDA_Viewer window you will see that the compressed size is much less
than the uncompressed size.


### Performance

I set acquire period to .001 (it was initially .005)
EPICS_NTDA_Viewer could only do about 140 frames/second
PY_NTDA_Viewer does about 330 frames/second.

Mark Rivers reports diffenent results.

