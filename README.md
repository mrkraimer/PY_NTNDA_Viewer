# PY_NTNDA_Viewer 2020.02.03

PY_NTNDA_Viewer is Python code that is similar to the EPICS_NTNDA_Viewer that comes with areaDector.

## Status

This is almost ready for prime time.

There are currently 2 versions:

1) PY_NTNDA_Viewer.py 
This uses p4p and crashes when simDetector is started in continous mode.
2) PVAPY_NTNDA_Viewer.py
This uses pvapy.
It seems to does not crash when simDetector is started in continous mode.
But pvapy is not available on windows.

Both are quite similar.
Note that class ImageDisplay does not access anything from class PY_NTNDA_Viewer.
And other than calling ImageDisplay.newImage no code accesses anythink from other threads.

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



### start P4P_NTNDA_Viewer or PVAPY_NTNDA_Viewer

In order to use the codec support from **areaDetector** you must have
a path to **areaDetector/ADSupport/lib...** defined.
The details differ between windows and linux or macos.

An example is **exampleStartP4P**, which uses **p4p** for communication with the simDetector.

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/epics7/areaDetector/ADSupport/lib/linux-x86_64
    python P4P_NTNDA_Viewer.py 13SIM1:Pva1:Image


I start it via

    mrk> pwd
    /home/epics7/modules/PY_NTNDA_Viewer
    mrk> ./exampleStartP4P

You will see errors if You have not installed all the python packages required.
If it shows no errors click connect and start.

Then run whatever opi tool you use to control the simDetector.
Then select plugins All and enable the PVA1 plugin.
Then click connect and then start.

You should see images being displayed.

**exampleStartPVAPY** starts **PVAPY_NTNDA_Viewer.py**, which uses **pvapy** for communication with the simDetector.

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
5) p4p or pvapy
6) pyqtgraph


## Other things to try

### pixel data types

In the display manager **simDetector** window try the various **Data type**s.
The default is **Uint8**.

Now select **Int8**.
This works just like **Uint8**.

Now select **Int16** and also set **Gain** to 255.
This works. **UInt16** also works.

I think that **Int32**, **UInt32**, **Int64**, **UInt64**, **Float32**, and **Float64** also work.
But is is not easy to test.


### color mode

Set **Data type** to either **Int8** or **Uint8**.

Then set **Color mode** to **Mono** or **RGB1** or **RGB2** or **RGB3** 
These should all work.

### codec

Set **Data type** to either **Int8** or **Uint8** and **Color mode** to any type

Then select plugins All.
On the new window set the Port for PVA1 to **CODEC1**.
Then on the line for CODEC1 click on **More**.
In the new window set Enable to **Enable**.

You should see what you saw before.

Next select Compressor.
You should see what you did before,
except that on the PY_NTNDA_Viewer window you will see that the compressed size is much less
than the uncompressed size.


### Performance

For a 1024x1024 image:

1) NDPVa generates 196 frames/sec
2) EPICS_NTDA_Viewer handles 140 frames/second
3) NTDA_Viewer only does about 20 frames/second.

For a 512cx512 image:

1) NDPVa generates 196 frames/sec
2) EPICS_NTDA_Viewer handles 193 frames/second
3) NTDA_Viewer does about 135 frames/second.


I did some searching on-line and saw:

'''
The ImageView class can also be instantiated directly and embedded in Qt applications.
Instances of ImageItem can be used inside a ViewBox or GraphicsView.
For higher performance, use RawImageWidget.
Any of these classes are acceptable for displaying video by calling setImage() to display a new frame. To increase performance, the image processing system uses scipy.weave to produce compiled libraries. If your computer has a compiler available, weave will automatically attempt to build the libraries it needs on demand. If this fails, then the slower pure-python methods will be used instead.
'''

But for python3, **weave** is no longer supported 


